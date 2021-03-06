#!/usr/bin/env python
import os
import xml.etree.ElementTree as xml
import paths
import optparse as op

def parseXML(fileName):
  '''Parses the SPHERLS.xml file to figure out settings for submit script and how to run SPHERLS
  returns settings, a dictionary with entries for:
  
  numProcs    = an integer number of process to submit the job with
  jobName     = a string containing the name of the job
  jobDuration = a string containg the duration of the job
  totalview   = logical containing either True if running with totalview debugging other wise False
  que         = a string that is either "test" for the test que or "main" for the main que, if the
                string is None, then run on the command line and don't submit to a que
  email       = set to the email to email when job is completed, if False or not given no email will
                be sent.
  '''
  
  #get root element of fileName
  settings={}
  tree=xml.parse(fileName)
  root=tree.getroot()
  
  #get job element
  jobElement=root.find("job")
  if jobElement==None:
    print "No \"job\" element found under \"data\" node in file \""+fileName+"\", quiting!"
    quit()
  
  #get procDims element
  procDimsElement=root.find("procDims")
  if procDimsElement==None:
    print "No \"procDims\" element found under \"data\" node in file \""+fileName+"\", quiting!"
    quit()
  
  #get x0 element
  x0Element=procDimsElement.find("x0")
  if x0Element==None:
    print "No \"x0\" element found under \"procDims\" node in file \""+fileName+"\", quiting!"
    quit()
  try:
    x0=int(x0Element.text)
  except ValueERror:
    print "\"x0\" element found under \"procDims\" node in file \""+fileName+"\" is not an integer, quiting!"
    quit()
  
  #get x1 element
  x1Element=procDimsElement.find("x1")
  if x1Element==None:
    print "No \"x1\" element found under \"procDims\" node in file \""+fileName+"\", quiting!"
    quit()
  try:
    x1=int(x1Element.text)
  except ValueERror:
    print "\"x1\" element found under \"procDims\" node in file \""+fileName+"\" is not an integer, quiting!"
    quit()
  
  #get x2 element
  x2Element=procDimsElement.find("x2")
  if x2Element==None:
    print "No \"x2\" element found under \"procDims\" node in file \""+fileName+"\", quiting!"
    quit()
  try:
    x2=int(x2Element.text)
  except ValueERror:
    print "\"x2\" element found under \"procDims\" node in file \""+fileName+"\" is not an integer, quiting!"
    quit()
  settings['numProcs']=str(x0*x1*x2)
  
  #get job que element
  jobQueElement=jobElement.find("que")
  settings['que']=None
  if jobQueElement==None:
    settings['que']=None
  elif jobQueElement.text.lower() in ("test","te","tq"):
    settings['que']="test"
  elif jobQueElement.text.lower() in ("m","main","","yes","true","tr"):
    settings['que']="main"
  
  #if we have a que, get job details for the que
  if settings['que'] in ("test","main"):
  
    #get job name element
    jobNameElement=jobElement.find("name")
    if jobNameElement==None:
      print "No \"name\" element found under \"job\" node in file \""+fileName+"\", stopping!"
      quit()
    settings['jobName']=jobNameElement.text
    
    #get job duration element
    jobDurationElement=jobElement.find("duration")
    if jobDurationElement==None:
      print "No \"duration\" element found under \"job\" node in file \""+fileName+"\", quiting!"
      quit()
    settings['jobDuration']=jobDurationElement.text
    
    #get job email
    jobEmailElement=jobElement.find("email")
    settings['email']=None
    if jobEmailElement==None:
      settings['email']=None
    elif jobEmailElement.text.lower() in ("false","no","f",""):
      settings['email']=None
    else :
      settings['email']=jobEmailElement.text
    
    #get job memory
    jobMemoryElement=jobElement.find("memory")
    settings['virtualMemory']=None
    settings['stackMemory']=None
    if jobMemoryElement==None:
      settings['virtualMemory']=None
      settings['stackMemory']=None
    else :
      settings['email']=jobMemoryElement.text
      settings['virtualMemory']=jobMemoryElement.text
      settings['stackMemory']=jobMemoryElement.text
    
    #get parallel environment
    jobPEElement=jobElement.find("parallel-environment")
    settings['parrallelEnvironment']="openmpi"#this is for lachesis
    if not jobPEElement==None:
      settings['parrallelEnvironment']=jobPEElement.text
  
  #check if wanting to run in totalview
  jobTotalviewElement=jobElement.find("totalview")
  settings['totalview']=False
  if jobTotalviewElement==None:
    settings['totalview']=False
  elif jobTotalviewElement.text.lower() in ("t","true","y","yes","tr","tru","ye","on"):
    settings['totalview']=True
  
  if settings['totalview']==True and settings['que'] in ("test","main"):#cannot run in a que with totalview
    print "WARNING: Cannont run in a que with totalview, que settings ignored!"
    settings['que']=None
  
  return settings
