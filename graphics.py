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
            
        
###########################################
###########################################
##Graphical analysis
###########################################
class analysisPerformer:
    """
    Singleton class containing tasks and methods for a graphical quantitative analysis of each
    language version, using graphic objects
    """
    def __init__(self, language, graphType):
##        Create directory tree to store data results and graphics for this language
##        ./graphics/language for graphics and ./graphics/language/data for data files

        #FIX-ME RETOCAR SEGUN EL SCRIPT DE PYTHON PARA IBM
        self.language=language
        self.graphType=graphType
        directories=os.listdir("./")
        if ("graphics" not in directories):
            os.makedirs("./graphics")
        else:
            dir_lang=os.listdir("./graphics/")
            if self.language not in dir_lang:
                os.makedirs("./graphics/"+self.language+"/data")
                
##        Object attrs to point to graphics and data paths
        self.filePath="./graphics/"+self.language+"/"
        self.dataPath="./graphics/"+self.language+"/data/"
        
        # Dictionary with commits per period
        self.commitsPeriodDict = {}
        # Dictionary with commiters per period
        self.commitersPeriodDict = {}
        
    def performAnalysis(self):
        
##        Get DB connection
        self.acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", self.language+"_stub")
##        Singleton objects to plot graphics in the class methods
        self.simpleGraph=graphic2D(self.filePath)
##        self.multiGraph=graphic2Dmulti(self.filePath)
##        self.giniGraph=graphicGini(self.filePath)
##        self.splitHistGraph=graphicSplitHist(self.filePath, self.dataPath)
        self.graph3D=graphic3D(self.filePath, self.dataPath)
        print "Starting analysis on DB "+self.language+"_stub\n"
##        self.UserNumContribsGroup(self.acceso[1])
##        self.UserNumContribsGenerations()
        authorsGini=[(95.9677,4.046,),(95.7015,4.304),(96.2223,4.363),(95.7104,4.395),(96.3844,4.407),(92.4691,4.528),(95.0077,4.603),(95.0071,4.7298),(93.785,5.051),(93.6076,5.888)]
        authorsGini.sort()
        ##authorsGini=[(4.046,95.9677),(4.304,95.7015),(4.363,96.2223),(4.395,95.7104),(4.407,96.3844),(4.528,92.4691),(4.603,95.0077),(4.7298,95.0071),(5.051,93.785),(5.888,93.6076)]
        
        self.simpleGraph.createGraphic("authors-Gini", (authorsGini,), "Gini coeff. (%)","Number of different authors (log)", "Gini coeff. vs. number of registered authors in the top-ten Wikipedias.")
##            Close DB connection
        dbaccess.close_Connection(self.acceso[0])
        print "This is finished"
            
    ####################################################
    ## USERS
    ####################################################
    def UserNumContribsGini(self, cursor):
        """
        A class to perform analysis on contributions with Gini graphs
        """
##        Retrieve info from DB and plot Gini graph
        tcnoann=dbaccess.query_SQL(cursor, select=" * ", table="stats_Contrib_NoAnnons_author_"+self.language)
        giniGraph.createGraphic("Gini graph for "+self.language, (tcnoann,), self.graphType)
        
    def UserNumContribsCompGini(self, cursor, languages):
##        Retrieve info from DB and plot Gini comparative graph
        dataSeries=[]
        for language in languages:
            dataSeries.append(dbaccess.query_SQL(cursor,\
            select=" * ", table="stats_Contrib_NoAnnons_author_"+self.language))
        giniGraph.createGraphic("Gini_Comparative", dataSeries, self.graphType)
        
    def UserNumContribsGroup(self, cursor):
        """
        A class to plot comparative graphics with contributions from 
        different groups
        """
        ###Reproduction of the article Power of the few...
