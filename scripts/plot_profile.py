#!/usr/bin/env python

import datafile
import optparse as op
import make_profiles
import glob
import numpy as np
import sys
import os
import disect_filename
import parser
from math import *
import xml.etree.ElementTree as xml

def parseOptions():
  #note: newlines are not respected in the optparse description string :(, maybe someday will use
  #argparse, which does allow for raw formating (repects indents, newlines etc.)
  
  #setup command line parser
  '''This is out of date, needs to be updated to reflect new additions'''
  parser=op.OptionParser(usage="Usage: %prog [options] XMLFILE"
    ,version="%prog 1.0",description=r"Reads in the XMLFILE which specifies how the plot is to be "
    +"made and generates the plot of plots accordingly.")
    
  #these options apply globaly
  parser.add_option("-s","--show",dest="show",action="store_true",default=False
    ,help="Display plot to x11 display rather than saving to a file.")
  parser.add_option("-k","--keep",action="store_true",dest="keep"
    ,help="Keeps distributed binary files [default].",default=True)
  parser.add_option("-r","--remove",action="store_false",dest="keep"
    ,help="Removes distributed binary files")
  parser.add_option("-m","--remake",action="store_true",dest="remake"
    ,help="Will remake profiles if they already exist. [not default].",default=False)
  parser.add_option("--remake-bins",action="store_true",dest="remakeBins"
    ,help="Will remake binaries even if they already exist. [not default].",default=False)
  parser.add_option("--dpi",dest="dpi",type="float",default=100
    ,help="Sets the dots per inch of the figure [default: %default]")
  parser.add_option("--space-axis-evenly",action="store_true",dest="spaceAxisEvenly"
    ,help="Will give the same amount of space per x-axis, instead of per plot. [not default]."
    ,default=False)
  
  #should likely be per plot, at the momement they are across all plots
  parser.add_option("--zone-index-from-center",dest="zoneIndexFromCenter",
    help="Specifies the radial zone at which to plot the desired column should starts with the "
    "center zone equal to zero and the zone number increasing towards the surface"
    ,action="store_true",default=False)
  parser.add_option("--fig-width",dest="figWidth",type="float",default=15
    ,help="Set the width of the figure [default: %default]")
  parser.add_option("--fig-height",dest="figHeight",type="float",default=9
    ,help="Set the height of the figure [default: %default]")
  
  #parse command line options
  return parser.parse_args()
