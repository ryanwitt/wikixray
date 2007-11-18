#############################################
#      WikiXRay: Quantitative Analysis of Wikipedia language versions                       
#############################################
#                  http://wikixray.berlios.de                                              
#############################################
# Copyright (c) 2006-7 Universidad Rey Juan Carlos (Madrid, Spain)     
#############################################
# This program is free software. You can redistribute it and/or modify    
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 or later of the GPL.     
#############################################
# Author: Jose Felipe Ortega Soto                                                             

"""
This module contains some methods to create graphics and files with 
statistical results about Wikipedia database dumps.

@see: quantAnalay_main

@authors: Jose Felipe Ortega, Jesus M. Gonzalez-Barahona
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jfelipe@gsyc.escet.urjc.es
"""

from rpy import *
import dbaccess, test_admins
import math, os, string, Numeric

class graphic(object):
    """
    Super class for all graphic classes
    """
    def __init__(self, filePath):
##        An tuple or list with sets of data to draw in the graphic
##        As a minimum you must provide (((x0,y0),(x1,y1),...,(xN, yN)),) for 2D graphics and
##        (((y0,),(y1,),...,(yN)),) for Gini graphics
##        Path to save the plotted files
        self.filePath=filePath
        
    def getDataList(self):
        return dataList
        
    def getFilename(self):
        return filename
        
    def getFilePath(self):
        return filePath
        
    def createGraphic(self, filename, data):
##        Clear dataList
        self.dataList=[]
        for set in data:
##            Create a new list for every set of values
            self.dataList.append(list())
        for column in data[0][0]:
            for set in self.dataList:
##           Create a list for every column in every set
                set.append(list())
        for i in range(0, len(data)):
##            Append elements to corresponding list
            for element in data[i]:
                for j in range(0, len(element)):
                    self.dataList[i][j].append(float(element[j]))
##        Set name of the file to be plotted
        self.filename=filename
        
    def gini_Coef(self, values):
        """
        Plots a GINI graph for author contributions 
        
        @type  values: list of ints
        @param values: list of integers summarizing total contributions for each registered author
        """
        sum_numerator=0
        sum_denominator=0
        for i in range(1, len(values)):
            sum_numerator+=(len(values)-i)*values[i]
            sum_denominator+=values[i]
##        Apply math function for the Gini coefficient
        g_coeff= (1.0/(len(values)-1))*(len(values)-2*(sum_numerator/sum_denominator))
        return g_coeff
        
class graphicRpy(graphic):
    """
    Graphic classes using Rpy to plot graphics can inherit directly from this class
    """
    typeDict={"png":".png", "eps":".eps","pdf":".pdf"}
    def __init__(self, filePath):
        super(graphicRpy, self).__init__(filePath)
    
    def createGraphic(self, filename, data, graphType):
        super(graphicRpy, self).createGraphic(filename, data)
        if graphType not in self.typeDict:
            print "Sorry, you chose an unsupported type of file.\n"
            return -1
        else:
            fileExt=self.typeDict[graphType]
            if fileExt==".png":
                r.png(self.filePath+self.filename+fileExt)
            elif fileExt==".eps":
                r.postscript(self.filePath+self.filename+fileExt, onefile=r.FALSE, horizontal=r.FALSE,\
                height=7, width=9,paper="special")
                r.par(mai=r.c(1,1,1,1))
            elif fileExt==".pdf":
                r.pdf(self.filePath+self.filename+fileExt)

class graphicR(graphic):
    """
    Superclass for all classes employing GNUR to plot graphics
    """
    typeDict={"png":("png",".png"), "eps":("postscript",".eps"),"pdf":("pdf",".pdf")}
    def __init__(self, filePath, dataPath):
        super(graphicR, self).__init__(filePath)
        self.dataPath=dataPath
    
    def getFiledata(self):
        return filedata
        
    def createGraphic(self, filename, data, graphType):
        super(graphicR, self).createGraphic(filename, data)
        if graphType not in self.typeDict:
            print "Sorry, you chose an unsupported type of file.\n"
            return -1
        else:
            self.graphDev=self.typeDict[graphType][0]
            self.graphExt=self.typeDict[graphType][1]
                