##        Admins and bots IDs can be retrieved from DB as subselects in the where clause
        ##########################
        ##Drop bots contribs from DB source view
        ##########################
        ##CREATE VIEW FOR PERIODS FROM 0 IN MONTHS
        minYear=dbaccess.query_SQL(cursor, select="MIN(year)",\
        tables="stats_Contrib_NoAnnons_months_author_"+self.language)
        
        minMonth=dbaccess.query_SQL(cursor, select="MIN(month)",\
        tables="stats_Contrib_NoAnnons_months_author_"+self.language,\
        where="year="+str(int(minYear[0][0])))
        
        dbaccess.createView(cursor, view="contribs_period_author_"+self.language,\
        columns="period, author, contribs",\
        query="SELECT ((year*12)+month-("+str(int(minYear[0][0]))+"*12)-"+str(int(minMonth[0][0]))\
        +") as period, author, theCount FROM "+\
        "stats_Contrib_NoAnnons_months_author_"+self.language+" WHERE author NOT IN "+\
        "(SELECT DISTINCT(ug_user) FROM user_groups WHERE ug_group='bot') ORDER BY period")
        
##        Retrieve number of revision made by admins per month
        revsAdminsPerMonth=dbaccess.query_SQL(cursor,select="period, SUM(contribs)",\
        tables="contribs_period_author_"+self.language,\
        where="author IN (SELECT ug_user FROM user_groups where ug_group='sysop')",\
        group="period",order="period")
##        Plot FIG 2
        self.simpleGraph.createGraphic("revs_admins_per_month", (revsAdminsPerMonth,),\
        xlabst="Months", ylabst="Revisions",mainTitle="Revisions per month for admins "+\
        self.language, graphType=self.graphType, log=False)
        
        contribsMonth=dbaccess.query_SQL(cursor,\
        select="period, SUM(contribs)",\
        tables="contribs_period_author_"+self.language,\
        group="period",order="period")
        
##        divide element by element
##        Supposedly, there is at least one rev per month made by an admin
        percContribsAdmins=[]
        for totAdminContrib in revsAdminsPerMonth:
            for totContrib in contribsMonth:
                if totAdminContrib[0]==totContrib[0]:
##            append (period, adminsContribs/totContribs)
                    perc=float(totAdminContrib[1])/float(totContrib[1])
                    percContribsAdmins.append((totAdminContrib[0],perc*100))
                    break
##        Plot FIG 1 % of total revs per month made by admins
        self.simpleGraph.createGraphic("perc_revs_admins_per_month", (percContribsAdmins,),\
        xlabst="Months", ylabst="% revisions",\
        mainTitle="% of total revisions per month made by admins "+self.language,\
        graphType=self.graphType, log=False)
        
##    FIG 4 TOTAL EDITS MADE BY USERS WITH DIFFERENT EDIT LEVELS
##    CREATE WHERE CLAUSES FOR CLUSTER OF USERS IDENTIFIED BY CONTRIBUTIONS LEVEL
##    5 LEVELS: <100, 100-1K, 1K-5K, 5K-10K, >10K
        usersLevel1="author IN (SELECT DISTINCT(author) FROM stats_Contrib_NoAnnons_author_"+\
        self.language+" WHERE theCount<=100 AND author NOT IN "+\
        "(SELECT DISTINCT(ug_user) FROM user_groups WHERE ug_group='bot'))"
        usersLevel2="author IN (SELECT DISTINCT(author) FROM stats_Contrib_NoAnnons_author_"+\
        self.language+" WHERE theCount BETWEEN 101 AND 1000 AND author NOT IN" +\
        "(SELECT DISTINCT(ug_user) FROM user_groups WHERE ug_group='bot'))"
        usersLevel3="author IN (SELECT DISTINCT(author) FROM stats_Contrib_NoAnnons_author_"+\
        self.language+" WHERE theCount BETWEEN 1001 AND 5000 AND author NOT IN "+\
        "(SELECT DISTINCT(ug_user) FROM user_groups WHERE ug_group='bot'))"
        usersLevel4="author IN (SELECT DISTINCT(author) FROM stats_Contrib_NoAnnons_author_"+\
        self.language+" WHERE theCount BETWEEN 5001 AND 10000 AND author NOT IN "+\
        "(SELECT DISTINCT(ug_user) FROM user_groups WHERE ug_group='bot'))"
        usersLevel5="author IN (SELECT DISTINCT(author) FROM stats_Contrib_NoAnnons_author_"+\
        self.language+" WHERE theCount>10000 AND author NOT IN "+\
        "(SELECT DISTINCT(ug_user) FROM user_groups WHERE ug_group='bot'))"
        