class Curve:
  '''This class holds all the information for a curve on a plot.'''
  def __init__(self,element,type):
    
    '''This method initilizes a curve object, the type parameter allows checking curve syntax 
    against axis syntax to see if they match.'''
    
    self.nColumn=None
    self.zone=None
    self.nCurveIDForZoneRef=None
    self.y=[]
    self.index=[]
    self.bTime=None
    self.formulaOrig=None
    self.code=None
    self.style=""
    self.color=""
    self.markersize=3.0
    self.linewidth=1.0
    self.testZoneAdjust=False#triggered first time zoning is adjusted so doesn't adjust it every load
    self.label=None
    
    #set curve style
    if element.get("style")!=None:
      self.style=element.get("style")
    
    #set curve color
    if element.get("color")!=None:
      self.color=element.get("color")
      
    #set curve label
    if element.get("label")!=None:
      self.label=element.get("label")
    
    #get marker size
    if element.get("markersize")!=None:
      if element.get("markersize").isdigit():
        self.markersize=float(element.get("markersize"))
      else:
        print "\"markersize\" must be a float, got \"",element.get("markersize"),"\""
    
    #get linewidth
    if element.get("linewidth")!=None:
      if element.get("linewidth").isdigit():
        self.linewidth=float(element.get("linewidth"))
      else:
        print "\"linewidth\" must be a float, got \"",element.get("linewidth"),"\""
    
    #set that the curve is a time, or profile curve
    if type=="time":
      self.bTime=True
    else:
      self.bTime=False
    
    #if it is a time axis, make sure we know which radial zone to plot from
    if self.bTime:
      if element.get("radialZone")!=None and element.get("radialZone")!="":
        if element.get("radialZone")=="max":
          self.zone="max"
        elif element.get("radialZone")=="min":
          self.zone="min"
        elif element.get("radialZone").isdigit():
          self.zone=element.get("radialZone")
        else:
          print "Attribute \"radialZone\" set to \"",element.get("radialZone"),"\" expecting "\
            +"either a zone number, \"max\", or \"min\""
          quit()
      else:
        print "Attribute \"radialZone\" must be set for a curve in an axis of type=\"time\""
        quit()
    
    if element.text.isdigit():
      self.nColumn=int(element.text)-1
    else:
      
      #if there is a foluma get list of columns
      self.formulaOrig=element.text
      columnsTemp=self.formulaOrig.split('$')
      self.formula=columnsTemp[0]
      if len(columnsTemp)>1:#turn into a list
        self.nColumn=[]
        for i in range(1,len(columnsTemp)):
          columnAndFormula=splitFirstInt(columnsTemp[i])
          self.formula+="a["+str(i-1)+"]"+columnAndFormula[1]
          self.nColumn.append(columnAndFormula[0]-1)
        self.code=parser.expr(self.formula).compile()
      else:
        self.formula=None
        if element.text == None or element.text=="":
          print "No column number given for curve, must have curve text be either an integer, or"\
            +" a mathatmical formula containing column references prefixed with a \"$\"."
          quit()
  def load(self,fileData,options):
    '''This method adds a y value and index to the curve for the current fileData.'''
    
    if self.zone=="max":
      #find largest value in column and use that
      nIndex=0
      while getY(self.nColumn,fileData,self.code,nIndex)==None:
        nIndex=nIndex+1
      yTemp=getY(self.nColumn,fileData,self.code,nIndex)
      yIndexTemp=0
      for i in range(nIndex,len(fileData.fColumnValues)-1):
        yTest=getY(self.nColumn,fileData,self.code,i)
        if yTest>yTemp:
          yTemp=yTest
          yIndexTemp=i
      self.y.append(yTemp)
      self.index.append(yIndexTemp)
    elif self.zone=="min":
      #find smallest value in column and use that
      nIndex=0
      while getY(self.nColumn,fileData,self.code,nIndex)==None:
        nIndex=nIndex+1
      yTemp=getY(self.nColumn,fileData,self.code,nIndex)
      yIndexTemp=0
      for i in range(nIndex,len(fileData.fColumnValues)-1):
        testY=getY(self.nColumn,fileData,self.code,nIndex)
        if testY<yTemp:
          yTemp=testY
          yIndexTemp=i
      self.y.append(yTemp)
      self.index.append(yIndexTemp)
    elif self.zone==None and self.bTime==False:#this will be a series of y's as a function of time,
      #creating a 2D list instead of a 1D list
      yTemp=[]
      for i in range(len(fileData.fColumnValues)):
        yTemp.append(getY(self.nColumn,fileData,self.code,i))
      self.y.append(yTemp)
      
    elif self.zone==None:
      print "If zone=",self.zone," is \"None\" then it shouldn't be a time curve and thus the if "\
        +"above should have been flagged first, something strange is going on here"
    elif self.zone.isdigit():
      if not self.testZoneAdjust:
        if not options.zoneIndexFromCenter:
          zone=len(fileData.fColumnValues)-1-int(self.zone)
          
          #if right at the surface, and the zone is a non-interface, should move in
          while getY(self.nColumn,fileData,self.code,zone)==None:
            zone=zone-1
          self.zone=str(zone)
        self.testZoneAdjust=True
      self.y.append(getY(self.nColumn,fileData,self.code,int(self.zone)))
      self.index.append(int(self.zone))
    else:#I don't know what to do ??
      print "unknown zone spedificiation \"",zone,"\""
