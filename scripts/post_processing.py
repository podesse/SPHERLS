#!/usr/bin/env python
import sys
import os
import optparse as op
import xml.etree.ElementTree as xml
import paths
#import subprocess
import multiprocessing
import time
import random
def main():
  
  parser=op.OptionParser(usage="Usage: %prog [options]"
    ,version="%prog 1.0"
    ,description="Searches subdirectories of the current directory for \"SPHERLS.xml\" files"
      +"when found it skips searches in any output directories listed in \"SPHERLS.xml\"+ it then "
      +"generates submissions scripts and submits jobs to run \"average_PKE.py\" in output "
      +"directories found in the \"SPHERLS.xml\" files. \"average_PKE.py\" will combine "
      +"distributed binary files and create radial profiles from the combined binary files, "
      +"finally it will sum up the Kinetic Energy in each profile, and find the peaks, and average "
      +"the peaks over 6 peaks/3periods.")
  parser.add_option('-n',default=10,type=int,dest="n",help="Sets the maximum number of jobs/threads "
    +"to submit/run at one time. [default: %default]")
  parser.add_option('-d',action="store_true",dest="d",default=False,help="Perform a dry run. "
    +"It will search directories and let the user know what files it finds but doesn't actually "
    +"create any submit scripts or submit any jobs. [not default]")
  parser.add_option('-t',action="store_true",dest="t",default=False,help="If set will use "
    +"threading instead of the sun grid engine")
  
  #parse command line options
  (options,args)=parser.parse_args()
  
  '''if options.t:
    print "not yet supported"
    quit()'''
  
  #get output file names and paths for running average_PKE.py in
  outputFilePaths=[]
  outputFileNames=[]
  count=0
  cwd=os.path.abspath('./')
  for root,dirs,files in os.walk(cwd):
    if "SPHERLS.xml" in files:
      (outputPath,outputFileName)=getConfigOutputDIR(os.path.join(root,"SPHERLS.xml"))
      outputFilePaths.append(outputPath)
      outputFileNames.append(outputFileName)
      count+=1
    
    #remove output directories from search, potentially lots of files in there that 
    #we know we won't need to search through
    for dir in dirs:
      testDir=os.path.join(root,dir)
      if testDir in outputFilePaths:
        dirs.remove(dir)
  
  if options.t:#use threads
    totalNumProcs=min(len(outputFilePaths),options.n)
    p=[]
    jobNames=[]
    numProcs=0
    random.seed(10)
    waitChars=["|","\\","-","/"]
    waitState=0
    for i in range(len(outputFilePaths)):
      if numProcs<totalNumProcs:#add another process
        jobName=os.path.relpath(outputFilePaths[i])
        jobName=jobName.replace("/","_")
        jobName=jobName.replace("\\","_")
        print "starting job "+jobName+", "+str(i+1)+"/"+str(len(outputFilePaths))
        p.append(multiprocessing.Process(target=runAverage
          , args=(os.path.join(outputFilePaths[i],outputFileNames[i]),jobName,options)))
        jobNames.append(jobName)
        p[i].start()
        numProcs+=1
      if numProcs>=totalNumProcs and i+1<len(outputFilePaths):#wait for a job to finish before starting a new one
        sys.stdout.write("\nnumber of processes is "+str(numProcs)+" which is the maximum number "
          +"of concurrent \n")
        sys.stdout.write("processes allowed, waiting for a process to finish before starting "
          +"more\n")
        sys.stdout.flush()
        while numProcs>=totalNumProcs:
          sys.stdout.write("\r"+waitChars[waitState])
          sys.stdout.flush()
          waitState+=1
          if waitState>=len(waitChars):
            waitState=0
          numProcs=0
          for j in range(len(p)):#check to see how many tasks are still running
            if p[j].is_alive():
              numProcs+=1
          if numProcs>=totalNumProcs:
            time.sleep(0.3)#wait a tenth of a second before trying again
        sys.stdout.write("\n\n")
    print "All jobs started, waiting for jobs to finish ..."
    for i in range(len(p)):
      p[i].join()
      print "job "+jobNames[i]+" finished"
  else:#use the que
    #create submit scripts, and run job
    settings={}
    settings['shell']="/bin/bash"
    settings['exe']=os.path.join(paths.scriptPaths,"average_PKE.py")
    for i in range(len(outputFilePaths)):
      
      jobName=os.path.relpath(outputFilePaths[i])
      jobName=jobName.replace("/","_")
      jobName=jobName.replace("\\","_")
      print jobName,outputFileNames[i]
      
      #create submission script
      script=""
      if not options.d:#if not a dry run make submit scripts
        settings['jobName']=jobName
        settings['arguments']=[os.path.join(outputFilePaths[i],outputFileNames[i])+"_t[0-*]"]
        script=makeSubScript(settings)
      
      #run job
      if not options.d:
        cmd="qsub "+script
        os.system(cmd)
      if i+1>=options.n:# if the maximum number of jobs are exceed stop
        break
def runAverage(outputFileName,logFile,options):
  cmd=os.path.join(paths.scriptPaths,"average_PKE.py")
  cmd+=" "+outputFileName+"_t[0-*] >"+logFile+".out"
  if options.d:
    print cmd
  else:
    os.system(cmd)
def getConfigOutputDIR(fileName):
  cwd=os.path.abspath("./")
  dir=os.path.dirname(fileName)
  tree=xml.parse(fileName)
  root=tree.getroot()
  outputNameElement=root.find("outputName")
  if outputNameElement!=None:
    text=outputNameElement.text
    if text!="":
      os.chdir(dir)
      outputPath=os.path.abspath(os.path.dirname(text))
      fileName=os.path.basename(text)
      os.chdir(cwd)
      return outputPath,fileName
  return None
def makeSubScript(settings):
  '''
  Creates a submit script for the sun grid engine based on settings, and returns the name of the 
  script. If no que was specified it returns None.
  '''
  #additional hard coded settings
  scriptName=settings['jobName']+"_que.sh"
  f=open(scriptName,'wb')
  script="#!"+settings['shell']+"\n"\
    +"##\n"\
    +"##Shell to run job in\n"\
    +"#$ -S "+settings['shell']+"\n"\
    +"##\n"\
    +"## Set job name\n"\
    +"#$ -N J"+settings['jobName']+"\n"\
    +"##\n"\
    +"## Run job from current working directory\n"\
    +"#$ -cwd\n"\
    +"##\n"\
    +"#$ -j y\n"\
    +"## Output file name\n"\
    +"#$ -o "+settings['jobName']+".out\n"\
    +"##\n"\
    +"## Transfer all environment variables when job is submitted\n"\
    +"#$ -V\n"
  script=script+settings['exe']+" "
  if "arguments" in settings.keys():
    for argument in settings['arguments']:
      script+=argument+" "
  script+="\n"
  f.write(script)
  f.close()
  return scriptName
if __name__ == "__main__":
  main()