def makeSubScript(settings):
  '''
  Creates a submit script for the sun grid engine based on settings, and returns the name of the 
  script. If no que was specified it returns None.
  '''
  #additional hard coded settings
  scriptName=""
  if settings['que']==None or settings['totalview']==True:
    return None
  elif settings['que']=="test":
    scriptName=settings['jobName']+"_testque.sh"
  elif settings['que']=="main":
    scriptName=settings['jobName']+"_que.sh"
  f=open(scriptName,'wb')
  script="#!"+settings['shell']+"\n"\
    +"##\n"\
    +"##Shell to run job in\n"\
    +"#$ -S "+settings['shell']+"\n"\
    +"##\n"\
    +"## Set job name\n"\
    +"#$ -N "+settings['jobName']+"\n"\
    +"##\n"\
    +"## Run job from current working directory\n"\
    +"#$ -cwd\n"\
    +"##\n"\
    +"## Output file name\n"\
    +"#$ -o "+settings['outputFile']+"\n"\
    +"##\n"\
    +"## Error file name\n"\
    +"#$ -e "+settings['errorFile']+"\n"\
    +"##\n"\
    +"## Error is not merged with standard out\n"\
    +"#$ -j n\n"\
    +"##\n"\
    +"## Number of processors\n"\
    +"#$ -pe "+settings['parrallelEnvironment']+" "+settings['numProcs']+"\n"\
    +"##\n"\
    +"## Run time\n"\
    +"#$ -l h_rt="+settings['jobDuration']+"\n"\
    +"##\n"\
    +"## Amount of virtual memory\n"
  if settings['virtualMemory']!=None:
    script=script+"#$ -l h_vmem="+settings['virtualMemory']+"\n"
  script=script+"##\n"\
    +"## Amount of stack memory\n"
  if settings['stackMemory']!=None:
    script=script+"#$ -l h_stack="+settings['stackMemory']+"\n"
  script=script+"##\n"\
    +"## Transfer all environment variables when job is submitted\n"\
    +"#$ -V\n"
  if settings['que']=="test":
    script=script\
      +"##\n"\
      +"## run in test que\n"\
      +"#$ -l test=true\n"
  if settings['email']!=None:
    script=script\
      +"##\n"\
      +"## Email on end, abort or suspend\n"\
      +"#$ -m eas\n"\
      +"##\n"\
      +"## Who to email\n"\
      +"#$ -M "+settings['email']+"\n"
  if settings['checkPointing']:
    script=script\
      +"##\n"\
      +"## Checkpointing via grid engine\n"\
      +"#$ -ckpt transparent\n"\
      +"#$ -c xs\n"\
      +"#$ -notify\n"\
      +"trap '' usr2\n"
  script=script+settings['mpirun']+" "+settings['target']
  f.write(script)
  f.close()
  return scriptName
def main():
  
  #make command line parser
  parser=op.OptionParser(usage="Usage: %prog [options]"
    ,version="%prog 1.0"
    ,description="Starts a SPHERLS run by parsing the SPHERLS.xml configuration file")
  parser.add_option("-d",action="store_true",dest="dryRun"
    ,help="If set it print out the run command but not execute it[not default]."
    ,default=False)
  
  #parse command line options
  (options,args)=parser.parse_args()

  settings=parseXML("SPHERLS.xml")
  
  #additional hard coded settings
  settings['mpirun']="mpirun"
  settings['target']=paths.SPHERLSPath
  
  if settings['que']==None and not settings['totalview']==True:# if not running in que
    cmd=settings['mpirun']+" -np "+settings['numProcs']+" "+settings['target']
    if options.dryRun:
      print cmd
    else:
      os.system(cmd)
  elif settings['totalview']==True:#if running with a debugger
    cmd=settings['mpirun']+" --debug -np "+settings['numProcs']+" "+settings['target']
    if options.dryRun:
      print cmd
    else:
      os.system(cmd)
  else:#if submitting to a que
    
    #additional hard coded settings only needed when submitting to a que
    settings['shell']="/bin/bash"
    settings['outputFile']=settings['jobName']+".out"
    settings['errorFile']=settings['jobName']+".err"
    settings['checkPointing']=False
    script=makeSubScript(settings)
    if script!=None:#sub the job in the que\n
      cmd="qsub "+script
      if options.dryRun:
        print cmd
      else:
        os.system(cmd)
if __name__ == "__main__":
  main()
  