class graphicGnuplot(graphic):
    """
    Superclass for all classes employing Gnuplot to plot graphics
    """
    def __init__(self, filePath, dataPath):
        super(graphicGnuplot, self).__init__(filePath)
        self.dataPath=dataPath
        
    def getFiledata(self):
        return filedata
        
    def createGraphic(self, filename, data):
        super(graphicGnuplot, self).createGraphic(filename, data)
##        FIX-ME Manage graphic type appropiately
##########################################
##CLASSES with Rpy
##########################################
class graphic2D(graphicRpy):
    """
    A class to plot 2D graphics using Python RPy
    """
    def __init__(self, filePath):
        super(graphic2D, self).__init__(filePath)
        
    def createGraphic(self, filename, data, xlabst, ylabst, mainTitle, graphType="eps",format=[],log=False):
##        Call superclass method to check wheter selected graphType is supported or not
        super(graphic2D,self).createGraphic(filename, data, graphType)
##        Retrieve data series
        self.dataList=self.dataList.pop()
        yvalues=self.dataList.pop()
        yvalues=list(yvalues)
        xvalues=self.dataList.pop()
        xvalues=list(xvalues)
        if len(format)==2:
            if log:
                r.plot(xvalues, yvalues, ylim=r.range(min(yvalues), max(yvalues)),log="y",\
                xlab=xlabst, ylab=ylabst, main=mainTitle, type=format[0], col=format[1])
            else:
                r.plot(xvalues, yvalues, ylim=r.range(min(yvalues), max(yvalues)),\
                xlab=xlabst, ylab=ylabst, main=mainTitle, type=format[0], col=format[1])
        else:
            if log:
                r.plot(xvalues, yvalues, ylim=r.range(min(yvalues), max(yvalues)),log="y",\
                xlab=xlabst, ylab=ylabst, main=mainTitle, type="b", col=2)
            else:
                r.plot(xvalues, yvalues, ylim=r.range(min(yvalues), max(yvalues)),\
                xlab=xlabst, ylab=ylabst, main=mainTitle, type="b", pch=15, col=2)
##        Close graphic device
        r.dev_off()

class graphic2Dmulti(graphicRpy):
    """
    A class to plot multiline 2D graphics using Python RPy
    WARNING
    This time dataList should follow the structure [[[xvals0],[yvalues0]],[[xvalues1],[yvalues1]],...,[[xvaluesN],[yvaluesN]]]
    where each pair of series representing data for line0, line1, ..., lineN
    """
    def __init__(self, filePath):
        super(graphic2Dmulti, self).__init__(filePath)
        
    def createGraphic(self, filename, data, xlabst, ylabst, mainTitle, graphType="eps",format=[],log=True):
##        Call superclass method to check wheter selected graphType is supported or not
        super(graphic2Dmulti,self).createGraphic(filename, data, graphType)
##        Draw the first x-y series
##        Calculate max range
        maximum=0
        for set in self.dataList:
            if max(set[1])>maximum:
                maximum=max(set[1])
        if log:
            maximum=math.log10(maximum)
        lastPair=self.dataList.pop(0)
        lastPair=list(lastPair)
        yvalues=lastPair.pop()
        yvalues=list(yvalues)
        xvalues=lastPair.pop()
        xvalues=list(xvalues)
        if len(format)==2:
            if log:
                for i in range(0, len(yvalues)):
                    if yvalues[i]!=0:
                        yvalues[i]=math.log10(yvalues[i])
                r.plot(xvalues, yvalues,xlab=xlabst, ylab=ylabst, main=mainTitle, type=format[0], col=format[1])
            else:
                r.plot(xvalues, yvalues, xlab=xlabst, ylab=ylabst, main=mainTitle, type=format[0], col=format[1])
        else:
            colour=2
            pointch=2
            if log:
                for i in range(0, len(yvalues)):
                    if yvalues[i]!=0:
                        yvalues[i]=math.log10(yvalues[i])
                r.plot(xvalues, yvalues, ylim=r.range(0, maximum),\
                xlab=xlabst, ylab=ylabst, main=mainTitle, type="b", col=colour, pch=pointch)
            else:
                r.plot(xvalues, yvalues, ylim=r.range(0, maximum),\
                xlab=xlabst, ylab=ylabst, main=mainTitle, type="b", col=colour, pch=pointch)
