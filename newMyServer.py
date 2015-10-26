from flask import Flask, render_template, send_file
from flask import request, redirect
from tasks import computeResults
from initWorker import init
from celery import Celery, group
import os
import subprocess
import matplotlib 
matplotlib.use('Agg')

from matplotlib import pyplot
import numpy as np
from cStringIO import StringIO
import pickledb

app = Flask(__name__)

def distribute_work(num_of_angles):
	max_angles = 5
	init((n/max_angles)+1)

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def distributeJob(start, stop, n):
    angle = []
    diff=((stop-start)/n)
    for i in range(0, n+1):
        angle.append(start + diff*i)
    return angle

def plot(image, x, y, z, c, i):
	a = pyplot.figure()
	a.suptitle("Lift and Drag forces over time", fontsize=16)
	ax1 = a.add_subplot(211)
	ax1.set_title("Lift Force")
	ax1.plot(x, y, c)
	ax2 = a.add_subplot(212)
	ax2.set_title("Drag Force")
	ax2.plot(x, z, c)
	a.savefig(image, format='png')

params = {'angle_start':2, 'angle_stop':4, 
'n_angles':1, 'n_nodes':10, 'n_levels':1}

airfoil_params = {'num_samples':10, 'visc':0.001, 'speed':10, 'T':0.1}

status="PENDING"
results="Not ready yet... Reload the page!"

show = 0

db = pickledb.load('plots.db', False)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
    
@app.route('/signup', methods = ['POST'])
def signup():
	for i in params.keys():
		params[i]  = request.form[i]
	
	return redirect('/')
	
@app.route('/signup2', methods = ['POST'])
def signup2():
	for i in airfoil_params.keys():
		airfoil_params[i] = request.form[i]
		
	return redirect('/')

@app.route('/run', methods = ['POST'])
def run():		
	print "first"
	if not (0<= num(params["n_levels"]) <= 3) :
		params["n_levels"] = "1"
	
	params["n_levels"] = "0"
	if not(1<= num(params['n_nodes']) <=200):
		params['n_nodes']= "10"
	
	if (num(params['angle_stop']) - num(params['angle_start']) >= num(params['n_angles']) ):
		params['n_angles'] = str((num(params['angle_stop']) - num(params['angle_start']))/2)
	
	#start new workers
	distribute_work(num(params['n_angles']))

	db.load('plots.db',False)
	angList = distributeJob(num(params['angle_start']), num(params['angle_stop']), num(params['n_angles']))
	names = db.getall()
	#names = os.listdir(os.path.join(app.static_folder))
	for i in angList:
		nameInputed = "_a"+str(i) +"_n"+str(params['n_nodes'])
		nameToCheck = "air"+ nameInputed + ".png"
		for j in names:
			if j == nameToCheck:
				angList.remove(i)
				
	if(len(angList) == 0):		
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
	status="This simulation has already been done", results="Click on the wanted plot to display it", images = names)
	 

	job = group(computeResults.s(params, airfoil_params, i) for i in angList)
	print job
	global task 
	task= job.apply_async()
	
	print "Celery is working..."
	
	return redirect('/params')

@app.route('/showParams', methods = ['POST'])
def showParams():		
	return redirect('/params')
	
@app.route('/params')
def emails():
	try:
		task.ready()
	except:
		db.load('plots.db',False)
		names = db.getall()
		#names = os.listdir(os.path.join(app.static_folder))
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
		status="Click RUN", results="", images = names)
	
	if task.ready() == False:
		global show 
		show = 0
		print "not ready"
		db.load('plots.db',False)
		names = db.getall()
		#names = os.listdir(os.path.join(app.static_folder))
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
		status="PENDING", results="...computing...", images=names)
	else:
		global show
		print "Task Done"
		status = "DONE"
		if show == 0:
			try:
				objects = task.get()
			except:
				names = db.getall()
				#names = os.listdir(os.path.join(app.static_folder))
				return render_template('params.html', params=params, airfoil_params=airfoil_params,
                status="FAILED", results="Something went wrong, return to index and try again...", images=names)
			for o in objects:
				print o
				obj = o[0]
				task_name=o[1]
				print task_name
				tmp = obj.split()
				tmp.pop(0)
				print "...1"
				l1 = tmp[::3]
				l2=tmp[1::3]
				l3=tmp[2::3]
				print l1.pop(0) #+ str(l1.pop(0))
				print l2.pop(0) #+ str(l2.pop(0))
				print l3.pop(0) #+ str(l3.pop(0))
				a=np.array(l2, dtype=np.float)
				b=np.array(l3, dtype=np.float)
				c = a/b
				d= np.array(l1, dtype = np.float)
				e = np.max(c)
				Nindex = nonzero(t == e)[0][0]
				
				
				pic_name = "air"+task_name + ".png"
				pic_path = "static/" + pic_name
				db.set(pic_name, pic_path)
				
				image = open(pic_path,'w')
				plot(image, d, a, b, 'b', Nindex)
				image.close
				
				db.dump()
				#LD = "Best L/D ratio: %f"  %(np.max(c))
		
				results = "Click on the buttons to change pictures"
			
				show = 1
				print "got results"
		
		#names = os.listdir(os.path.join(app.static_folder))
		names = db.getall()
		global results
		global status
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
		status=status, results=results, images=names)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
	
	
	
    