##        Some vars used in for iterations
        levels=(usersLevel1, usersLevel2, usersLevel3, usersLevel4, usersLevel5)
        listContribsLevel=[]
        listAvgContribsLevel=[]
        listPercContribsLevel=[]
        listUsersLevel=[]
        listPercUsersLevel=[]
        
##        Retrieve tot num of users per month
        usersMonth=dbaccess.query_SQL(cursor,\
        select="period, COUNT(DISTINCT(author))",\
        tables="contribs_period_author_"+self.language,\
        group="period",order="period")
        
        for level in levels:
##            Retrieve contribs per month for this level
            contribsLevelMonth=dbaccess.query_SQL(cursor,\
            select="period, SUM(contribs)",\
            tables="contribs_period_author_"+self.language,\
            where=level, group="period", order="period")
            listContribsLevel.append(contribsLevelMonth)
            
            percContribsLevel=[]
##            Append (period, contribsLevel/totContribs) checking periods correspondence
            for totLevelContrib in contribsLevelMonth:
                for totContrib in contribsMonth:
                    if totLevelContrib[0]==totContrib[0]:
                        perc=float(totLevelContrib[1])/float(totContrib[1])
                        percContribsLevel.append((totLevelContrib[0],perc*100))
                        break
            listPercContribsLevel.append(percContribsLevel)
            
            ##            Retrieve number of users per level per month
            usersLevelMonth=dbaccess.query_SQL(cursor,\
            select="period, COUNT(DISTINCT(author))",\
            tables="contribs_period_author_"+self.language,\
            where=level, group="period",order="period")
            ##Append to the list of users per level per month
            listUsersLevel.append(usersLevelMonth)
            
            avgUsersLevel=[]
##            Retrieve avg number of revs per user in each group, per month
            for contribs in contribsLevelMonth:
                for totUsers in usersLevelMonth:
                    if contribs[0]==totUsers[0]:
                        avg=float(contribs[1])/float(totUsers[1])
                        avgUsersLevel.append((contribs[0],avg))
            listAvgContribsLevel.append(avgUsersLevel)
            
            percUsersLevel=[]
##            Append (period, usersLevel/totUsers)
            for users, totUsers in zip(usersLevelMonth, usersMonth):
                for totUsers in usersMonth:
                    if users[0]==totUsers[0]:
                        perc=float(users[1])/float(totUsers[1])
                        percUsersLevel.append((users[0],perc*100))
                        break
            listPercUsersLevel.append(percUsersLevel)
            
##        2D graph for FIG 4
        self.multiGraph.createGraphic("perc_revs_per_userlevel_month",\
        listPercContribsLevel, xlabst="months", ylabst="% revisions",\
        mainTitle="% of total revs per user level per month", graphType=self.graphType,\
        format=[],log=False)
        
##        Plot 2D multi graph (FIG 5)
        self.multiGraph.createGraphic("revs_per_userlevel_month",\
        listContribsLevel, xlabst="months", ylabst="revisions",\
        mainTitle="Total revisions per user level per month", graphType=self.graphType,\
        format=[],log=True)
        
##    FIG 6 AVERAGE NUMBER OF EDITS PER USER PER MONTH FOR EACH LEVEL
        self.multiGraph.createGraphic("avg_revs_per_userlevel_month",\
        listAvgContribsLevel, xlabst="months", ylabst="avg. revisions",\
        mainTitle="Avg revisions per user level per month", graphType=self.graphType,\
        format=[],log=True)
        
