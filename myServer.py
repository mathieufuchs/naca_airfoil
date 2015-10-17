from flask import Flask, render_template, send_file
from flask import request, redirect
from tasks import computeResults
from celery import Celery, group
import os
import subprocess
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot
import numpy as np
from cStringIO import StringIO

app = Flask(__name__)

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

def plot(image, x, y, z, c):
	a = pyplot.figure()
	a.suptitle("Lift and Drag forces over time", fontsize=16)
	ax1 = a.add_subplot(211)
	ax1.set_title("Lift Force")
	ax1.plot(x, y, c)
	ax2 = a.add_subplot(212)
	ax2.set_title("Drag Force")
	ax2.plot(x, z, c)
	a.savefig(image, format='png')

params = {'angle_start':0, 'angle_stop':30, 
'n_angles':10, 'n_nodes':200, 'n_levels':3}

airfoil_params = {'num_samples':10, 'visc':0.0001, 'speed':10, 'T':1}

status="PENDING"
results="Not ready yet... Reload the page!"

show = 0

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
	angList = distributeJob(num(params['angle_start']), num(params['angle_stop']), num(params['n_angles']))
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
		names = os.listdir(os.path.join(app.static_folder))
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
		status="Click RUN", results="", images = names)
	
	if task.ready() == False:
		global show 
		show = 0
		print "not ready"
		names = os.listdir(os.path.join(app.static_folder))
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
		status="PENDING", results="...computing...", images=names)
	else:
		global show
		print "Task Done"
		status = "DONE"
		if show == 0:
			objects = task.get()
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
				
				pic_name = "air"+task_name + ".png"
				image = open("static/"+pic_name,'w')
				plot(image, d, a, b, 'r--')
				image.close
			
				#LD = "Best L/D ratio: %f"  %(np.max(c))
		
				results = "Click on the buttons to change pictures"
			
				show = 1
				print "got results"
		
		names = os.listdir(os.path.join(app.static_folder))
		global results
		global status
		return render_template('params.html', params=params, airfoil_params=airfoil_params,
		status=status, results=results, images=names)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
	
	
	
    