##        Draw remaining series
        for curPair in self.dataList:
            colour+=1
            pointch+=1
            yvalues=curPair.pop()
            yvalues=list(yvalues)
            xvalues=curPair.pop()
            xvalues=list(xvalues)
            if log:
                for i in range(0, len(yvalues)):
                    if yvalues[i]!=0:
                        yvalues[i]=math.log10(yvalues[i])
                r.lines(xvalues, yvalues, col=colour, pch=pointch)
            else:
                r.lines(xvalues, yvalues, col=colour, pch=pointch)
##        Close graphic device
        r.dev_off()

class graphicBar(graphicRpy):
    """
    A class to plot bar graphics using Python RPy
    """
    def __init__(self, filePath):
        super(graphicBar, self).__init__(filePath)
        
    def createGraphic(self, filename, data, xlabst, ylabst, mainTitle, graphType="eps",format=[],log=False):
##        Call superclass method to check wheter selected graphType is supported or not
        super(graphicBar,self).createGraphic(filename, data, graphType)
##        Retrieve data series
        self.dataList=self.dataList.pop()
        yvalues=self.dataList.pop()
        yvalues=list(yvalues)
        xvalues=self.dataList.pop()
        xvalues=list(xvalues)
        names=[]
        for value in xvalues:
            names.append(str(value))
        if len(format)==2:
            if log:
                r.barplot(yvalues, names=xvalues, ylim=r.range(min(yvalues), max(yvalues)),log="y",\
                xlab=xlabst, ylab=ylabst, main=mainTitle, type=format[0], col=format[1])
            else:
                r.barplot(yvalues, names=xvalues, ylim=r.range(min(yvalues), max(yvalues)),\
                xlab=xlabst, ylab=ylabst, main=mainTitle, type=format[0], col=format[1])
        else:
            if log:
                r.barplot(yvalues, names=xvalues, ylim=r.range(min(yvalues), max(yvalues)),log="y",\
                xlab=xlabst, ylab=ylabst, main=mainTitle, col="royalblue")
            else:
                r.barplot(yvalues, names=xvalues, ylim=r.range(min(yvalues), max(yvalues)),\
                xlab=xlabst, ylab=ylabst, main=mainTitle, col="royalblue")
##        Close graphic device
        r.dev_off()
class graphicGini(graphicRpy):
    """
    A class to plot lorenz curve and Gini coefficient
    """
    def __init__(self, filePath):
##        dataList must provide only one vector of values (total contributions for every author)
        super(graphicGini, self).__init__(filePath)
        
    def createGraphic(self, filename, data, graphType="eps"):
##        Call superclass method to check wheter selected graphType is supported or not
        super(graphicGini, self).createGraphic(filename, data, graphType)
##        Retrieve total contributions for every user
        self.dataList=self.dataList.pop()
        yvaluesLorenz=self.dataList.pop()
##        Insert the first point of the Lorenz curve
        yvaluesLorenz.insert(0, 0)
##        Build array for x values
        xvalues=[]
        for i in range(0, len(yvaluesLorenz)):	
            xvalues.append(100.0*(float(i)/len(yvaluesLorenz)))
##        Call method to work out the Gini coefficient
        gCoeff=super(graphicGini,self).gini_Coef(yvaluesLorenz)
##        Work out aggregate contributions (execept for the first point (0,0))
        aggSum=0
        for j in range(1, len(yvaluesLorenz)):
            aggSum+=yvaluesLorenz[j]
            yvaluesLorenz[j]=aggSum
##        Calculate % of total contributions
        for k in range(len(yvaluesLorenz)):
            yvaluesLorenz[k]=100.0*(float(yvaluesLorenz[k])/yvaluesLorenz[len(yvaluesLorenz)-1])
##        Plot graphic and legend
        r.plot(xvalues, yvaluesLorenz, xlab="(%)Authors",ylab="(%)Cumulative contribution", main="Cumulative Distribution Function", type="l", col=2)
        r.legend(10, 80, legend="Gini Coefficient = %f" % gCoeff)
        r.legend(10, 100, legend=r.c("Line of perfect equality", "Lorenz curve"), col=r.c(1,2), pch=r.c(1,2))
##        Plot line of perfect equality
        r.lines(xvalues, xvalues)