class Plot:
  '''This class holds all the information for a single plot, namely the list of curves for that plot.'''
  
  def __init__(self,element,type):
    '''This method initlizes the plot object'''
    
    self.ylabel=None
    self.curves=[]
    self.limits=None
    self.grid=None
    self.bMinorTics=False
    self.legendloc=1
    
    #check for grid setting
    if element.get("grid")!=None:
      if element.get("grid").lower() in ["major","minor","both"]:
        self.grid=element.get("grid").lower()
      else:
        print "Grid type for plot unrecognized \"",element.get("grid"),"\" should be \"major\","\
          +" \"minor\", or \"both\"."
        quit()
    
    #check if using minor tics
    if element.get("yminortics")!=None:
      if element.get("yminortics").lower() in ["true","1","t","yes","y"]:
        self.bMinorTics=True
    
    #get ylabel
    if element.get("ylabel")!=None and element.get("ylabel")!="":
      self.ylabel=element.get("ylabel")
    
    #get range
    yMin=None
    if element.get("ymin")!=None and element.get("ymin")!="":
      yMin=float(element.get("ymin"))
    yMax=None
    if element.get("ymax")!=None and element.get("ymax")!="":
      yMax=float(element.get("ymax"))
    self.limits=[yMin,yMax]
    
    #get ledgend location
    if element.get("legendloc")!=None and element.get("legendloc")!="":
      self.legendloc=int(element.get("legendloc"))
    
    #add curves to plot
    curveElements=element.findall("curve")
    for curveElement in curveElements:
      self.curves.append(Curve(curveElement,type))
  def load(self,fileData,options):
    '''loads the data for a plot, y-data is stored in the curves, and sets the ylabel from the first
    file read in'''
    
    if self.ylabel==None:#if not already set, this should be triggered only on the first load
      
      for curve in self.curves:
        
        #load curve data
        curve.load(fileData,options)
        
        #add zone number to suffix
        suffix=''
        if curve.bTime:
          suffix="_"+curve.zone
        
        #add curve reference to suffix
        if curve.nCurveIDForZoneRef!=None:
          suffix='_ref('+str(curve.nCurveIDForZoneRef)+')'
        
        #set ylabel
        if self.ylabel==None:
          if isinstance(curve.nColumn,int):
            self.ylabel=fileData.sColumnNames[curve.nColumn]+suffix
          else:
            self.ylabel=curve.formulaOrig+suffix
        else:
          if isinstance(curve.nColumn,int):
            self.ylabel=self.ylabel+", "+fileData.sColumnNames[curve.nColumn]+suffix
          else:
            self.ylabel=self.ylabel+", "+curve.formulaOrig+suffix
    else:#for all subsequent files
      for curve in self.curves:
        curve.load(fileData,options)
