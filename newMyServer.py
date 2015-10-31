from flask import Flask, render_template, send_file
from flask import request, redirect
from tasks import computeResults
from initWorker import init, kill
from Manage_Container import put_file, get_file
from celery import Celery, group
import os
import requests
import subprocess
import matplotlib 
matplotlib.use('Agg')
from matplotlib import pyplot
import numpy as np
from cStringIO import StringIO
import pickledb
import thread

app = Flask(__name__)

# this function handles the creation and delition of workers. 
# It optimizes the need for workers depending on 
# how much angles (n) the user is demanding to do the simulations on.  
def distribute_work(n):
	global n_workers
	max_angles = 6
	if n_workers == 0:
		if ((n/max_angles)+1) >= 8:
			n_workers = init(n_workers, 8)
		else:
			n_workers = init(n_workers, (n/max_angles)+1)
	elif n_workers > ((n/max_angles)+1):
		n_workers = kill((n/max_angles)+1, n_workers)
	else:
		if ((n/max_angles)+1) >= 8:
			n_workers = init(n_workers, 8)
		else:
			n_workers = init(n_workers, (n/max_angles)+1)

#small function used to translate a string (s) to a num or float.
def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

# translation of the first loop of run.sh which creates a list of angles
# n is the number of angles between start and stop
# returns the list of angles
def distributeJob(start, stop, n):
    angle = []
    diff=((stop-start)/n)
    for i in range(0, n+1):
        angle.append(start + diff*i)
    return angle

#plots both lift and drag with time as two subplots 
#saves the plots to a .png
def plot(image, x, y1, y2, c):
	a = pyplot.figure()
	a.suptitle("Lift and Drag forces over time", fontsize=16)
	ax1 = a.add_subplot(211)
	ax1.set_title("Lift Force")
	ax1.plot(x, y1, c)
	ax2 = a.add_subplot(212)
	ax2.set_title("Drag Force")
	ax2.plot(x, y2, c)
	a.savefig(image, format='png')

params = {'angle_start':2, 'angle_stop':4, 'n_angles':1, 'n_nodes':10, 'n_levels':1} #dictionnary of the gmsh params

airfoil_params = {'num_samples':10, 'visc':0.001, 'speed':10, 'T':0.1} #dictionnary of the airfoil params 

show = 0 #global variable to handle the website

get_file('plots.db','plots.db')  #downloads the database from the container

db = pickledb.load('plots.db', False)	#loads it as the current database to use

n_workers = 0 #global variable used to keep track on how much worker you use

@app.route('/')
#returns the main page index.html
def index():
    return render_template('index.html')
    
@app.route('/signup', methods = ['POST'])
#handles the mesh parameters submission 
#returns index.html
def signup():
	for i in params.keys():
		params[i]  = request.form[i]

	return redirect('/')
	
@app.route('/signup2', methods = ['POST'])
#handles the airfoil parameters submission
#return index.html
def signup2():
	for i in airfoil_params.keys():
		airfoil_params[i] = request.form[i]
		
	return redirect('/')

@app.route('/run', methods = ['POST'])
#Parses the database, creates workers, initates the simulations. 
#redirects to params.html
def run():		
	print "first"
	if not (0<= num(params["n_levels"]) <= 3) :
		params["n_levels"] = "0"
	
	params["n_levels"] = "0"
	if not(1<= num(params['n_nodes']) <=200):
		params['n_nodes']= "10"

	db.load('plots.db',False)
	angList = distributeJob(num(params['angle_start']), num(params['angle_stop']), num(params['n_angles']))
	names = db.getall()

	#removes the angles and nodes that already have been computed 
	angList = [a for a in angList if "air_a"+str(a)+"_n"+str(params['n_nodes'])+".png" not in names]
				
	#no need to start new computations if it has been done
	if(len(angList) == 0):		
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
	status="This simulation has already been done", results="Click on the wanted plot to display it", images = names)
	 
	#start new workers if needed
	distribute_work(len(angList))

	#creates a group of tasks 
	job = group(computeResults.s(params, airfoil_params, i) for i in angList)
	global task 

	#distributes the job
	task= job.apply_async()
	
	print "Celery is working..."
	
	return redirect('/params')

@app.route('/showParams', methods = ['POST'])
#returns the parameter page
def show_params():		
	return redirect('/params')
	
@app.route('/params')
#handles the output. 
#checks if the computations are ready, handles the results, creates pngs...
#redirects to params.html with the right status message shown to the user. 
def show_results():
	try:
		task.ready()
	except:
		db.load('plots.db',False)
		names = db.getall()
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
		status="Click RUN", results="", images = names)
	
	if task.ready() == False:
		global show 
		show = 0
		print "not ready"
		db.load('plots.db',False)
		names = db.getall()
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
		status="PENDING", results="...computing...", images=names)
	else:
		global show
		print "Task Done"
		if show == 0:
			try:
				objects = task.get()
			except:
				db.load('plots.db',False)
				names = db.getall()
				return render_template('params.html', params=params, airfoil_params=airfoil_params,
                status="FAILED", results="Something went wrong, return to index and try again...", images=names)

			for o in objects:
				obj = o[0]                  
				task_name=o[1]						#taskname
				tmp = obj.split()					#drag_ligt.m
				del tmp[:4]							#removes "%", "time", "lift", "drag" 
				l1=tmp[::3]							#time list
				l2=tmp[1::3]						#lift list
				l3=tmp[2::3]						#drag list
				l=np.array(l2, dtype=np.float) 		#lift array
				d=np.array(l3, dtype=np.float)		#drag array
				t=np.array(l1, dtype=np.float)		#time array
				
				pic_name = "air"+task_name + ".png" 
				pic_path = "static/" + pic_name
				db.set(pic_name, pic_path)			#uploads the results to the db
				
				#plot and save it as png
				with open(pic_path,'w') as image:
					plot(image, t, l, d, 'b')		
				
				db.dump()							#saves the db

				put_file('plots.db', 'plots.db')	#uploads the db to the container
				
				#uploads the files as a python thread for not blocking the webapplication
				thread.start_new_thread( put_file, (pic_name, pic_path, ) )
			
				show = 1
				print "got results"
		
		names = db.getall()
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
		status="DONE", results="Click on the buttons to change pictures", images=names)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
	
	
	
    
