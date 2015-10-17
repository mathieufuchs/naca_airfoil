from flask import Flask, render_template, send_file
from flask import request, redirect
from tasks import computeResults
from celery import Celery, group
import subprocess
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot
import numpy as np
from cStringIO import StringIO

app = Flask(__name__)


def distributeJob(start, stop, n):
    angle = []
    diff=((stop-start)/n)
    for i in range(0, n+1):
        angle.append(start + diff*i)
    return angle

def plot(image, file):
    x = numpy.linspace(0, 10)
    y = numpy.sin(x)
    pyplot.plot(x, y)
    pyplot.savefig(image, format='png')

params = {'angle_start':0, 'angle_stop':30, 
'n_angles':10, 'n_nodes':200, 'n_levels':3}

airfoil_params = {'num_samples':10, 'visc':0.0001, 'speed':10, 'T':1}

status="PENDING"
results="Not ready yet... Reload the page!"

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
    angList = distributeJob(params['angle_start'], params['angle_stop'], params['n_angles'])
    job = group(computeResults.s(params, airfoil_params, i) for i in angList)
    print job
    global task 
    task= job.apply_async()
    
    print "Celery is working..."
    
    return redirect('/params')

@app.route('/showParams', methods = ['POST'])
def show():     
    return redirect('/params')
    
@app.route('/params')
def emails():
    if task.ready() == False:
        print "not ready"
        return render_template('params.html', params=params, airfoil_params=airfoil_params,
        status="bla", results="bla")
    else:
        print "Task Done"
        status = "DONE"
        obj = task.get()
        #print obj
        tmp = obj[0].split()
        
        print "...1"
        l1 = tmp[::3]
        l2=tmp[1::3]
        l3=tmp[2::3]
        print l1.pop(0)
        print l2.pop(0)
        print l3.pop(0)
        a=np.array(l2, dtype=np.float)
        b=np.array(l3, dtype=np.float)
        c = a/b
        
        
        LD = "Best L/D ratio: %f"  %(np.max(c))
        
        
        results = LD
        print "got results"
        return render_template('params.html', params=params, airfoil_params=airfoil_params,
        status=status, results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
    
    
    