##        FIG 7 POPULATION GROWTH FOR EACH USER GROUP
        self.multiGraph.createGraphic("users_per_level_month",\
        listUsersLevel, xlabst="months", ylabst="log(num users)",\
        mainTitle="Growth of each user group per month", graphType=self.graphType,\
        format=[],log=True)
##        FIG 8 % OF TOTAL POPULATION OF EACH USER GROUP
        self.multiGraph.createGraphic("perc_users_per_level_month",\
        listPercUsersLevel, xlabst="months", ylabst="% users",\
        mainTitle="% of users in each user group per month", graphType=self.graphType,\
        format=[],log=False)
        
        """
        Possible targets:
            Groups by number of total contributions (same as Power of the Few)
            Same but with:
                active users (+5 edits/month)
                quite active (+25)
                very active (+100) (same as official statistics by Erik)
            Same but grouping users by their age:
                ancient (+3 years)
                young (+1 year)
                newbies (-1 year)
        """
    def UserNumContribsGenerations(self):
        """
        Same 3D study as in LibreSoftware
        """
        self.periodCommitsCommiter = \
        dbaccess.query_SQL(self.acceso[1],\
        select="period, author, contribs",\
        tables="contribs_period_author_"+self.language,\
        order="period, contribs DESC")
        self.lastPeriod = int (self.periodCommitsCommiter[-1][0])
        
        # Perform all the analysis
        print ('Performing analysis with period = months\n')
        #self.commitsPerPeriodPerCommiter()
        self.commitsPerPeriod()
        self.largestCommiters()
        self.topFractionCommits(0.1)
        #self.topFractionCommits(0.5)
        #self.topFractionCommits(1.0)