##        Close graphic device
        r.dev_off()
    
class graphicGiniComp(graphicRpy):
    """
    A class to plot several lorenz curves in the same graphic
    for comparative purposes
    """
    def __init__(self, filePath):
##        dataList must provide an array of vector with values for total contributions for every author
##        for all language versions
        super(graphicGiniComp, self).__init__(filePath)
        
    def createGraphic(self, filename, data, graphType="eps"):
##        Call superclass method to check wheter selected graphType is supported or not
        super(graphicGiniComp, self).createGraphic(filename, data, graphType)
##        Retrieve total contributions for every user (last set)
        finalSet=self.dataList.pop()
        yvaluesLorenz=finalSet.pop()
##        Insert the first point of the Lorenz curve
        yvaluesLorenz.insert(0, 0)
##        Build array for x values
        xvalues=[]
        for i in range(0, len(yvaluesLorenz)):	
            xvalues.append(100.0*(float(i)/len(yvaluesLorenz)))
##        Call method to work out the Gini coefficient
        gCoeff=super(graphicGiniComp, self).gini_Coef(yvaluesLorenz)
##        Work out aggregate contributions (execept for the first point (0,0))
        aggSum=0
        for j in range(1, len(yvaluesLorenz)):
            aggSum+=yvaluesLorenz[j]
            yvaluesLorenz[j]=aggSum
##        Calculate % of total contributions
        for k in range(len(yvaluesLorenz)):
            yvaluesLorenz[k]=100.0*(float(yvaluesLorenz[k])/yvaluesLorenz[len(yvaluesLorenz)-1])
##        Plot first Lorenz curve
        r.plot(xvalues, yvaluesLorenz, xlab="(%)Authors",ylab="(%)Cumulative contribution", main="Cumulative Distribution Function", type="l", col=2)
##        Plot line of perfect equality
        r.lines(xvalues, xvalues)
##        Plot remaining Lorenz curves
        for set in self.dataList:
            yvalues=set.pop()
            yvalues.insert(0,0)
            aggSum=0
            for j in range(1, len(yvalues)):
                aggSum+=yvalues[j]
                yvalues[j]=aggSum
    ##        Calculate % of total contributions
            for k in range(len(yvalues)):
                yvalues[k]=100.0*(float(yvalues[k])/yvalues[len(yvalues)-1])
    ##        Plot first Lorenz curve
            r.lines(xvalues, yvalues)
##        Close graphic device
        r.dev_off()
        
#################################################
##CLASSES with GNU R
#################################################

class graphic2DR(graphicR):
    """
    A class for 2D graphics with GNU R
    """
    def __init__(self, filePath, dataPath):
        super(graphic2DR, self).__init__(filePath, dataPath)
        
    def createGraphic(self, filename, data, graphType, xlabst, ylabst, mainTitle):
        pass

class graphicHistogram(graphicR):
    """
    A class for histogram graphics
    """
    def __init__(self, filePath, dataPath):
##        This time, filename could be even an empty string
##        The names are created inside the method, and are fixed
##        Datalist must provide an array of values with the length of every page
        super(graphicHistogram, self).__init__(filePath, dataPath)
        
    def createGraphic(self, filename, data, graphType, xlabst, ylabst, mainTitle):
##    Call superclass method to check wheter selected graphType is supported or not
        super(graphicHistogram, self).createGraphic(filename, data, graphType)
        
##        Create histograms and additional files
        print "Creating histograms for ... "+self.filePath+self.filename+"\n"
##        Create a template with the script code to plot the histogram with GNU R
        scriptTemplate=string.Template("""
        # Script to plot the histogram of an array of values
        #Load library for Kurtosis and Skewness methods
        library(moments)
        # Read values from data file
        input=read.table("$dataFile")
        values=input[,1]
        # Calculate probability density function
        dens=density(values)
        # Plot histogram graph
        $dev("$plotFile$ext")
        histogram=hist(values, xlab="$xlb", probability=TRUE, ylab="$ylb", main="$mainT", ylim=range(0,max(dens$$y)))
        # Plot probability density function
        lines(dens)
        # Switch off graphic device
        dev.off()
        #Print out some useful values about the sample groups
        sink("$infoFile.info")
        #Summaries and fivenumbers
        print("Summary for $infoFile")
        print(summary(values))
        print("Tukey five numbers for $infoFile")
        print(fivenum(values))
        print("*************************")
        print("*************************")
        print("Skewness and Kurtosis coefficientes for $infoFile")
        print("Skewness")
        print(skewness(values))
        print("Kurtosis")
        print(kurtosis(values))
        print("*************************")
        print("*************************")
        sink()
        """)
