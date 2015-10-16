from flask import Flask
from flask import render_template
from flask import request, redirect
from tasks import computeResults
from celery import Celery, group
import subprocess

app = Flask(__name__)

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
    job = group(computeResults.s(params, airfoil_params))
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
    try:
        if task.ready() == False:
            return render_template('params.html', params=params, airfoil_params=airfoil_params,
            status=status, results=results)
        else:
            print "in app"
            status = "DONE"
            toReturn = task.get()
            results = toReturn
            print "got results"
            return render_template('params.html', params=params, airfoil_params=airfoil_params,
            status=status, results=results)
    except:
        return render_template('params.html', params=params, airfoil_params=airfoil_params,
            status="PENDING", results="Not ready")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
    
    
    