##        FIXME: repeat executions with different percentages
##        TODO: add periodified plotbars for topFractionCommiters
        self.topFractionCommiters(0.05)
        #self.topFractionCommiters(0.2)
        #self.topFractionCommiters(1.0)

    def commitsPerPeriodPerCommiter(self):

        """
        Print lines to a file, each line repesenting:
          period commiter commits
        """
        
        filehand = open(self.dataPath + 'commits_per_period_per_commiter', 'w')
        
        result = dbaccess.raw_query_SQL\
        (self.acceso[1], "select * from contribs_period_author_"+self.language)
        for row in result:
            # 0:period, 1:commiter, 2:commits
            filehand.write (row[0] + ' ' + row[1] + ' ' + row[2] + '\n')
            
        filehand.close()
        
    def commitsPerPeriod(self):
        
        """
        Print lines to a file, each line representing:
          period commits commiters
        Also, fills in self.commitsPeriodDict (commits per period)
        and self.commitersPeriodDict (commiters per period)
        """
        
        filehand = open(self.dataPath + 'data_per_period', 'w')

        # Commits per period, as an array of rows
        commitsPeriod = dbaccess.raw_query_SQL(self.acceso[1],\
        "select period, sum(contribs), count(DISTINCT(author))"+\
        " from contribs_period_author_"+self.language+" group by period")
        for row in commitsPeriod:
            # 0:period, 1:commits, 2: commiters
            filehand.write (str(row[0]) + ' ' + str(row[1]) + ' ' + str(row[2]) + '\n') 
            self.commitsPeriodDict [int(row[0])] = int(row[1])
            self.commitersPeriodDict [int(row[0])] = int(row[2])

    def largestCommiters(self):

        """
        Get, for each period, the largest commiter, and trace her
        history (commits in any other period)
        """
        
        print ('- Generating matrix for largest commiters')
        
        matrixSize = self.lastPeriod + 1
        matrixPeriods = Numeric.zeros((matrixSize,matrixSize))
        currentPeriod = - 1
        for row in self.periodCommitsCommiter:
            # 0:period, 1:commiter, 2:commits
            period = int (row[0])
            if period > currentPeriod:
                # This row corresponds to the largest commiter in a new period
                currentPeriod = period
                print "Computing period %d\n" % period
                commiter = row[1]
                self.commitsCommiterAllPeriods \
                  (commiter,
                   matrixPeriods[currentPeriod])
        # Now, write the 3D graph
        print ("Writing 3D graph for largest commiters")
        self.graph3D.createGraphic("largest_commiters_", matrixPeriods,self.commitsPeriodDict,\
        xlabst="period", ylabst="author", zlabst="log(revisions)", mainTitle="Largest authors"+\
        self.language)

    def topFractionCommits(self, fraction):

        """
        Get, for each period, the commiters producing the top fraction
        of the commits, and trace their history (commits in any other
        period for all of them)

        fraction should be between 0 and 1
        """

        print ('- Generating matrix for commiters producing ' + \
              'top fraction of commits (fraction: ' + \
              str (fraction)+")")
              
        matrixSize = self.lastPeriod + 1
        matrixPeriods = Numeric.zeros((matrixSize,matrixSize))
        currentPeriod = - 1
        commitersBars=[]
        thresholdBars=[]
        countCommiters=0
        catchThreshold=0
        for row in self.periodCommitsCommiter:
            # 0:period, 1:commiter, 2:commits
            period = int (row[0])
            commiter = row[1]
            if period > currentPeriod:
                # This row corresponds to a new period,
                #  init. values for new period
                currentPeriod = period
                append=True
                print "Computing period %d\n" % period
                if period > 0:
                    print "total commits period %d = %d" % ((period-1),currentCommits)
                currentCommits = 0
            if currentCommits < self.commitsPeriodDict[period] * fraction:
                # Still not all commiters wanted for this period,
                #   add this one
                currentCommits = currentCommits + int(row[2])
                countCommiters+=1
                catchThreshold=int(row[2])
                self.commitsCommiterAllPeriods \
                  (commiter,
                   matrixPeriods[currentPeriod])
            else:
                if append:
                    #Append bars=0:period,1:numberCommitters,2:commits_threshold
                    commitersBars.append([period,countCommiters])
                    thresholdBars.append([period,catchThreshold])
                    countCommiters=0
                    catchThreshold=0
                    append=False
        # Now, write the 3D graph
        print ("Writing 3D graph for top fraction commits")
        self.graph3D.createGraphic("authors_top-"+str(fraction)+"-contribs", matrixPeriods,\
        self.commitsPeriodDict, xlabst="period", ylabst="history (periods)", zlabst="log(revisions)",\
        mainTitle="Authors producing the top "+str(fraction)+" fraction of revisions."+\
        self.language)
        self.graphBars=graphicBar(self.filePath)
        self.graphBars.createGraphic("periodifying-authors-"+str(fraction)+"-contribs",(commitersBars,),\
        xlabst="period", ylabst="authors", mainTitle="Number of committers per period for the 10% per period")
        self.graphBars.createGraphic("periodifying-revisions-"+str(fraction)+"-contribs",(thresholdBars,),\
        xlabst="period", ylabst="authors", mainTitle="Min. num. of contributions for the top 10% per period")

    def topFractionCommiters(self, fraction):

        """
        Get, for each period, the top fraction of commiters, and
        trace their history (commits in any other period for all
        of them)

        fraction should be between 0 and 1
        """
        
        print ('- Generating matrix for top fraction of commiters ' + \
        '(fraction: ' + str (fraction) + ')')
               
        matrixSize = self.lastPeriod + 1
        matrixPeriods = Numeric.zeros((matrixSize,matrixSize))
        currentPeriod = - 1
        for row in self.periodCommitsCommiter:
            # 0:period, 1:commiter, 2:commits
            period = int (row[0])
            commiter = row[1]
            if period > currentPeriod:
                # This row corresponds to a new period,
                #  init. values for new period
                currentPeriod = period
                print "Analyzing period %d" % period
                if period > 0:
                    print "total commiters period %d=%d" % ((period-1), currentCommiters)
                currentCommiters = 0
            if currentCommiters < self.commitersPeriodDict[period] * fraction:
                # Still not all commiters wanted for this period,
                #   add this one
                currentCommiters = currentCommiters + 1
                self.commitsCommiterAllPeriods \
                  (commiter,
                   matrixPeriods[currentPeriod])
        # Now, write the 3D graph
        print ("Writing 3D graph for top fraction commiters")
        self.graph3D.createGraphic("top-"+str(fraction)+"-authors", matrixPeriods,\
        self.commitsPeriodDict, xlabst="period", ylabst="history (periods)",\
        zlabst="log(revisions)", mainTitle="Top "+str(fraction)+" fraction of authors"+\
        self.language)
        
    def commitsCommiterAllPeriods(self, commiter, arrayCommits):

        """
        Calculate the number of commits per period, for all periods,
        for a given commiter, and produce an add that information
        to the given arrayCommits (which should be zeroed before
        calling this function in case this is the first call to fill
        it in).
        """
        
        # print arrayCommits
        result = dbaccess.raw_query_SQL (self.acceso[1],\
        "select period, contribs from contribs_period_author_"+\
        self.language+" where author="+\
        str(commiter) + " group by period")
        for row in result:
            # 0:period, 1:commits
            period = int (row[0])