##        Complete the script with accurate values
        script=scriptTemplate.safe_substitute(dataFile=self.dataPath+"histogram.data",\
        dev=self.graphDev,plotFile=self.filePath+self.filename,ext=self.graphExt, xlb=xlabst, ylb=ylabst, mainT=mainTitle)
        #######################################################
        #Print the GNU R script to a file
        f=open(self.filePath+"histogram.R",'w')
        f.write(script)
        f.close()
        #######################################################
        
        #Print to another file a list with article sizes to plot histograms
        f=open(self.dataPath+"histogram.data", 'w')
        #Get the dataset (only 1) and then the dataList (again, only 1)
        #When you make pop, there's no stop
        self.dataList=self.dataList.pop().pop()
        ##            Take log10 of article size to plot histogram
        for i in range(len(self.dataList)):
            if self.dataList[i]!=0:
                self.dataList[i]=math.log10(self.dataList[i])
        for value in self.dataList:
            f.write(str(value)+"\n")
        f.close()
        
        #CALL THE GNU R SCRIPT Histogram.R
        succ=os.system("R --vanilla < "+self.filePath+"histogram.R > debug_R")
        if succ==0:
            print "Histogram script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
class graphicECDF(graphicR):
    """
    A class to plot ECDF graphics
    """
    def __init__(self, filePath, dataPath):
##        This time, filename could be even an empty string
##        The names are created inside the method, and are fixed
##        Datalist must provide an array of values with the length of every page
        super(graphicECDF, self).__init__(filePath, dataPath)
        
    def createGraphic(self, filename, data, graphType):
##    Call superclass method to check wheter selected graphType is supported or not
        super(graphicECDF, self).createGraphic(filename, data, graphType)
        
##        Create histograms and additional files
        print "Creating ECDF for ... "+self.filePath+self.filename+"\n"
##        Create a template with the script code to plot the ECDF with GNU R
        scriptTemplate=string.Template("""
        # Script to plot the ECDF of an array of values
        # Read values from data file
        input=read.table("$dataFile")
        values=input[,1]
        # Plot ECDF graph
        $dev("$plotFile$ext")
        plot(ecdf(values), do.points=FALSE, verticals=TRUE)
        # Plot ECDF of normal distribution to compare
        x=seq(min(values), max(values), 0.1)
        lines(x, pnorm(x, mean=mean(values), sd=sd(values)),lty=3, col=2)
        # Switch off graphic device
        dev.off()
        """)
##        Complete the script with accurate values
        script=scriptTemplate.safe_substitute(dataFile=self.dataPath+"ECDF.data",\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt)
        #######################################################
        #Print the GNU R script to a file
        f=open(self.filePath+"ECDF.R",'w')
        f.write(script)
        f.close()
        #######################################################
        #Print to another file the array of values to plot the ECDF
        f=open(self.dataPath+"ECDF.data", 'w')
        #Get the dataset (only 1) and then the dataList (again, only 1)
        #When you make pop, there's no stop
        self.dataList=self.dataList.pop().pop()
        for value in self.dataList:
            f.write(str(value)+"\n")
        f.close()
        
        #CALL THE GNU R SCRIPT Histogram.R
        succ=os.system("R --vanilla < "+self.filePath+"ECDF.R > debug_R")
        if succ==0:
            print "ECDF script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
class graphicBoxplot(graphicR):
    """
    A class to plot Boxplot graphics
    """
    def __init__(self, filePath, dataPath):
##        This time, filename could be even an empty string
##        The names are created inside the method, and are fixed
##        Datalist must provide an array of values with the length of every page
        super(graphicBoxplot, self).__init__(filePath, dataPath)
        
    def createGraphic(self, filename, data, graphType):
##    Call superclass method to check wheter selected graphType is supported or not
        super(graphicBoxplot, self).createGraphic(filename, data, graphType)
        
