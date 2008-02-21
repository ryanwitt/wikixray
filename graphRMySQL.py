# coding=utf8
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

import os, string

class graphRMySQL(object):
    """
    Superclass for the rest of graphic classess using GNU R and the RMySQL library
    """
    
    def __init__(self,  filePath, dbname, dbuser, dbpass):
        """
            self.typeGraphs=Supported graphic types (png, jpg, eps, pdf)
            The minimum information we should provide:
            filePath: Path to where we store the graphic file
            filename: Name of the graphic file
            dbname: Name of the database we connect to
            dbuser: The user name we want to use to connect to the DB
            dbpass: The pass to enter the DB
            query: The query to the DB for retrieving the data we want to process
        """
        self.typeGraphs={"png":("png",".png"),"jpeg":("jpeg",".jpeg") ,\
        "eps":("postscript",".eps"),"pdf":("pdf",".pdf")}
        self.filePath=filePath
        self.dbname=dbname
        self.dbuser=dbuser
        self.dbpass=dbpass
        
    def createGraphic(self, filename, query, graphType):
        self.filename=filename
        self.query=query
        if graphType not in self.typeGraphs:
            print "Sorry, you chose an unsupported type of file.\n"
            return -1
        else:
            self.graphDev=self.typeGraphs[graphType][0]
            self.graphExt=self.typeGraphs[graphType][1]
        
    #TODO: READ IN BEGINNING PYTHON ABOUT ATTRIBUTES INSTEAD OF GET METHODS
    def getfilePath(self):
        return self.filePath
        
    def getfilename(self):
        return self.filename
        
    def getdbname(self):
        return self.dbname
        
    def getdbuser(self):
        return self.dbuser
        
    def getdbpass(self):
        return self.dbpass
        
    def getquery(self):
        return self.query
        