class Axis:
  '''This class holds all the information needed for a particular x-axis. An axis can either be 
  either of time, or of some column in the data files.'''
  
  def __init__(self,element,options):
    '''This function initizalizes the axis object.'''
    
    self.plots=[]
    self.bTime=False
    self.period=None
    self.nColumn=None
    self.xlabel=None
    self.x=[]
    self.formulaOrig=None
    self.formula=None
    self.phase=[]
    self.code=None
    self.limits=None
    self.bMinorTics=False
    
    #check for grid setting
    if element.get("grid")!=None:
      if element.get("grid").lower() in ["major","minor","both"]:
        self.grid=element.get("grid").lower()
      else:
        print "Grid type for plot unrecognized \"",element.get("grid"),"\" should be \"major\","\
          +" \"minor\", or \"both\"."
        quit()
    
    #check if using minor tics
    if element.get("xminortics")!=None:
      if element.get("xminortics").lower() in ["true","1","t","yes","y"]:
        self.bMinorTics=True
    
    #get type of axis
    if element.get("type")=="time":
      self.bTime=True
    elif element.get("type")=="profile":
      self.bTime=False
    else:
      print "axis type is \"",element.get("type"),"\" must be either \"profile\" or \"time\"."
      quit()
    
    #if time axis set period if there is one
    if self.bTime and element.get("period") != None:
      self.period=float(element.get("period"))
    
    #get xlabel
    self.xlabel=element.get("xlabel")
    if self.xlabel==None and self.bTime:
      if self.period!=None:
        self.xlabel="phase"
      else:
        self.xlabel="t [s]"
    
    #get xrange
    xMin=None
    if element.get("xmin")!=None and element.get("xmin")!="":
      xMin=float(element.get("xmin"))
    xMax=None
    if element.get("xmax")!=None and element.get("xmax")!="":
      xMax=float(element.get("xmax"))
    self.limits=[xMin,xMax]
    
    #get column if not a time axis
    if not self.bTime:
      
      #if there is a foluma get list of columns
      self.formulaOrig=element.get("column")
      columnsTemp=self.formulaOrig.split('$')
      self.formula=columnsTemp[0]
      if len(columnsTemp)>1:#turn into a list
        self.nColumn=[]
        for i in range(1,len(columnsTemp)):
          columnAndFormula=splitFirstInt(columnsTemp[i])
          self.formula+="a["+str(i-1)+"]"+columnAndFormula[1]
          self.nColumn.append(columnAndFormula[0]-1)
        self.code=parser.expr(self.formula).compile()
      else:
        self.formula=None
        if element.get("column") == None or element.get("column")=="":
          print "no column number given for axis, must set \"column\" to an integer, or a "\
            +"mathatmical formula containing column references prefixed with a \"$\""
          quit()
        else:
          self.nColumn=int(element.get("column"))-1
    
    #add plots to axis
    plotElements=element.findall("plot")
    for plotElement in plotElements:
      type="profile"
      if self.bTime:
        type="time"
      self.plots.append(Plot(plotElement,type))
      
  def load(self,fileData,options):
    '''This function loads the values needed for the x-axis data from the fileData argument'''
    
    if self.bTime:#add time
      fileHeader=fileData.sHeader.split()
      self.x.append(float(fileHeader[1]))
      
      #set phase
      if self.period!=None:
        self.phase.append((float(fileHeader[1])-self.x[0])/self.period)
        
    else:#assuming if it isn't time data, it is column data
      if self.nColumn!=None:
        if self.xlabel==None:
          if isinstance(self.nColumn,int):
            self.xlabel=fileData.sColumnNames[self.nColumn]
          else:
            self.xlabel=self.formulaOrig
        xTemp=[]
        for i in range(len(fileData.fColumnValues)):
          xTemp.append(getY(self.nColumn,fileData,self.code,i))
        self.x.append(xTemp)
          
    #load plots
    for plot in self.plots:
      plot.load(fileData,options)
class DataSet:
  '''This class holds all the information for a single dataSet, which includes the baseFileName of 
  the dataset, the range of the dataSet (start-end), the times and phases of the files within the 
  range of the dataSet, and the plots made from the dataSet.'''
  
  def __init__(self,element,options):
    '''Initilizes the dataSet by setting baseFileName, start, end, and intilizing plots from an xml 
    element'''
    
    #set some initial values
    self.baseFileName=None
    self.start=None
    self.end=None
    self.axes=[]
    self.nNumFiles=None
    self.fileIndices=[]
    self.hasNonTimeAxis=False
    
    [self.start,self.end,self.baseFileName]=disect_filename.disectFileName(element.attrib["fileRange"])
    
    #add axes to dataset
    axisElements=element.findall("axis")
    for axisElement in axisElements:
      axis=Axis(axisElement,options)
      self.axes.append(axis)
      if not axis.bTime:
        self.hasNonTimeAxis=True
  
  def load(self,options):
    '''Loads the dataSet, this means that it sets, time, phases, and plots data'''
    
    #make sure that all the combined binary files within range of dataset have profiles made
    fileName=self.baseFileName+"["+str(self.start)+"-"+str(self.end)+"]"
    make_profiles.make_profiles(options.keep,fileName,options.remake,options.remakeBins)
    
    #get and sort profiles within range of dataset
    extension="_pro"+".txt"
    filesExistProfiles=glob.glob(self.baseFileName+"*"+extension)
    files=[]
    for file in filesExistProfiles:
      intOfFile=int(file[len(self.baseFileName):len(file)-len(extension)])
      if intOfFile>=self.start and intOfFile<self.end:
        files.append(file)
    files.sort()
    if len(files)==0:
      print "no files found in range"
      quit()
    
    self.nNumFiles=len(files)
    
    #create time, phase and curve y's for dataset
    nFileCount=0
    for file in files:
      
      #get file index
      temp=file[file.find("_t")+2:]
      self.fileIndices.append(temp[:temp.find("_pro")])
      
      #read in profile
      print "reading in profile ",file," ..."
      fileData=datafile.DataFile()
      fileData.readFile(file)
      
      #load x-axis data and y-data
      for axis in self.axes:
        axis.load(fileData,options)
            
  def getCurve(self,ID):
    '''Returns a curve object that has ID, ID'''
    nCount=0
    for axis in self.axes:
      for plot in axis.plots:
        for curve in plot.curves:
          if nCount==ID:
            return curve
          nCount=nCount+1
