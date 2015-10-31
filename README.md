Files:
readme.txt: this file, instructions
run.sh: bash script generating .msh files
naca2gmsh_geo.py: python script generating .geo files
geo: directory where geo files are stored
msh: directory where msh files are stored
dolfin_convert.py: python script used to convert .msh to .xml
initWorker.py: python script used to handle instances (initiation and termination)
Manage_Container.py: python script used to manage an openstack container (Put and Get files)
myServer.py: OLD server handling airfoil
newMyServer.py: script to use to run the final server
tasks.py: the tasks the celery worker has to do
static: directory where the pngs are stored for each session
templates: directory where the .html files are stored. 
userdata2.yml: user_data file used to contextualize the new workers (starts celery and gives the ip of the broker, for example)

Note:
newMyServer.py: starts the flask app that listens on port 5000
tasks.py: computes the simulations as a celery task
templates/index.html is the main page of the website accessible from xx.xx.xx.xx:5000/ where xx.xx.xx.xx is the ip of your machine.