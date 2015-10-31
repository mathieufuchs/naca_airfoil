* ###__Files__:
  * __readme.txt__: this file, instructions
  * __run.sh__: bash script generating .msh files
  * __naca2gmsh_geo.py__: python script generating .geo files
  * __geo__: directory where geo files are stored
  * __msh__: directory where msh files are stored
  * __dolfin_convert.py__: python script used to convert .msh to .xml
  * __initWorker.py__: python script used to handle instances (initiation and termination)
  * __Manage_Container.py__: python script used to manage an openstack container (Put and Get files)
  * __myServer.py__: OLD server handling airfoil
  * __newMyServer.py__: script to use to run the final server
  * __tasks.py__: the tasks the celery worker has to do
  * __static__: directory where the pngs are stored for each session
  * __templates__: directory where the .html files are stored. 
  * __userdata2.yml__: user_data file used to contextualize the new workers (starts celery and gives the ip of the broker, for example)

* ###__Note__:
  * __newMyServer.py__: starts the flask app that listens on port 5000
  * __tasks.py__: computes the simulations as a celery task
  * __templates/index.html__: main page of the website accessible from xx.xx.xx.xx:5000/ where xx.xx.xx.xx is the ip of your machine.