##        Create histograms and additional files
        print "Creating Boxplot for ... "+self.filePath+self.filename+"\n"
##        Create a template with the script code to plot the ECDF with GNU R
        scriptTemplate=string.Template("""
        # Script to plot the ECDF of an array of values
        # Read values from data file
        input=read.table("$dataFile")
        values=input[,1]
        # Boxplot graph
        $dev("$plotFile$ext")
        boxplot(values)
        # Switch off graphic device
        dev.off()
        """)
##        Complete the script with accurate values
        script=scriptTemplate.safe_substitute(dataFile=self.dataPath+"Boxplot.data", \
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt)
        #######################################################
        #Print the GNU R script to a file
        f=open(self.filePath+"Boxplot.R",'w')
        f.write(script)
        f.close()
        #######################################################
        #Print to another file the array of values to plot the ECDF
        f=open(self.dataPath+"Boxplot.data", 'w')
        #Get the dataset (only 1) and then the dataList (again, only 1)
        #When you make pop, there's no stop
        self.dataList=self.dataList.pop().pop()
        for value in self.dataList:
            f.write(str(value)+"\n")
        f.close()
        
        #CALL THE GNU R SCRIPT Histogram.R
        succ=os.system("R --vanilla < "+self.filePath+"Boxplot.R > debug_R")
        if succ==0:
            print "Boxplot script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
    
class graphicSplitHist(graphicR):
    """
    A class to plot ECDF graphics
    """
    def __init__(self, filePath, dataPath):
##        This time, filename could be even an empty string
##        The names are created inside the method, and are fixed
##        Datalist must provide an array of values with the length of every page
        super(graphicSplitHist, self).__init__(filePath, dataPath)
        
    def createGraphic(self, filename, data, graphType, xlabst, ylabst, mainTitle):
##    Call superclass method to check wheter selected graphType is supported or not
        super(graphicSplitHist, self).createGraphic(filename, data, graphType)
        
##        Create histograms and additional files
        print "Creating split histograms for ... "+self.filePath+self.filename+"\n"
##        Create a template with the script code to plot the ECDF with GNU R
        scriptTemplate=string.Template("""
        # Script to plot the ECDF of an array of values
        # Read values from data file
        input=read.table("$dataFile")
        values=input[,1]
        # Plot histogram and probability density for aggregate data
        $dev("$plotFile$ext")
        dens=density(values)
        histogram=hist(values, xlab="$xlb", probability=TRUE, ylab="$ylb", main="$mainT", ylim=range(0,max(dens$$y)))
        lines(dens)
        #Subdivide values in two samples groups, based on histogram info
        #First we focus split area
        resume=summary(histogram$mids)
        # We focus between the 1st quartile and the median
        q1=resume["1st Qu."]
        q2=resume["Median"]
        # We take density values falling into the focus zone
        focus_mids=histogram$mids[q1<histogram$mids & histogram$mids<q2]
        focus_dens=histogram$density[q1<histogram$mids & histogram$mids<q2]
        # And determine the cut point of both populations from the density of probability
        cutpoint_dens=min(focus_dens)
        cutpoint_mids=focus_mids[focus_dens==cutpoint_dens]
        # Split the values in 2 subpopulations
        values_low=values[values<cutpoint_mids]
        values_high=values[values>=cutpoint_mids]
        # Go on with each population independently
        #Print histogram for the lower group of samples
        $dev("$plotFileLow$ext")
        dens=density(values_low)
        hist(values_low, xlab="$xlb", probability=TRUE, ylab="$ylb", main="$mainT (Lower Half)", ylim=range(0,max(dens$y)))
        lines(dens)
        dev.off()
        #Same for the upper group of samples
        $dev("$plotFileHigh$ext")
        dens=density(values_high)
        hist(values_high, xlab="$xlb", probability=TRUE, ylab="$ylb", main="$mainT (Higher half)", ylim=range(0,max(dens$y)))
        lines(dens)
        # Switch off graphic device
        dev.off()
        """)
