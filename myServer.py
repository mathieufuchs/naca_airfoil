from flask import Flask
from flask import render_template
from flask import request, redirect
import subprocess

app = Flask(__name__)

params = {'angle_start':0, 'angle_stop':30, 
'n_angles':10, 'n_nodes':200, 'n_levels':3}

#angle_start=0
#angle_stop=30
#n_angles=10
#n_nodes=200
#n_levels=3

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
    
@app.route('/signup', methods = ['POST'])
def signup():
    toRun = './run.sh'
    for i in params.keys():
        params[i]  = request.form[i]
        toRun = toRun + ' ' + params[i]
    subprocess.call(toRun, shell = True)
    print toRun
    return redirect('/')
#angle_start = request.form['angle_start']
    #angle_stop = request.form['angle_stop']
    #n_angles = request.form['n_angles']
    #n_nodes= request.form['n_nodes']
    #n_levels = request.form['n_levels']    

@app.route('/params')
def emails():
    return render_template('params.html', params=params)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
    
    