def plot(dataSets,options,title):
  
  #set import options based on weather it will saved to a file, or sent to x11
  #print "interactive backends=",matplotlib.rcsetup.interactive_bk
  #print "non-interactive backends=",matplotlib.rcsetup.non_interactive_bk
  #print "all backends=",matplotlib.rcsetup.all_backends
  
  import matplotlib
  if not options.show:
    matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  
  from matplotlib.gridspec import GridSpec
  
  #basic plot spacing options
  axisSpacing=0.05
  figBottom=0.05
  figTop=0.95
  
  #count number of axes in all plots, this number will be the same for all plots.
  nNumAxes=0
  for dataSet in dataSets:
    nNumAxes=nNumAxes+len(dataSet.axes)
  heightAxis=((figTop-figBottom)-axisSpacing*(nNumAxes-1.0))/nNumAxes
  
  #count number of plots
  nNumPlots=0
  for dataSet in dataSets:
    for axis in dataSet.axes:
      nNumPlots=nNumPlots+len(axis.plots)
  heightPlot=((figTop-figBottom)-axisSpacing*(nNumAxes-1.0))/nNumPlots
  
  #figure out how many output files will be made, will match the largest number of files read in of
  #all dataSets
  nMaxNumFiles=1
  for dataSet in dataSets:
    bNonTimeAxis=False
    for axis in dataSet.axes:
      if axis.bTime:
        bNonTimeAxis=True
    if dataSet.hasNonTimeAxis:
      if nMaxNumFiles<dataSet.nNumFiles:
        nMaxNumFiles=dataSet.nNumFiles
  
  #create plots
  fileCount=0
  fileStart=0
  for i in range(nMaxNumFiles):
    
    fig=plt.figure(figsize=(options.figWidth,options.figHeight))
    axisCount=0
    nTotalPlotCount=1
    dataSetCount=0
    ax=[]
    gs=[]
    top=figTop
    
    #add title
    if title!="":
      tempTitle=title
      count=0
      for dataSet in dataSets:
        for axisMine in dataSet.axes:
          if axisMine.bTime:
            time=axisMine.x[fileCount]
            timeStr=format(time,"0.4e")
            tempTitle=tempTitle.replace("\\time"+str(count),timeStr)
            break
            
            if axisMine.period!=None:
              phase=axisMine.phase[fileCount]
              phaseStr=format(phase,"0.4e")
              tempTitle=tempTitle.replace("\phase"+str(count),phaseStr)
              break
        indexStr="\index"+str(count)
        tempTitle=tempTitle.replace(indexStr,str(dataSet.fileIndices[fileCount]))
        count+=1
        
      #find out if we have any time plots
      fig.suptitle(tempTitle)
    
    for dataSet in dataSets:
      for axisMine in dataSet.axes:
        gs.append(GridSpec(len(axisMine.plots),1))
        bottom=top-heightPlot*(len(axisMine.plots))
        if options.spaceAxisEvenly:
          top=figTop-axisCount*(heightAxis+axisSpacing)
          bottom=figBottom+(nNumAxes-1.0-axisCount)*(heightAxis+axisSpacing)
        gs[axisCount].update(top=top,bottom=bottom,hspace=0.0)
        
        #for each plot
        nPlotCount=0
        for plot in axisMine.plots:
          
          #create a subplot
          ax.append(plt.subplot(gs[axisCount][nPlotCount,0]))
          
          #set minor axis tics
          if axisMine.bMinorTics:
            ax[nTotalPlotCount-1].xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
          if plot.bMinorTics:
            ax[nTotalPlotCount-1].yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
          
          #set grid settings
          if plot.grid!=None:
            ax[nTotalPlotCount-1].grid(True, which=plot.grid)
          else:
            ax[nTotalPlotCount-1].grid(False)
          
          #for each curve in the plot
          lines=[]
          labels=[]
          if axisMine.bTime:
            curveCount=0
            for curve in plot.curves:
              
              #plot the curve
              if axisMine.period!=None:#use phase instead of time if period is given
                temp=ax[nTotalPlotCount-1].plot(axisMine.phase,curve.y
                  ,curve.color+curve.style,markersize=curve.markersize,linewidth=curve.linewidth)
                if curve.label!=None and curve.label!="":
                  lines.append(temp)
                  labels.append(curve.label)
                if dataSet.hasNonTimeAxis:#only need bar, if there are non-time axes in dataSet
                  limits=ax[nTotalPlotCount-1].axis()
                  xTemp=[axisMine.phase[fileCount],axisMine.phase[fileCount]]
                  yTemp=[limits[2],limits[3]]
                  if plot.limits[0]!=None:
                    yTemp[0]=plot.limits[0]
                  if plot.limits[1]!=None:
                    yTemp[1]=plot.limits[1]
                  ax[nTotalPlotCount-1].plot(xTemp,yTemp,'r-',linewidth=curve.linewidth)
              else:
                temp=ax[nTotalPlotCount-1].plot(axisMine.x,curve.y,curve.color+curve.style
                  ,markersize=curve.markersize,linewidth=curve.linewidth)
                if curve.label!=None and curve.label!="":
                  lines.append(temp)
                  labels.append(curve.label)
                if dataSet.hasNonTimeAxis:#only need bar, if there are non-time axes in dataSet
                  limits=ax[nTotalPlotCount-1].axis()
                  xTemp=[axisMine.x[fileCount],axisMine.x[fileCount]]
                  yTemp=[limits[0],limits[1]]
                  if plot.limits[0]!=None:
                    yTemp[0]=plot.limits[0]
                  if plot.limits[1]!=None:
                    yTemp[1]=plot.limits[1]
                  ax[nTotalPlotCount-1].plot(xTemp,yTemp,'r-',linewidth=curve.linewidth)
              curveCount=curveCount+1
          else:
            curveCount=0
            for curve in plot.curves:
              
              #plot the curve
              temp=ax[nTotalPlotCount-1].plot(axisMine.x[i],curve.y[i]
                ,curve.color+curve.style,markersize=curve.markersize,linewidth=curve.linewidth)
              if curve.label!=None and curve.label!="":
                lines.append(temp)
                labels.append(curve.label)
              curveCount=curveCount+1
          ax[nTotalPlotCount-1].set_xlim(axisMine.limits)
          ax[nTotalPlotCount-1].set_ylim(plot.limits)
          
          #set legend
          if len(lines)>0:
            ax[nTotalPlotCount-1].legend(lines,labels,loc=plot.legendloc)
          
          #remove x-axis labels
          if nPlotCount!=len(axisMine.plots)-1:
            plt.setp(plt.gca(), 'xticklabels', [])
          else:
            ax[nTotalPlotCount-1].set_xlabel(axisMine.xlabel)
          
          #set y-axis labels
          ax[nTotalPlotCount-1].set_ylabel(plot.ylabel)
          
          #remove top and bottom y-axis tic labels
          ax[nTotalPlotCount-1].yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(prune='both'))
          
          #adjust hspace to be 0 so plots for the same x-axis will be tight
          nPlotCount=nPlotCount+1#resets every axis
          nTotalPlotCount=nTotalPlotCount+1#continues to increase for all plots
        
        top=bottom-axisSpacing
        axisCount=axisCount+1
    
    #done making plot
    if options.show:
      print "ploting file ",i," to screen, close for next plot"
      plt.show()
    else:
      [path,ext]=os.path.splitext(options.outputFile)
      supportedFileTypes=["png", "pdf", "ps", "eps", "svg"]
      if ext[1:] not in supportedFileTypes:
        print "File type \""+ext[1:]+"\" not suported. Supported types are ",supportedFileTypes," please choose one of those"
        quit()
      print __name__+":"+main.__name__+": saving figure to file \""+path+"_"+str(fileCount)+ext+"\" ..."
      fig.savefig(path+"_"+str(fileCount)+ext,format=ext[1:],transparent=False,dpi=options.dpi)#save to file
      plt.close(fig)
    fileCount=fileCount+1