##            It is better for us to compute the log10(num-revisions) for low values to appear
            arrayCommits [period] = arrayCommits [period] + int(row[1])
        
    def UserSizeContribsGenerations(self, cursor):
        """
        Idem as the previous one, but with size of contribs instead of num of contribs
        """
        pass
        
    ####################################################
    ## ARTICLES
    ####################################################
    def articleNumContribsGini(self, cursor):
        """
        Gini graphics for the number of contributions received per article
        """
        pass
    def articleSizeContribsGini(self, cursor):
        pass
    def articleSizeHistogram(self, cursor):
        """
        Histogram for the size of articles and split in two subpopulations
        """
##        Retrive dataset with length of pages from DB
        pageLen=dbaccess.query_SQL(cursor, select="page_id, page_len", table="aux")
##        Plot aggregate histogram and split histograms for subpopulations
        splitHistGraph.createGraphic("Histogram", (pageLen,),"eps", xlabst="Page length (log)",\
        ylabst="Probability densities", mainTitle="Histogram for length of articles")
        
    def articleSizeHistogramEvol(self, cursor):
        pass

##langs=["dewiki", "frwiki", "plwiki", "jawiki", "nlwiki", "itwiki", "ptwiki", "svwiki", "eswiki"]
##langs=["enwiki"]
##for lang in langs:
performer=analysisPerformer("nlwiki", "png")
performer.performAnalysis()
performer=None
"""
def prueba():
##    t=((1,),(1,),(1,),(1,),(1,),(1,),(1,),(1,),(1,),(1,),(1,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(2,),(3,))
##    objeto=graphicHistogram("prueba","./pruebas/","./pruebas/data/", (t,))
##    objeto.createGraphic("png","etiqueta x", "etiqueta y", "TITULO")

    acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", "nlwiki_stub")
    tcnoann=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_NoAnnons_author_nlwiki")
##    Conversion to tuple of sets
##    PLEASE NOTICE THAT YOU CAN PASS EITHER TUPLES OR LISTS
##    EXAMPLES FOR Only one result (resultSet,) OR [resultSet]
    tcnoann=[tcnoann]
    print "Information retrieved, going on...\n"
    dbaccess.close_Connection(acceso[0])
    objeto=graphicBoxplot("pruebaGraphBox","./pruebas/","./pruebas/data/", tcnoann)
    objeto.createGraphic("png")
    
    ###Vigilar ECDF, parece que  todavia no plotea adecuadamente

prueba()
"""