class plot2D(graphRMySQL):
    """
    Draw a 2D graph with R and RMySQL
    The query should return the x in the first column and the y in the second column
    or else, the y in the first column (then an ordinal vector will be created automatically for x)
    Avoid taking logarirthms of negative or 0 values!!
    """
    
    def __init__(self, filePath, dbname, dbuser, dbpass):
        super(plot2D,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot a 2D graph : by plot2D : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        #Now, we should check whether the results have only one column (y) or 2 columns (x,y)
        #And plot the 2D graph
        if (length(names(results))==1) {
        plot(x=${log1x}1:length(results[,1])${log2x}, 
        y=${log1y}results[,1]${log2y}, main="$mainT", xlab="${log1x}$xlb${log2x}", 
        ylab="${log1y}$ylb${log2y}", col="$col", 
        type="$atype", lty=$alty, lwd=$alwd, pch=$apch, cex=$acex)
        } else {
        plot(x=${log1x}results[,1]${log2x}, y=${log1y}results[,2]${log2y}, main="$mainT", 
        xlab="${log1x}$xlb${log2x}", ylab="${log1y}$ylb${log2y}", col="$col",
        type="$atype", lty=$alty, lwd=$alwd, pch=$apch, cex=$acex)
        }
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        
    def createGraphic(self, filename, query, graphType="eps", logx="", logy="",\
    xlabst="", ylabst="", mainTitle="Main Title", colour="blue", type="p",lty=1, lwd=1, pch=19, cex=1 ):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        graphType={"png","jpeg","eps","pdf"}
        logx, logy: Adjust log scale (and labels) if you want, automatically
            log types can be:{ "", "log", "log10"}
        xlabst, ylabst, mainTitle: Labels for the x axis, y axis and main title
        colour: Defalut to blue, it can also be one of palette()[n], with n=[1..8] or any other palette in GNU R
        type: "p" (points), "l" (lines), "b" (both), "h" (vertical lines), "s" (stair steps)
        lty: int indicating type of line; defaults to 1 (see ?par)
        lwd: int indicating line width; defaults to 1 (see ?par)
        pch: int indicating the point character (defaults to solid circle=19; see ?points)
        cex: Magnification ratio for the character point (defaults to no magnification=1)
        """
        super(plot2D, self).createGraphic(filename, query, graphType)
        self.xlabst=xlabst; self.ylabst=ylabst; self.mainTitle=mainTitle; self.colour=colour
        self.type=type; self.lty=lty; self.lwd=lwd; self.pch=pch; self.cex=cex
        self.logs={"":("",""), "log":("log(",")"), "log10":("log10(",")")}
        #Substitute received values in script template
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        question=self.query, log1x=self.logs[logx][0], log2x=self.logs[logx][1],\
        log1y=self.logs[logy][0], log2y=self.logs[logy][1],\
        mainT=self.mainTitle, xlb=self.xlabst, ylb=self.ylabst, col=self.colour,
        atype=self.type, alty=self.lty, alwd=self.lwd, apch=self.pch, acex=self.cex)
        #Print the GNU R script to a file
        f=open(self.filePath+"plot2D.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"plot2D.R > debug_R")
        if succ==0:
            print "Plot2D script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
class plot2Dmulti(graphRMySQL):
    """
    Create a 2D graph for multiple variables simultaneously
    You should ensure that the x axis (first column) has a wide enough range
    to represent the rest of columns in the y axis
    It is mandatory to retrieve the x var in the first column of the query
    Avoid taking logarirthms of neg or 0 values!!
    """
    
    def __init__(self,filePath, dbname, dbuser, dbpass):
        super(plot2Dmulti,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot a 2Dmulti graph : by plot2Dmulti : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        #Plot the first graph
        xmin=min(${log1x}results[,1]${log2x})
        xmax=max(${log1x}results[,1]${log2x})
        ymin=min(${log1y}results[,2:length(names(results))]${log2y})
        ymax=max(${log1y}results[,2:length(names(results))]${log2y})
        plot(x=${log1x}results[,1]${log2x}, y=${log1y}results[,2]${log2y}, main="$mainT", 
        xlab="${log1x}$xlb${log2x}", ylab="${log1y}$ylb${log2y}", col=palette()[1],
        type="$atype", lty=1, lwd=$alwd, pch=19, cex=$acex,
        xlim=c(xmin,xmax), ylim=c(ymin,ymax))
        #Plot remaining curves with lines(...)
        longitude=length(names(results))
        if (longitude>2) {
            for (i in 3:length(names(results))){
                lines(x=${log1x}results[,1]${log2x}, y=${log1y}results[,i]${log2y}, col=palette()[i-1],
                type="$atype", lty=i-1, lwd=$alwd, pch=17+i, cex=$acex)
            }
        }
        #Generate legend information
        legend(x="$alegend", legend=names(results)[2:longitude], col=palette()[1:(longitude-1)],
        lty=1:(longitude-1), pch=19+(0:(longitude-1)))
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        
    def createGraphic(self, filename, query, graphType="eps", logx="", logy="",\
    xlabst="", ylabst="", mainTitle="Main Title", legend="topleft", type="p",lwd=1, cex=1 ):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        graphType={"png","jpeg","eps","pdf"}
        logx, logy: Adjust log scale (and labels) if you want, automatically
            log types can be:{ "", "log", "log10"}
        xlabst, ylabst, mainTitle: Labels for the x axis, y axis and main title
        legend: Position of the legend square
            Allowed values are= "bottomright", "bottom", "bottomleft","left", 
            "topleft", "top", "topright", "right"
        Automatically selects one of palette()[n], with n=[1..8], in GNU R
        type: "p" (points), "l" (lines), "b" (both), "h" (vertical lines), "s" (stair steps)
        For lty selects sequentially from [1..6] (see ?par)
        lwd: int indicating line width; defaults to 1 (see ?par)
        For pch selects the point character from [19..25]  (solid circle=19; see ?points)
        """
        super(plot2Dmulti, self).createGraphic(filename, query, graphType)
        self.xlabst=xlabst; self.ylabst=ylabst; self.mainTitle=mainTitle; self.legend=legend
        self.type=type; self.lwd=lwd; self.cex=cex
        self.logs={"":("",""), "log":("log(",")"), "log10":("log10(",")")}
        #Substitute received values in script template
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        question=self.query, log1x=self.logs[logx][0], log2x=self.logs[logx][1],\
        log1y=self.logs[logy][0], log2y=self.logs[logy][1], alegend=self.legend,\
        mainT=self.mainTitle, xlb=self.xlabst, ylb=self.ylabst,
        atype=self.type, alwd=self.lwd, acex=self.cex)
        #Print the GNU R script to a file
        f=open(self.filePath+"plot2Dmulti.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"plot2Dmulti.R > debug_R")
        if succ==0:
            print "Plot2Dmulti script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
class plot2DmultiDB(graphRMySQL):
    """
    Object to plot several 2D lines in the same graph with datasets
    retrieved running the same query in different DBs.
    """
    def __init__(self,filePath, dbname, dbuser, dbpass):
        super(plot2DmultiDB,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot a 2Dmulti graph : by plot2DmultiDB : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Initialize list of DBs
        dblist=$dbn
        #Initialize languages names
        languages=$langs
        #Connect to the DBs
        for (dbn in dblist){
            dbconnlist=c(dbconnlist, dbConnect(dbDriver("MySQL"),dbname=dbn, user="$dbu",password="$dbp"))
        }
        #Fetch queries as data.frames
        for (con in dbconnlist){
            results=c(results, dbGetQuery(con,"$question"))
        }
        #Open graphic device
        $dev("$plotFile$ext")
        #Plot the first graph
        #Find adequate extreme values for x and y in all result sets
        xmin=min(${log1x}results[seq(1,length(resultlist),by=2)]${log2x})
        xmax=max(${log1x}results[seq(1,length(resultlist),by=2)]${log2x})
        ymin=min(${log1y}results[seq(2,length(resultlist),by=2)]${log2y})
        ymax=max(${log1y}results[seq(2,length(resultlist),by=2)]${log2y})
        plot(x=${log1x}results[1]${log2x}, y=${log1y}results[2]${log2y}, main="$mainT", 
        xlab="${log1x}$xlb${log2x}", ylab="${log1y}$ylb${log2y}", col=palette()[1],
        type="$atype", lty=1, lwd=$alwd, pch=19, cex=$acex,
        xlim=c(xmin,xmax), ylim=c(ymin,ymax))
        #Plot remaining curves with lines(...)
        for (i in seq(3, length(results), by=2)){
            lines(x=${log1x}results[i]${log2x}, y=${log1y}results[i+1]${log2y}, col=palette()[i-1],
            type="$atype", lty=i-1, lwd=$alwd, pch=17+i, cex=$acex)
        }
        #Generate legend information
        legnames=names(results)[seq(2, length(results), by=2)]
        for (i in 1:length(legnames)){
            legnames[i]=paste(languages[i],legnames[i])
        }
        legend(x="$alegend", legend=legnames, col=c(palette()[1], palette()[seq(2:(length(results)-1),by=2)]),
        lty=c(1, seq(2:(length(results)-1),by=2)), pch=c(19, 17+seq(3, (length(results)),by=2)) )
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        for (con in dbconnlist){
            dbDisconnect(con)
        }
        """)
        
    def createGraphic(self, filename, query, graphType="eps", logx="", logy="",\
    xlabst="", ylabst="", mainTitle="Main Title", legend="topleft", type="p",lwd=1, cex=1 ):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        graphType={"png","jpeg","eps","pdf"}
        logx, logy: Adjust log scale (and labels) if you want, automatically
            log types can be:{ "", "log", "log10"}
        xlabst, ylabst, mainTitle: Labels for the x axis, y axis and main title
        legend: Position of the legend square
            Allowed values are= "bottomright", "bottom", "bottomleft","left", 
            "topleft", "top", "topright", "right"
        Automatically selects one of palette()[n], with n=[1..8], in GNU R
        type: "p" (points), "l" (lines), "b" (both), "h" (vertical lines), "s" (stair steps)
        For lty selects sequentially from [1..6] (see ?par)
        lwd: int indicating line width; defaults to 1 (see ?par)
        For pch selects the point character from [19..25]  (solid circle=19; see ?points)
        """
        super(plot2DmultiDB, self).createGraphic(filename, query, graphType)
        self.xlabst=xlabst; self.ylabst=ylabst; self.mainTitle=mainTitle; self.legend=legend
        self.type=type; self.lwd=lwd; self.cex=cex
        self.logs={"":("",""), "log":("log(",")"), "log10":("log10(",")")}
        #Create list of DB names
        self.dblist="c("
        if (len(self.dbname)==1):
            self.dblist+=self.dbname[0]+")"
        else:
            for i in range(0, len(self.dbname)-2):
                self.dblist+=self.dbname[i]+","
            self.dblist+=self.dbname[-1]+")"
        #Extract langs from dblist
        self.langslist=[]
        for name in self.dbname:
            self.langslist.append(name.split('_')[1])
        self.langs="c("
        if (len(self.langlist)==1):
            self.langs+=self.langlist[0]+")"
        else:
            for i in range(0, len(self.langlist)-2):
                self.langs+=self.langlist[i]+","
            self.langs+=self.langlist[-1]+")"
        #Substitute received values in script template
        ###ACUERDATE DE METER LA LISTA DE NOMBRES DE DBSS!!!!!!
        self.script=self.scriptTemplate.safe_substitute(langs=self.langs, dbn=self.dblist,\
        dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        question=self.query, log1x=self.logs[logx][0], log2x=self.logs[logx][1],\
        log1y=self.logs[logy][0], log2y=self.logs[logy][1], alegend=self.legend,\
        mainT=self.mainTitle, xlb=self.xlabst, ylb=self.ylabst,
        atype=self.type, alwd=self.lwd, acex=self.cex)
        #Print the GNU R script to a file
        f=open(self.filePath+"plot2DmultiDB.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"plot2DmultiDB.R > debug_R")
        if succ==0:
            print "Plot2DmultiDB script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
class histogram(graphRMySQL):
    """
    Object to plot histograms in GNU R with RMySQL
    """
    def __init__(self,filePath, dbname, dbuser, dbpass):
        super(histogram,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot a histogram and density graph : by histogram : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        #Plot histogram (probabilities) and density function
        linedens=density(${log1}results[,1]${log2})
        hist(${log1}results[,1]${log2}, prob=T, ylim=c(0,max(linedens$$y)),
        xlab="$xlb", ylab="$ylb", main="$mainT")
        lines(linedens, col="$acol", lty=$alty, lwd=$alwd)
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        
    def createGraphic(self, filename, query, graphType="eps", log="",\
    xlabst="", ylabst="", mainTitle="Main Title", colour="blue",lty=1, lwd=1):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        graphType={"png","jpeg","eps","pdf"}
        log: Adjust log scale (and labels) if needed, automatically
            log types can be:{ "", "log", "log10"}
        xlabst, ylabst, mainTitle: Labels for the x axis, y axis and main title
        colour: Defalut to blue, it can also be one of palette()[n], with n=[1..8] or any other palette in GNU R
        lty: int indicating type of line; defaults to 1 (see ?par)
        lwd: int indicating line width; defaults to 1 (see ?par)
        """
        super(histogram, self).createGraphic(filename, query, graphType)
        self.xlabst=xlabst; self.ylabst=ylabst; self.mainTitle=mainTitle;
        self.colour=colour; self.lty=lty; self.lwd=lwd
        self.logs={"":("",""), "log":("log(",")"), "log10":("log10(",")")}
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        question=self.query, log1=self.logs[log][0], log2=self.logs[log][1],\
        mainT=self.mainTitle, xlb=self.xlabst, ylb=self.ylabst,
        acol=self.colour, alty=self.lty, alwd=self.lwd)
        #Print the GNU R script to a file
        f=open(self.filePath+"histogram.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"histogram.R > debug_R")
        if succ==0:
            print "Histogram script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
class boxplot(graphRMySQL):
    """
    Object to create boxplots in GNU R with RMySQL
    """
    def __init__(self,filePath, dbname, dbuser, dbpass):
        super(boxplot,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to create a boxplot : by boxplot : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        #Draw the boxplot of the list of results
        boxplot(${log1}results${log2}, names=names(results), main="$mainT", col="$acol")
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        
    def createGraphic(self, filename, query, graphType="eps",log="",\
    mainTitle="Main Title", colour="blue"):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        log: Take the log of the set of results
            log types can be:{ "", "log", "log10"}
        graphType={"png","jpeg","eps","pdf"}
        mainTitle: Label for the main title
        colour: Defalut to blue, it can also be one of palette()[n], with n=[1..8] or any other palette or valid colour in GNU R
        """
        super(boxplot, self).createGraphic(filename, query, graphType)
        self.logs={"":("",""), "log":("log(",")"), "log10":("log10(",")")}
        self.mainTitle=mainTitle; self.colour=colour
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        question=self.query, log1=self.logs[log][0], log2=self.logs[log][1],\
        mainT=self.mainTitle, acol=self.colour)
        #Print the GNU R script to a file
        f=open(self.filePath+"boxplot.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"boxplot.R > debug_R")
        if succ==0:
            print "Boxplot script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
    
class plotBar(graphRMySQL):
    pass
    
class ECDF(graphRMySQL):
    """
    Object to create Script to plot the ECDF of a sequence of values along with the ECDF of normal distribution
    with GNU R and the RMySQL library
    """
    def __init__(self,filePath, dbname, dbuser, dbpass):
        super(ECDF,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot the ECDF of a sequence of values along with the ECDF of normal distribution
        #: by ecdf : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        #Draw the boxplot of the list of results
        par(col="$acolf", lty=$alty, lwd=$alwd, pch=$apch, cex=$acex)
        plot(ecdf(${log1}results[,1]${log2}), do.points=FALSE, verticals=TRUE)
        # Plot ECDF of normal distribution to compare
        x=seq(min(${log1}results[,1]${log2}), max(${log1}results[,1]${log2}), 0.1)
        lines(x, pnorm(x, mean=mean(${log1}results[,1]${log2}), sd=sd(${log1}results[,1]${log2})),lty=$alty+2, col="$acoln")
        legend(x="topleft", legend=c(paste("${log1}",names(results),"${log2}"), "normal distrib."), lty=c($alty, $alty+2), col=c("$acolf", "$acoln") )
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        
    def createGraphic(self, filename, query, graphType="eps",log="",\
    colourf="black", colourn="red", lty=1, lwd=1, pch=19, cex=1):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        log: Take the log of the set of results
            log types can be:{ "", "log", "log10"}
        graphType={"png","jpeg","eps","pdf"}
        colour: Defalut to blue, it can also be one of palette()[n], with n=[1..8] or any other palette or valid colour in GNU R
        """
        super(ECDF, self).createGraphic(filename, query, graphType)
        self.logs={"":("",""), "log":("log(",")"), "log10":("log10(",")")}
        self.colourf=colourf; self.colourn=colourn;self.lty=lty; self.lwd=lwd; self.pch=pch; self.cex=cex
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        question=self.query, log1=self.logs[log][0], log2=self.logs[log][1],\
        acolf=self.colourf, acoln=self.colourn, alty=self.lty, alwd=self.lwd, apch=self.pch, acex=self.cex)
        #Print the GNU R script to a file
        f=open(self.filePath+"ecdf.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"ecdf.R > debug_R")
        if succ==0:
            print "Ecdf script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
    
class Gini(graphRMySQL):
    """
    Object to create Lorenz curve and Gini coeff. with GNU R and the RMySQL library
    """
    def __init__(self,filePath, dbname, dbuser, dbpass):
        super(Gini,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot the Lorenz curve and Gini coeff
        #: by Gini : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        #Calculate values for Gini formula
        ord_count=c(0.0, sort(results[,2]))
        recv=c(0, c(1:length(results[,1])))
        sum_count=cumsum(ord_count);
        sum_recv=cumsum(recv)
        perc_count=(sum_count/max(sum_count))*100;
        perc_recv=(sum_recv/max(sum_recv))*100;
        numerator=perc_recv-perc_count
        numerator=sum(numerator);
        denominator=sum(perc_recv)-100;
        coef_gini = numerator/denominator
        #Plot Lorenz curve, line of perfect equality and Gini coeff (in legend) 
        plot(perc_recv,perc_count, main="$mainT", xlab="$xlb", ylab="$ylb",
        col="blue", lty=$alty, lwd=$alwd, type="l")
        lines(range(perc_recv), range(perc_count),col="black", lwd=$alwd); grid()
        legend(x="topleft", legend= c("Lorenz curve", "Perf. equality", paste("Gini coeff. =", round(coef_gini,5))),
        lty=c($alty, 1), col=c("blue", "black"), lwd=c($alwd, $alwd))
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        
    def createGraphic(self, filename, query, graphType="eps", xlabst="", ylabst="",\
    mainTitle="", lty=1, lwd=1):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        It is mandatory that the first column must be the recieving param .(users, pages, etc.) and the second column the count
        of the distributed param. (edits, contrib_len, etc.)
        log: Take the log of the set of results
            log types can be:{ "", "log", "log10"}
        graphType={"png","jpeg","eps","pdf"}
        colour: Defalut to blue, it can also be one of palette()[n], with n=[1..8] or any other palette or valid colour in GNU R
        """
        super(Gini, self).createGraphic(filename, query, graphType)
        self.mainTitle=mainTitle;self.lty=lty; self.lwd=lwd; self.xlabst=xlabst; self.ylabst=ylabst
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        question=self.query,mainT=self.mainTitle, alty=self.lty, alwd=self.lwd, xlb=self.xlabst, ylb=self.ylabst)
        #Print the GNU R script to a file
        f=open(self.filePath+"gini.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"gini.R > debug_R")
        if succ==0:
            print "Gini script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
    
class Ginimulti(graphRMySQL):
    """
    A class to generate Lorenz curves and Gini coeffs. in the same plot for different
    parameters within the same DB
    """
    def __init__(self,filePath, dbname, dbuser, dbpass):
        super(Ginimulti,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot several Lorenz curves and Gini coeffs in the same graph
        #: by Ginimulti : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        #Calculate vaules for Gini formula
        recv=c(0, c(1:length(results[,1])))
        sum_recv=cumsum(recv)
        perc_recv=(sum_recv/max(sum_recv))*100;
        for (i in 2:length(results)) {
            ord_count=c(ord_count, c(0.0, sort(results[,2])))
        }
        for (count in ord_count) {
            count=cumsum(count)
            count=count/max(count))*100
        }
        for (count in ord_count) {
            numerators=c(numerators, sum(perc_recv-count))
        }
        denominator=sum(perc_recv)-100;
        coefs_gini = numerators/denominator
        #Plot Lorenz curves, line of perfect equality and Gini coeffs (in legend)
        plot(range(perc_recv),range(ord_count[1]), main="$mainT", xlab="$xlb", ylab="$ylb",
        col="blue", lty=$alty, lwd=$alwd, type="l")
        for (count in ord_count) {
            lines(perc_recv, count, col="black", lwd=$alwd); grid()
        }
        ########################################################
        ## Me falta sacar bien los textos de la leyenda
        ########################################################
        legend(x="topleft", legend= c("Lorenz curve", "Perf. equality", paste("Gini coeff. =", round(coef_gini,5))),
        lty=c($alty, 1), col=c("blue", "black"), lwd=c($alwd, $alwd))
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        
    def createGraphic(self, filename, query, graphType="eps", xlabst="", ylabst="",\
    mainTitle="", lty=1, lwd=1):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        It is mandatory that the first column must be the recieving param .(users, pages, etc.) and the second column the count
        of the distributed param. (edits, contrib_len, etc.)
        log: Take the log of the set of results
            log types can be:{ "", "log", "log10"}
        graphType={"png","jpeg","eps","pdf"}
        colour: Defalut to blue, it can also be one of palette()[n], with n=[1..8] or any other palette or valid colour in GNU R
        """
        super(Ginimulti, self).createGraphic(filename, query, graphType)
        self.mainTitle=mainTitle;self.lty=lty; self.lwd=lwd; self.xlabst=xlabst; self.ylabst=ylabst
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        question=self.query,mainT=self.mainTitle, alty=self.lty, alwd=self.lwd, xlb=self.xlabst, ylb=self.ylabst)
        #Print the GNU R script to a file
        f=open(self.filePath+"ginimulti.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"ginimulti.R > debug_R")
        if succ==0:
            print "Ginimulti script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            

class GinimultiDB(graphRMySQL):
    """
    Same as previous one but for data retrieved with the same query executed in
    different DBs
    """
    pass

class scatterplot(graphRMySQL):
    """
    Scatterplot of two or multiple vars
    """
    def __init__(self,filePath, dbname, dbuser, dbpass):
        super(scatterplot,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot the correlation graph and Pearson corr. coeff. for two variables
        #: by PearsonCor : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        #Plot the graphs
        plot(results, main="$mainT",  col="navy")
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        
    def createGraphic(self, filename, query, graphType="eps",log=""):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        log: Take the log of the set of results
            log types can be:{ "", "log", "log10"}
        graphType={"png","jpeg","eps","pdf"}
        colour: Defalut to blue, it can also be one of palette()[n], with n=[1..8] or any other palette or valid colour in GNU R
        """
        super(scatterplot, self).createGraphic(filename, query, graphType)
        self.logs={"":("",""), "log":("log(",")"), "log10":("log10(",")")}
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        question=self.query, log1=self.logs[log][0], log2=self.logs[log][1])
        #Print the GNU R script to a file
        f=open(self.filePath+"scatterplot.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"scatterplot.R > debug_R")
        if succ==0:
            print "Scatterplot script sucessfully executed... "+self.filePath+self.filename+"\n\n"
         

class PearsonCor(graphRMySQL):
    """
    Plot correlation graph and display Pearson correlation coeff for two variables
    corr. coeff. method could be one of = ("Pearson", "Kendall", "Spearman")
    na.rm=True will delete NAs before computation
    """
    def __init__(self,filePath, dbname, dbuser, dbpass):
        super(PearsonCor,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot the correlation graph and Pearson corr. coeff. for two variables
        #: by PearsonCor : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        #Plot the scatterplot, then display the correlation coeff
        plot(x=${log1x}results[,1]${log2x}, y=${log1y}results[,2]${log2y}, main="$mainT", 
        xlab="${log1x}$xlb${log2x}", ylab="${log1y}$ylb${log2y}", col="$col",
        type="$atype", lty=$alty, lwd=$alwd, pch=$apch, cex=$acex)
        abline(v=mean(range(results[,1])), untf=FALSE, lty=2, col="red")
        abline(h=mean(range(results[,2])), untf=FALSE, lty=2, col="red")
        legend(x="topleft",
        legend=c("$meth", paste("Cor. coeff = ", 
        round(cor(${log1x}results[,1]${log2x}, ${log1y}results[,2]${log2y}, method="$meth", na.rm=$nrm),5))))
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        
    def createGraphic(self, filename, query, graphType="eps",log="",\
    colour="navy", method="Pearson", narm="True", lty=1, lwd=1, pch=19, cex=1):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        log: Take the log of the set of results
            log types can be:{ "", "log", "log10"}
        graphType={"png","jpeg","eps","pdf"}
        colour: Defalut to blue, it can also be one of palette()[n], with n=[1..8] or any other palette or valid colour in GNU R
        Six additional plots  are currently created: a plot
        of residuals against fitted values, a Scale-Location plot of
        sqrt{| residuals |} against fitted values, a Normal Q-Q plot, a
        plot of Cook's distances versus row labels, a plot of residuals
        against leverages, and a plot of Cook's distances against
        leverage/(1-leverage).  By default, the first three and '5' are
        provided.
        """
        super(PearsonCor, self).createGraphic(filename, query, graphType)
        self.method=method; self.narm=narm
        self.logs={"":("",""), "log":("log(",")"), "log10":("log10(",")")}
        self.colour=colour;self.lty=lty; self.lwd=lwd; self.pch=pch; self.cex=cex
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        meth=self.method, nrm=self.narm,\
        question=self.query, log1=self.logs[log][0], log2=self.logs[log][1],\
        col=self.colour, alty=self.lty, alwd=self.lwd, apch=self.pch, acex=self.cex)
        #Print the GNU R script to a file
        f=open(self.filePath+"PearsonCor.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"PearsonCor.R > debug_R")
        if succ==0:
            print "PearsonCor script sucessfully executed... "+self.filePath+self.filename+"\n\n"
            
class linearModel(graphRMySQL):
    def __init__(self, filePath, dbname, dbuser, dbpass):
        super(linearModel,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot a 2D graph : by plot2D : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        #Plot the linear fit and display params
        fit=lm(${log1y}$fooy${log2y}~${log1x}$foox${log2x})
        plot(x=${log1x}results[,1]${log2x}, y=${log1y}results[,2]${log2y}, main="$mainT", 
        xlab="${log1x}$xlb${log2x}", ylab="${log1y}$ylb${log2y}", col="$col",
        type="$atype", lty=$alty, lwd=$alwd, pch=$apch, cex=$acex)
        abline(fit)
        legend(x="topleft", legend=c(paste("Intercept = ", coef(fit)[1]), paste("Slope = ", coef(fit)[2])) )
        #Close graphic device
        dev.off()
        #Plot the six additional graphs
        $dev("$plotFile_resudials_vs_fitted$ext")
        plot.lm(fit, which=1)
        dev.off()
        $dev("$plotFile_normal_qq$ext")
        plot.lm(fit, which=2)
        dev.off()
        $dev("$plotFile_scale_location$ext")
        plot.lm(fit, which=3)
        dev.off()
        $dev("$plotFile_cooks_distance$ext")
        plot.lm(fit, which=4)
        dev.off()
        $dev("$plotFile_residuals_vs_leverage$ext")
        plot.lm(fit, which=5)
        dev.off()
        $dev("$plotFile_cooks_dist_vs_leverage$ext")
        plot.lm(fit, which=6)
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        
    def createGraphic(self, filename, query, graphType="eps", logx="", logy="",\
    xlabst="", ylabst="", mainTitle="Main Title", colour="blue", type="p",lty=1,\
    vary="results[,2]", varx="results[,1]", lwd=1, pch=19, cex=1 ):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        graphType={"png","jpeg","eps","pdf"}
        logx, logy: Adjust log scale (and labels) if you want, automatically
            log types can be:{ "", "log", "log10"}
        xlabst, ylabst, mainTitle: Labels for the x axis, y axis and main title
        colour: Defalut to blue, it can also be one of palette()[n], with n=[1..8] or any other palette in GNU R
        type: "p" (points), "l" (lines), "b" (both), "h" (vertical lines), "s" (stair steps)
        lty: int indicating type of line; defaults to 1 (see ?par)
        lwd: int indicating line width; defaults to 1 (see ?par)
        pch: int indicating the point character (defaults to solid circle=19; see ?points)
        cex: Magnification ratio for the character point (defaults to no magnification=1)
        """
        super(linearModel, self).createGraphic(filename, query, graphType)
        self.xlabst=xlabst; self.ylabst=ylabst; self.mainTitle=mainTitle; self.colour=colour
        self.type=type; self.lty=lty; self.lwd=lwd; self.pch=pch; self.cex=cex
        self.logs={"":("",""), "log":("log(",")"), "log10":("log10(",")")}
        self.vary=vary; self.varx=varx
        #Substitute received values in script template
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        fooy=self.vary, foox=self.varx,\
        question=self.query, log1x=self.logs[logx][0], log2x=self.logs[logx][1],\
        log1y=self.logs[logy][0], log2y=self.logs[logy][1],\
        mainT=self.mainTitle, xlb=self.xlabst, ylb=self.ylabst, col=self.colour,
        atype=self.type, alty=self.lty, alwd=self.lwd, apch=self.pch, acex=self.cex)
        #Print the GNU R script to a file
        f=open(self.filePath+"linearModel.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"linearModel.R > debug_R")
        if succ==0:
            print "LinearModel script sucessfully executed... "+self.filePath+self.filename+"\n\n"
        
    
class plotTS(graphRMySQL):
    def __init__(self, filePath, dbname, dbuser, dbpass):
        super(plotTS,self).__init__(filePath, dbname, dbuser, dbpass)
        #Define the script template
        self.scriptTemplate=string.Template("""
        #Script to plot a 2D graph : by plot2D : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="$dbn",user="$dbu",password="$dbp")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"$question")
        #Open graphic device
        $dev("$plotFile$ext")
        series=ts(${log1y}$var${log2y}, frequency=$frec, start=c$strt)
        plot(series, main="$mainT", 
        ylab="${log1y}$ylb${log2y}", col="$col",
        type="$atype", lty=$alty, lwd=$alwd, pch=$apch, cex=$acex)
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        """)
        #######################################
    def createGraphic(self, filename, query, graphType="eps", logx="", logy="",\
    xlabst="", ylabst="", mainTitle="Main Title", colour="blue", type="p",lty=1, lwd=1, pch=19, cex=1 ):
        """
        Actually creates the script file and executes it
        filename: Name of the graphic file
        query: The query to retrieve de data we want to plot
        graphType={"png","jpeg","eps","pdf"}
        logx, logy: Adjust log scale (and labels) if you want, automatically
            log types can be:{ "", "log", "log10"}
        xlabst, ylabst, mainTitle: Labels for the x axis, y axis and main title
        colour: Defalut to blue, it can also be one of palette()[n], with n=[1..8] or any other palette in GNU R
        type: "p" (points), "l" (lines), "b" (both), "h" (vertical lines), "s" (stair steps)
        lty: int indicating type of line; defaults to 1 (see ?par)
        lwd: int indicating line width; defaults to 1 (see ?par)
        pch: int indicating the point character (defaults to solid circle=19; see ?points)
        cex: Magnification ratio for the character point (defaults to no magnification=1)
        """
        super(plotTS, self).createGraphic(filename, query, graphType)
        self.xlabst=xlabst; self.ylabst=ylabst; self.mainTitle=mainTitle; self.colour=colour
        self.type=type; self.lty=lty; self.lwd=lwd; self.pch=pch; self.cex=cex
        self.logs={"":("",""), "log":("log(",")"), "log10":("log10(",")")}
        #Substitute received values in script template
        self.script=self.scriptTemplate.safe_substitute(dbn=self.dbname, dbu=self.dbuser, dbp=self.dbpass,\
        dev=self.graphDev, plotFile=self.filePath+self.filename, ext=self.graphExt,\
        question=self.query, log1x=self.logs[logx][0], log2x=self.logs[logx][1],\
        log1y=self.logs[logy][0], log2y=self.logs[logy][1],\
        mainT=self.mainTitle, xlb=self.xlabst, ylb=self.ylabst, col=self.colour,
        atype=self.type, alty=self.lty, alwd=self.lwd, apch=self.pch, acex=self.cex)
        #Print the GNU R script to a file
        f=open(self.filePath+"plotTS.R",'w')
        f.write(self.script)
        f.close()
        #Executre R script
        succ=os.system("R --vanilla < "+self.filePath+"plotTS.R > debug_R")
        if succ==0:
            print "PlotTS script sucessfully executed... "+self.filePath+self.filename+"\n\n"
        
    
class plot3D(graphRMySQL):
    pass

#TODO: IMPLEMENTAR FUNCIONES QUE SAQUEN PARTIDO DE LAS REGRESIONES
#CHAP 10 UsingR    
    
#TODO: Q-Q PLOTS!!!!!
#TODO: Plot.ts()
#TODO: plot(stl(x,window="?"))
#TODO: fit<-StructTS()+tsdiag(fit)
#TODO: tsSmooth()

#dibujo=Gini("","wx_glwiki_research","pepito","fenix")
#dibujo.createGraphic("prueba", "SELECT rev_id, (ABS(contrib_len))/1024 FROM articles_glwiki_contrib_len",\
#mainTitle="Test Gini", xlabst="Cumulative % of users", ylabst="Cum. distrib. (%) of ABS(contrib_len) (KiB)")


    
    