##        Complete the script with accurate values
        script=scriptTemplate.safe_substitute(dataFile=self.dataPath+"SplitHist.data", \
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt, xlb=xlabst, ylb=ylabst, mainT=mainTitle,\
        plotFileLow=self.filePath+self.filename+"_low_population", plotFileHigh=self.filePath+self.filename+"_high_population")
        #######################################################
        #Print the GNU R script to a file
        f=open(self.filePath+"SplitHist.R",'w')
        f.write(script)
        f.close()
        #######################################################
        #Print to another file the array of values to plot the ECDF
        f=open(self.dataPath+"SplitHist.data", 'w')
        #Get the dataset (only 1) and then the dataList (again, only 1)
        #When you make pop, there's no stop
        self.dataList=self.dataList.pop().pop()
        ##            Take log10 of article size to plot histogram
        for i in range(len(self.dataList)):
            if self.dataList[i]!=0:
                self.dataList[i]=math.log10(self.dataList[i])
        for value in self.dataList:
            f.write(str(value)+"\n")
        f.close()
        
        #CALL THE GNU R SCRIPT Histogram.R
        succ=os.system("R --vanilla < "+self.filePath+"SplitHist.R > debug_R")
        if succ==0:
            print "SplitHist script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
##########################################
##CLASSES with Gnuplot
##########################################

class graphic3D(graphicGnuplot):
    """
    A class for 3D graphics
    """
    def __init__(self, filePath, dataPath):
##        This time, dataList should contain a two dimensional matrix
##        with values suitable to plot with Gnuplot
        super(graphic3D, self).__init__(filePath, dataPath)
        
    def createGraphic(self, filename, data, revPeriodDict, xlabst, ylabst, zlabst, mainTitle):
        """
        Plot matrix with aggregate revision values in Gnuplot
        Matrix is two dimensional, with a value for each position.
        Output it to a file suitable for being shown by gnuplot.
        Both absolute and normalized (by the number of revisons per period)
        matrices are produced.
        """
        self.revPeriodDict=revPeriodDict
        self.filename=filename
        self.data=data
        print "Creating 3D graphics for..."+self.filePath+self.filename+"\n"
        
##        Write matrix data to a file for Gnuplot to adquire them
        filehand = open(self.dataPath+"matrix3D.data", 'w')
        for x in range(0, len(self.data)-1):
            for y in range(0, len(self.data[x])-1):
                if (self.data[x,y]!=0):
                    filehand.write (str(x) + ' ' + str(y) + ' ' + str(self.data[x,y]) + '\n')
                else:
                    filehand.write (str(x) + ' ' + str(y) + ' ' + str(self.data[x,y]) + '\n')
            filehand.write ('\n')
            
        filehand.close()
        
        filehand = open(self.dataPath+ 'matrix3D-normal.data', 'w')
        for x in range(0, len(self.data)-1):
            for y in range(0, len(self.data[x])-1):
                if y in self.revPeriodDict:
                    revsNormalized = float(self.data[x,y]) / self.revPeriodDict[y]
                else:
                    revsNormalized = 0
                filehand.write (str(x) + ' ' + str(y) + ' ' \
                                + str(revsNormalized) \
                                + '\n')
            filehand.write ('\n')
            
        filehand.close()
        
##        Create Gnuplot script
        scriptTemplate=string.Template("""
        set terminal postscript color
        unset contour
        set pm3d
        set palette defined ( 0 "green", 1 "blue", 2 "orange", 3 "red" )
        unset surface
        set ticslevel 0
        set xlabel "$xlb"
        set ylabel "$ylb"
        set zlabel "$zlb"
        set out "$plotFile"
        set view 36,41
        splot "$dataFile" with lines
        set out "$plotFileNorm"
        set view 36,41
        splot "$dataFileNorm" with lines
        """)
        script=scriptTemplate.safe_substitute(xlb=xlabst, ylb=ylabst, zlb=zlabst, plotFile=self.filePath+self.filename+".eps",\
        plotFileNorm=self.filePath+self.filename+"-normal.eps", dataFile=self.dataPath+"matrix3D.data",\
        dataFileNorm=self.dataPath+"matrix3D-normal.data")
        #######################################################
        #Print the GNU R script to a file
        f=open(self.filePath+"graphic3D.gnuplot",'w')
        f.write(script)
        f.close()
        #######################################################
        #CALL THE Gnuplot SCRIPT graphic3D.gnuplot
        succ=os.system("gnuplot < "+self.filePath+"graphic3D.gnuplot > debug_gnuplot")
        if succ==0:
            print "graphic3D script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
