from celery import Celery
import os
import glob
import json
import time
import urllib2
import subprocess
from dolfin_convert import gmsh2xml 
app = Celery('tasks', backend='amqp', broker='amqp://ma:fu@130.238.29.150:5672/mafu')


def convertToXML():
	meshes = glob.glob("msh/*.msh")
	for fn in meshes:
		gmsh2xml(fn, fn[:-3] + "xml")
		subprocess.check_call(name, shell=True)

def runAirfoil(d):
	xmlFiles = glob.glob("msh/*.xml")
	for fn in xmlFiles:
		print "Starting airfoil"
		name = "./navier_stokes_solver/airfoil %s %s %s %s %s > file.log" %(d['num_samples'], d['visc'], d['speed'], d['T'], fn)
		subprocess.check_call(name, shell=True)
		print "Finnished airfoil"

@app.task()
def computeResults(d, airfoil_params, i):
	#subprocess.check_call("sudo chown -R ubuntu /home/ubuntu/naca_airfoil > file.log")
	subprocess.check_call("rm msh/*", shell=True)
	subprocess.check_call("rm geo/*", shell=True)
	toRun = './run.sh %s %s %s %s %s' %(i, i, 1, d['n_nodes'], d['n_levels'])
	print "Running: " + toRun
	subprocess.check_call(toRun, shell = True)
	print "Finnished running"
	convertToXML()

	runAirfoil(airfoil_params)
	toReturn = open("results/drag_ligt.m", 'r').read()
	print toReturn
	return toReturn, "_a"+str(i) +"_n"+str(d['n_nodes'])

