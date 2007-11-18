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
This module contains a class implementing different quantitative analyses.
You should create a singleton method to undertake the analyses.
The implementing approach will change in the future to use Python plug-ins

@see: quantAnalay_main

@authors: Jose Felipe Ortega, Jesus M. Gonzalez-Barahona
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jfelipe@gsyc.escet.urjc.es
"""
from rpy import *
from graphics import *
import dbaccess, test_admins
import math, os, string, Numeric

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