def splitFirstInt(str):
  '''Returns the integer which starts at the very first character of str, and drops everything else 
  from str'''
  
  strInt=''
  i=0
  while str[i].isdigit() or (str[i]=='-' and i==0):
    strInt=strInt+str[i]
    i=i+1
    if i>=len(str):#check that we haven't passed the end of the string
      break
  return [int(strInt),str[i:]]
def splitFirstFloat(str):
  '''Returns the integer which starts at the very first character of str, and drops everything else 
  from str'''
  
  strInt=''
  i=0
  nExponentIndex=-1
  nDecimalCount=0
  while str[i].isdigit()\
    or ((str[i]=='-' or str[i]=='+') and i==0)\
    or ((str[i]=="e" or str[i]=="E") and nExponentIndex==-1)\
    or ((str[i]=="-" or str[i]=="+") and nExponentIndex+1==i)\
    or (str[i]=="." and nDecimalCount==0) :
    if str[i]=="e" or str[i]=="E":
      nExponentIndex=i
    if str[i]==".":
      nDecimalCount=nDecimalCount+1
    strInt=strInt+str[i]
    i=i+1
    if i>=len(str):#check that we haven't passed the end of the string
      break
  return [float(strInt),str[i:]]
def getY(nColumn,fileData,code,i):
  if isinstance(nColumn,int):
    #normal simple 1 column data
    return fileData.fColumnValues[i][nColumn]
  else:
    #new column operation
    a=[]
    for j in range(len(nColumn)):
      if fileData.fColumnValues[i][nColumn[j]]==None:
        return None
      else:
        a.append(fileData.fColumnValues[i][nColumn[j]])
    return eval(code)
def main():
  
  #parse command line options
  (options,args)=parseOptions()
  
  #get root element
  tree=xml.parse(args[0])
  root=tree.getroot()
  
  #set plot title
  title=""
  if root.get("title")!=None and root.get("title")!="":
    title=root.get("title")
  
  #set plot output
  if root.get("outputfile")!=None and root.get("outputfile")!="":
    options.outputFile=root.get("outputfile")
    [path,ext]=os.path.splitext(options.outputFile)
    supportedFileTypes=["png", "pdf", "ps", "eps", "svg"]
    if ext[1:] not in supportedFileTypes:
      print "File type \""+ext[1:]+"\" not suported. Supported types are ",supportedFileTypes," please choose one of those"
      quit()
  
  #get list of dataSet elements
  dataSetElements=root.findall("dataSet")
  
  #initialize datasets
  dataSets=[]
  for dataSetElement in dataSetElements:
    dataSets.append(DataSet(dataSetElement,options))
  
  #load datasets
  i=0
  for dataSet in dataSets:
    print "reading in data set ",i
    dataSet.load(options)
    i=i+1
  
  #plot datasets
  plot(dataSets,options,title)
  
  return
if __name__ == "__main__":
  main()