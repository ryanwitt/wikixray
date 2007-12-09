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
Creates additional database views,  
creating an adequate interface to access relevant quantitative data (including
evolution in time of important parameters).

@see: quantAnalay_main

@authors: Jose Felipe Ortega
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jfelipe@gsyc.escet.urjc.es
"""

import dbaccess, datetime

class dbanaly(object):
    def __init__(self, conf, language="furwiki"):
        """
        Creates multiple views to create a convenient interface to access quantitative data
        It also generates necessary tables and views to store intermidiate results, so that other methods
        can later store data directly. 
        """
        self.conf=conf
        self.language=language
        ##List of namespaces to analyse. We have added new special namespaces (e.g. subsets of main)
        self.nspaces=["all","ns0","articles","redirects","cur_redirects","cur_stubs","stubs","talk",\
        "pageUser", "userTalk","meta", "metaTalk", "image", "imageTalk", "mediawiki",\
        "mediawikiTalk", "template", "templateTalk", "help", "helpTalk", "category", "categoryTalk"]
        
        ##Some fancy lists to work with time intervals in some private methods following
        self.type_interval_columns={"days":"day, year", "weeks":"week, year", "months":"month, year",\
        "quarters":"quarter, year", "years":"year"}
        self.type_interval_select={"days":"DAYOFYEAR(rev_timestamp) AS day, YEAR(rev_timestamp) AS year ",\
        "weeks":"WEEK(rev_timestamp,1) AS week, YEAR(rev_timestamp) AS year ",\
        "months":"MONTH(rev_timestamp) AS month, YEAR(rev_timestamp) AS year ",\
        "quarters":"QUARTER(rev_timestamp) AS quarter, YEAR(rev_timestamp) AS year ",\
        "years":"YEAR(rev_timestamp) AS year "}
        self.type_interval_group={"days":"year, day", "weeks":"year, week", "months":"year, month",\
        "quarters":"year, quarter", "years":"year"}
        
        ##	Get new DB connection
        self.acceso = dbaccess.get_Connection("localhost", 3306, self.conf.msqlu, self.conf.msqlp,\
        "wx_"+self.language+"_"+self.conf.dumptype)
        
        ##    Delete previous versions of views
        for nspace in self.nspaces:
            dbaccess.dropView(self.acceso[1], nspace+"_"+self.language)
        
        ##    Create updated versions for views from revision table
        #View sumarizing all info for every revision (linking with info from table page)
        dbaccess.createView(self.acceso[1], view="all_"+self.language,\
        columns="rev_id, page_id, rev_len, page_ns, page_len, is_redirect, author, author_text,"+\
        " rev_timestamp, rev_parent_id",
        query="SELECT rev_id, rev_page, rev_len, page_namespace, page_len, rev_is_redirect,"+\
        " rev_user, rev_user_text, rev_timestamp, rev_parent_id FROM revision, page WHERE rev_page=page_id")
        #View sumarizing info regarding pages in namespace=0 (including articles, stubs and redirects)
        dbaccess.createView(self.acceso[1], view="ns0_"+self.language,\
        columns="rev_id, page_id, rev_len, page_len, page_title, is_redirect, author, author_text,"+\
        " rev_timestamp, rev_parent_id",
        query="SELECT rev_id, rev_page, rev_len, page_len, page_title, page_is_redirect, rev_user,"+\
        " rev_user_text, rev_timestamp, rev_parent_id FROM revision, page WHERE rev_page=page_id"+\
        " AND page_namespace=0")
        #View sumarizing info for articles (excluding pages that currently are redirects and stubs)
        dbaccess.createView(self.acceso[1], view="articles_"+self.language,\
        columns="rev_id, page_id, rev_len, page_len, page_title, author, author_text, rev_timestamp, "+\
        "rev_parent_id",
        query="SELECT rev_id, rev_page, rev_len, page_len, page_title, rev_user, rev_user_text,"+\
        " rev_timestamp, rev_parent_id FROM revision, page WHERE rev_page=page_id AND page_namespace=0 AND "+\
        "page_is_redirect=0 AND page_is_stub=0")
        #View with info only for redirects (pages that were redirects when that revision was made)
        dbaccess.createView(self.acceso[1], view="redirects_"+self.language,\
        columns="rev_id, page_id, rev_len, page_len, page_title, author, author_text, rev_timestamp, "+\
        "rev_parent_id",
        query="SELECT rev_id, rev_page, rev_len, page_len, page_title, rev_user, rev_user_text, "+\
        "rev_timestamp, rev_parent_id FROM revision, page WHERE rev_page=page_id AND "+\
        "page_namespace=0 AND rev_is_redirect=1")
        #View with info only for current redirects
        dbaccess.createView(self.acceso[1], view="cur_redirects_"+self.language,\
        columns="rev_id, page_id, rev_len, page_len, page_title, author, author_text, rev_timestamp, "+\
        "rev_parent_id",
        query="SELECT rev_id, rev_page, rev_len, page_len, page_title, rev_user, rev_user_text, "+\
        "rev_timestamp, rev_parent_id FROM revision, page WHERE rev_page=page_id AND "+\
        "page_namespace=0 AND page_is_redirect=1")
        #View with info only for revisions of stub pages (pages that were stubs when that revision was made)
        dbaccess.createView(self.acceso[1], view="stubs_"+self.language,\
        columns="rev_id, page_id, rev_len, page_len, page_title, author, author_text, rev_timestamp,"\
        " rev_parent_id",
        query="SELECT rev_id, rev_page, rev_len, page_len, page_title, rev_user, rev_user_text, "+\
        "rev_timestamp, rev_parent_id FROM revision, page WHERE rev_page=page_id AND"+\
        " page_namespace=0 AND rev_is_stub=1")
        #View with info only for revisions of current stub pages
        dbaccess.createView(self.acceso[1], view="cur_stubs_"+self.language,\
        columns="rev_id, page_id, rev_len, page_len, page_title, author, author_text, rev_timestamp,"\
        " rev_parent_id",
        query="SELECT rev_id, rev_page, rev_len, page_len, page_title, rev_user, rev_user_text, "+\
        "rev_timestamp, rev_parent_id FROM revision, page WHERE rev_page=page_id AND"+\
        " page_namespace=0 AND page_is_stub=1")
        #From this point on, automatically create views for the set of pages included in the remaining namespaces in MediaWiki
        for nspace, nsnum in zip(self.nspaces[7:], range(1,16)):
            dbaccess.createView(self.acceso[1], view=nspace+"_"+self.language,\
            columns="rev_id, page_id, rev_len, page_len, page_title, author, author_text, rev_timestamp,"+\
            " rev_parent_id",
            query="SELECT rev_id, rev_page, rev_len, page_len, page_title, rev_user, rev_user_text, "+\
            "rev_timestamp, rev_parent_id FROM revision, page WHERE rev_page=page_id AND"+\
            " page_namespace="+str(nsnum))
            
        #View sumarizing the distribution of pages among namespaces
        dbaccess.dropView(self.acceso[1], "nspaces_"+self.language)
        dbaccess.createView(self.acceso[1],view="nspaces_"+self.language, columns="namespace, pages_in_nspace",\
        query="SELECT page_namespace, COUNT(*) FROM page GROUP BY page_namespace")
    
        ##    Intermidiate views for the minimun timestamp of every page [annons, and logged users]
        ## And other useful intermediate views regarding page evolution
        for nspace in self.nspaces:
            dbaccess.dropView(self.acceso[1], nspace+"_"+self.language+\
            "_page_min_timestamp_logged")
            dbaccess.createView(self.acceso[1], view=nspace+"_"+self.language+\
            "_page_min_timestamp_logged", columns="page_id, rev_id, author, rev_timestamp",\
            query="SELECT page_id, rev_id,author, MIN(rev_timestamp) FROM "+\
            nspace+"_"+self.language+" WHERE author!=0 GROUP BY page_id")
            dbaccess.dropView(self.acceso[1], nspace+"_"+self.language+\
            "_page_min_timestamp_annons")
            dbaccess.createView(self.acceso[1], view=nspace+"_"+self.language+\
            "_page_min_timestamp_annons",\
            columns="page_id, rev_id, author_text, rev_timestamp",\
            query="SELECT page_id,rev_id,author_text, MIN(rev_timestamp) FROM "+\
            nspace+"_"+self.language+" WHERE author=0 GROUP BY page_id")
            
            dbaccess.dropView(self.acceso[1],nspace+"_"+self.language+"_list_months")
            dbaccess.createView(self.acceso[1],view=nspace+"_"+self.language+"_list_months",\
            columns="month, year",query="SELECT MONTH(rev_timestamp) as month, "+\
            "YEAR(rev_timestamp) as year"+\
            " FROM "+nspace+"_"+self.language+" GROUP BY year, month ORDER BY year, month")
            
            dbaccess.dropView(self.acceso[1],nspace+"_"+self.language+"_list_quarters")
            dbaccess.createView(self.acceso[1],view=nspace+"_"+self.language+"_list_quarters",\
            columns="quarter, year",query="SELECT QUARTER(rev_timestamp) as quarter, "+\
            "YEAR(rev_timestamp) as year FROM "+nspace+"_"+self.language+" GROUP BY year,"+\
            " quarter ORDER BY year, quarter")
        
    ##    Close DB connection
        dbaccess.close_Connection(self.acceso[0])
        
    def infoAuthors(self):
        ##  Generates statistics per user
        ##  Get DB connection
        self.acceso = dbaccess.get_Connection("localhost", 3306, self.conf.msqlu, self.conf.msqlp,\
        "wx_"+self.language+"_"+self.conf.dumptype)
        
        ##	local configuration: retrieving info for authors
        target="author"
        ##	intervals might be days, weeks, months, quarters, years
        intervals=["months", "quarters","weeks"]
        
        ############################
        #Number of total revisions per author ID
        for nspace in self.nspaces:
            self.__total_rev(self.acceso[1], nspace+"_"+self.language, target)
        
        ############################
        #Different articles edited per user
        for nspace in self.nspaces:
            self.__total_rev_diff(self.acceso[1], nspace+"_"+self.language, target)
        
        ############################
        #Total num of articles started per author
        #We consider as the beginning of an article the first revision of that article
        for nspace in self.nspaces:
            self.__total_page_init_author(self.acceso[1], nspace+"_"+self.language)
        
        ############################
        #Total number of revisions per author for several time intervals
        #Currently, we are only interested in data per months, quarters and weeks
        for nspace in self.nspaces:
            for interval in intervals:
                self.__total_rev_time(self.acceso[1], interval,nspace+"_"+self.language, target)
        
        ############################
        #Num of different articles revised per author for several time intervals
        for nspace in self.nspaces:
            for interval in intervals:
                self.__total_rev_diff_time(self.acceso[1], interval,nspace+"_"+self.language, target)
        
        ############################
        #Num of different articles initiated per author
        for nspace in self.nspaces:
            for interval in intervals:
                self.__total_page_init_author_time(self.acceso[1], interval,nspace+"_"+self.language)
                
        ############################
        #   BIRTH AND DEATH ANALYSIS FOR THE AUTHOR COMMUNITY
        ############################
        
        #Close DB connection
        dbaccess.close_Connection(self.acceso[0])
    
    def infoPages(self):
        ##	Generates statistics per article
        ##	Get new DB connection
        self.acceso = dbaccess.get_Connection("localhost", 3306, self.conf.msqlu, self.conf.msqlp,\
        "wx_"+self.language+"_"+self.conf.dumptype)
        
        #Local configuration
        target="page_id"
        intervals=["months", "quarters","weeks"]
        
        ###########################
        #Total num of revisions per page
        for nspace in self.nspaces:
            self.__total_rev(self.acceso[1], nspace+"_"+self.language, target)
        
        ###########################
        #Total number of different editors per page
        for nspace in self.nspaces:
            self.__total_rev_diff(self.acceso[1], nspace+"_"+self.language, target)
        
        ###########################
        #Total number of revisions per page for several time intervals
        #Currently, we are only interested in months, quarters and weeks
        for nspace in self.nspaces:
            for interval in intervals:
                self.__total_rev_time(self.acceso[1], interval,nspace+"_"+self.language, target)
        
        ###########################
        #Total number of different editors per page; per month ,quarter and week
        for nspace in self.nspaces:
            for interval in intervals:
                self.__total_rev_diff_time(self.acceso[1], interval,nspace+"_"+self.language, target)
        
        #Close DB connection
        dbaccess.close_Connection(self.acceso[0])
    
    def infoContents(self):
        ###########################
        #Contents analysis
        ###########################
        ##  Get DB connection
        self.acceso = dbaccess.get_Connection("localhost", 3306, self.conf.msqlu, self.conf.msqlp,\
        "wx_"+self.language+"_"+self.conf.dumptype)
        ## For all namespaces (official an artificial):
        ## Evolution in time of the lenght of user contributions (per month; per quarter)
        ## Evolution in time of the lenght of pages (per month; per quarter supported but commented)
        for nspace in self.nspaces:
            self.__content_evolution(self.acceso[1], nspace+"_"+self.language)
        dbaccess.close_Connection(self.acceso[0])
        
    def generalStatistics(self):
    ##  Computes the views containing general statistics and overall information:
    ##  For all namespaces (official and artificial):
    ################
    ##  View _overall_statistics1_months, which includes
    ##  Total num of pages with at least one edit in that month, total number of contribs, 
    ##  total num of users who made at least 1 edit in that month (alive_users)
    ####################################
    ##  Parameters from Wikistats by Erik Zachte
    ####################################
    ##  Wikipedians: contributors, active wikipedians, very active wikipedians
    ##  Articles: (WARNING: readable contents are not being filtered out yet)
    ##  new articles per day, edits per article, bytes per article, % of articles over 0.5k,
    ##  % of articles over 2k
    ##  Total size of contribs per month
    ##  Size of pages and number of different authors who have edited them
    ####################################
    ##    Get new DB connection
        self.acceso = dbaccess.get_Connection("localhost", 3306, self.conf.msqlu, self.conf.msqlp,\
        "wx_"+self.language+"_"+self.conf.dumptype)
    ##    General statistics
        for nspace in self.nspaces:
            self.__gral_stats(self.acceso[1], nspace+"_"+self.language)
    ##    Close DB connection
        dbaccess.close_Connection(self.acceso[0])
        
    ##########################################################
    #################################
    #PRIVATE METHODS
    #################################
    
    def __total_rev(self,cursor, table, target="author"):
    ##    target=author --> Contributions per logged user, without annons
    ##    target=page_id --> Contributions per page, without annons
        dbaccess.dropView(cursor, table+"_revs_"+target+"_logged")
        dbaccess.createView(cursor, view=table+"_revs_"+target+"_logged",\
        columns=target+", tot_revisions", query="SELECT "+target+", count(*) AS tot_revisions FROM "+\
        table+" WHERE author!=0 GROUP BY "+target+" ORDER BY tot_revisions")
    ##        Idem , sum up annons and registered users (only for pages)
        if target=="page_id":
            dbaccess.dropView(cursor, table+"_revs_"+target+"_all")
            dbaccess.createView(cursor, view=table+"_revs_"+target+"_all",\
            columns=target+", tot_revisions", query="SELECT "+target+", count(*) AS tot_revisions FROM "+\
            table+" GROUP BY "+target+" ORDER BY tot_revisions")
    ##        Idem only with annons edits, order by IP address
        if target == "author":
            target = "author_text"
        dbaccess.dropView(cursor, table+"_revs_"+target+"_annons")
        dbaccess.createView(cursor, view=table+"_revs_"+target+"_annons",\
        columns=target+", tot_revisions", query="SELECT "+target+", count(*) AS tot_revisions FROM "+\
        table+" WHERE author=0 GROUP BY "+target+" ORDER BY tot_revisions")
    
    def __total_rev_diff(self,cursor, table, target="author"):
    
        ##	target=author Total number of different pages per author
        ##	target=page_id Total number of different authors per page
        if target=="author":
            field_distinct="page_id"
        elif target=="page_id":
            field_distinct="author"
            
        dbaccess.dropView(cursor, table+"_diff_"+field_distinct+"_"+target+"_logged")
        dbaccess.createView(cursor, view=table+"_diff_"+field_distinct+"_"+target+"_logged",\
        columns=target+", diff_"+field_distinct, query="SELECT "+target+", COUNT(DISTINCT "+\
        field_distinct+") AS diff_"+field_distinct+" FROM "+table+" WHERE author!=0 GROUP BY "+\
        target+" ORDER BY diff_"+field_distinct)
    ##        Total number of different authors per page (annons included)
        if target=="page_id":
            dbaccess.dropView(cursor, table+"_diff_"+field_distinct+"_"+target+"_all")
            dbaccess.createView(cursor, view=table+"_diff_"+field_distinct+"_"+target+"_all",\
            columns=target+", diff_"+field_distinct, query="SELECT "+target+", COUNT(DISTINCT "+\
            field_distinct+") AS diff_"+field_distinct+" FROM "+table+" GROUP BY "+\
            target+" ORDER BY diff_"+field_distinct)
    ##        target=author Total number of different pages per annon author
    ##        target=page_id Total number of different annons per page
        if target == "author":
            target = "author_text"
        dbaccess.dropView(cursor, table+"_diff_"+field_distinct+"_"+target+"_annons")
        dbaccess.createView(cursor, view=table+"_diff_"+field_distinct+"_"+target+"_annons",\
        columns=target+", diff_"+field_distinct, query="SELECT "+target+", COUNT(DISTINCT "+\
        field_distinct+") AS diff_"+field_distinct+" FROM "+table+" WHERE author=0 GROUP BY "+\
        target+" ORDER BY diff_"+field_distinct)
    
    def __total_page_init_author(self,cursor, table):
        """
        Total number of different pages started per author
        We count the number of different pages a certain author edited for the first time
        The opposite is useless, since only one author init every article
        """
    ##    Total number of different pages started by a logged author
        dbaccess.dropView(cursor, table+"_init_pages_author_logged")
        dbaccess.createView(cursor, view=table+"_init_pages_author_logged",\
        columns="author, init_pages", query= "SELECT author, COUNT(DISTINCT page_id) AS init_pages FROM "+\
        table+"_page_min_timestamp_logged WHERE author!=0 GROUP BY author ORDER BY init_pages")
    ##    The same for annons
        dbaccess.dropView(cursor, table+"_init_pages_author_annons")
        dbaccess.createView(cursor, view=table+"_init_pages_author_annons",\
        columns="author_text, init_pages", query= "SELECT author_text, COUNT(DISTINCT page_id)"+\
        " AS init_pages FROM "+table+"_page_min_timestamp_annons GROUP BY author_text ORDER BY init_pages")
    
    def __total_rev_time(self,cursor,interval,table, target="author"):
    ##    target=author Total number of revisions per author in a certain time interval
    ##    target=article Total number of revisions per article received in a certain time interval
        if interval in self.type_interval_select:
    ##        logged users
            dbaccess.dropView(cursor, table+"_revs_"+target+"_logged_"+interval)
            dbaccess.createView(cursor, view=table+"_revs_"+target+"_logged_"+interval, columns=target+\
            ", tot_revisions, "+self.type_interval_columns[interval], query="SELECT "+target+\
            ", count(*) AS tot_revisions, "+self.type_interval_select[interval]+" FROM "+table+\
            " WHERE author!=0 GROUP BY "+target+", "+self.type_interval_group[interval]+" ORDER BY tot_revisions")
    ##        all users per page_id
            if target=="page_id":
                dbaccess.dropView(cursor, table+"_revs_"+target+"_all_"+interval)
                dbaccess.createView(cursor, view=table+"_revs_"+target+"_all_"+interval, columns=target+\
                ", tot_revisions, "+self.type_interval_columns[interval], query="SELECT "+target+\
                ", count(*) AS tot_revisions, "+self.type_interval_select[interval]+" FROM "+table+" GROUP BY "+\
                target+", "+self.type_interval_group[interval]+" ORDER BY tot_revisions")
    ##        annons
            if target == "author":
                target = "author_text"
            dbaccess.dropView(cursor, table+"_revs_"+target+"_annons_"+interval)
            dbaccess.createView(cursor, view=table+"_revs_"+target+"_annons_"+interval, columns=target+\
            ", tot_revisions, "+self.type_interval_columns[interval], query="SELECT "+target+\
            ", count(*) AS tot_revisions, "+self.type_interval_select[interval]+" FROM "+table+\
            " WHERE author=0 GROUP BY "+target+", "+self.type_interval_group[interval]+" ORDER BY tot_revisions")
        else:
            print "You chose an unsupported time interval.\n"
            print "Please choose one of the following [days, weeks, moths, quarters, years]\n"
    
    def __total_rev_diff_time(self,cursor,interval,table, target="author"):
        """
        target = author Recovers total num of different articles contributed by every author
        classifying results in temporal intervals
        target = article Recovers number of different authors who revised every article
        classifying results in temporal intervals
        """
        if target=="author":
            field_distinct="page_id"
        elif target=="page_id":
            field_distinct="author"
        
        if interval in self.type_interval_select:
            dbaccess.dropView(cursor, table+"_diff_"+field_distinct+"_"+target+"_logged_"+interval)
            dbaccess.createView(cursor, view=table+"_diff_"+field_distinct+"_"+target+"_logged_"+interval,\
            columns=target+", diff_"+field_distinct+", "+self.type_interval_columns[interval], query="SELECT "+\
            target+", COUNT(DISTINCT "+field_distinct+") AS diff_"+field_distinct+", "+\
            self.type_interval_select[interval]+" FROM "+table+" WHERE author!=0 GROUP BY "+target+", "+\
            self.type_interval_group[interval]+" ORDER BY diff_"+field_distinct)
            if target=="page_id":
                dbaccess.dropView(cursor, table+"_diff_"+field_distinct+"_"+target+"_all_"+interval)
                dbaccess.createView(cursor, view=table+"_diff_"+field_distinct+"_"+target+"_all_"+\
                interval, columns=target+", diff_"+field_distinct+", "+self.type_interval_columns[interval],\
                query="SELECT "+target+", COUNT(DISTINCT "+field_distinct+") AS diff_"+field_distinct+", "+\
                self.type_interval_select[interval]+" FROM "+table+" GROUP BY "+target+", "+\
                self.type_interval_group[interval]+" ORDER BY diff_"+field_distinct)
            
            if target == "author":
                target = "author_text"
            dbaccess.dropView(cursor, table+"_diff_"+field_distinct+"_"+target+"_annons_"+interval)
            dbaccess.createView(cursor, view=table+"_diff_"+field_distinct+"_"+target+"_annons_"+\
            interval, columns=target+", diff_"+field_distinct+", "+self.type_interval_columns[interval],\
            query="SELECT "+target+", COUNT(DISTINCT "+field_distinct+") AS diff_"+field_distinct+", "+\
            self.type_interval_select[interval]+" FROM "+table+" WHERE author=0 GROUP BY "+target+", "+\
            self.type_interval_group[interval]+" ORDER BY diff_"+field_distinct)
        else:
            print "You chose an unsupported time interval.\n"
            print "Please choose one of the following [days, weeks, moths, quarters, years]\n"
    
    def __total_page_init_author_time(self,cursor,interval,table):
        ##	Total number of different articles initiated per author
        ##	for different time intervals
        if interval in self.type_interval_select:
            ##    Total number of different pages started by a logged author
            dbaccess.dropView(cursor, table+"_init_pages_author_logged_"+interval)
            dbaccess.createView(cursor, view=table+"_init_pages_author_logged_"+interval,\
            columns="author, init_pages, "+self.type_interval_columns[interval],\
            query= "SELECT author, COUNT(DISTINCT page_id) AS init_pages, " +self.type_interval_select[interval]+\
            " FROM "+table+"_page_min_timestamp_logged WHERE author!=0 GROUP BY author, "+\
            self.type_interval_group[interval]+" ORDER BY init_pages")
            ##    The same for annons
            dbaccess.dropView(cursor, table+"_init_pages_author_annons_"+interval)
            dbaccess.createView(cursor, view=table+"_init_pages_author_annons_"+interval,\
            columns="author_text, init_pages, "+self.type_interval_columns[interval],\
            query= "SELECT author_text, COUNT(DISTINCT page_id) AS init_pages, " +\
            self.type_interval_select[interval]+" FROM "+table+"_page_min_timestamp_annons GROUP BY author_text, "+\
            self.type_interval_group[interval]+" ORDER BY init_pages")
        else:
            print "You chose an unsupported time interval.\n"
            print "Please choose one of the following [days, weeks, moths, quarters, years]\n"
    
    ###########################################################
    
    def __content_evolution(self,cursor, table):
    ##    Create some views to make data retrieving and graphics depicting easier
    ##    Evolution in time of the page len at the beginning of every month/quarter
        dbaccess.dropView(cursor, table+"_page_temp_months")
        dbaccess.createView(cursor, view=table+"_page_temp_months",\
        columns="page_id, rev_id, rev_len, month, year", query="SELECT page_id, rev_id, rev_len,"+\
        " MONTH(rev_timestamp), YEAR(rev_timestamp) FROM "+table)
        
##        dbaccess.dropView(cursor, table+"_page_temp_quarters")
##        dbaccess.createView(cursor, view=table+"_page_temp_quarters",\
##        columns="page_id, rev_id, rev_len, quarter, year", query="SELECT page_id, rev_id, rev_len,"+\
##        " QUARTER(rev_timestamp), YEAR(rev_timestamp) FROM "+table)
        
        dbaccess.dropView(cursor, table+"_page_maxrev_till_month")
        dbaccess.createView(cursor, view=table+"_page_maxrev_till_month",\
        columns="page_id, max_rev_id, month, year",\
        query="SELECT page_id, max(rev_id), b.month, b.year"+\
        " FROM "+table+"_page_temp_months"+" AS a, "+table+"_list_months"+\
        " AS b WHERE(a.month<=b.month) AND (a.year<=b.year)"+\
        " GROUP BY b.year, b.month, page_id")
        
        dbaccess.dropView(cursor, table+"_page_len_till_month")
        dbaccess.createView(cursor, view=table+"_page_len_till_month",\
        columns="page_id, max_rev_id, rev_len, amonth, ayear, bmonth, byear",\
        query="SELECT b.page_id, b.max_rev_id, a.rev_len, a.month, a.year, b.month, b.year"+\
        " FROM "+table+"_page_temp_months"+" AS a, "+table+"_page_maxrev_till_month"+\
        " AS b WHERE (a.rev_id=b.max_rev_id) ORDER BY b.year, b.month, page_id")
        
        dbaccess.dropView(cursor, table+"_page_len_evol_months")
        dbaccess.createView(cursor, view=table+"_page_len_evol_months",\
        columns="month, year, page_len_sum",query="SELECT bmonth, byear, SUM(rev_len) FROM "+\
        table+"_page_len_till_month GROUP BY byear, bmonth ORDER BY byear, bmonth")
        
        dbaccess.dropView(cursor, table+"_page_num_evol_months")
        dbaccess.createView(cursor, view=table+"_page_num_evol_months",\
        columns="month, year, page_num",\
        query="SELECT b.month, b.year, COUNT(DISTINCT(page_id))"+\
        " FROM "+table+"_page_temp_months"+" AS a, "+table+"_list_months"+\
        " AS b WHERE(a.month<=b.month) AND (a.year<=b.year)"+\
        " GROUP BY b.year, b.month")
        
##        dbaccess.dropView(cursor, table+"_page_maxrev_till_quarter")
##        dbaccess.createView(cursor, view=table+"_page_maxrev_till_quarter",\
##        columns="page_id, max_rev_id, quarter, year",\
##        query="SELECT page_id, max(rev_id), b.quarter, b.year"+\
##        " FROM "+table+"_page_temp_quarters"+" AS a, "+table+"_list_quarters"+\
##        " AS b WHERE(a.quarter<=b.quarter) AND (a.year<=b.year)"+\
##        " GROUP BY b.year, b.month, page_id")
        
##        dbaccess.dropView(cursor, table+"_page_len_till_quarter")
##        dbaccess.createView(cursor, view=table+"_page_len_till_quarter",\
##        columns="page_id, max_rev_id, rev_len, aquarter, ayear, bquarter, byear",\
##        query="SELECT b.page_id, b.max_rev_id, a.rev_len, a.quarter, a.year, b.quarter, b.year"+\
##        " FROM "+table+"_page_temp_quarters"+" AS a, "+table+"_page_maxrev_till_quarter"+\
##        " AS b WHERE (a.rev_id=b.max_rev_id) ORDER BY b.year, b.quarter, page_id")
##        
##        dbaccess.dropView(cursor, table+"_page_len_evol_quarters")
##        dbaccess.createView(cursor, view=table+"_page_len_evol_quarters",\
##        columns="quarter, year, page_len_sum",query="SELECT bquarter, byear, SUM(rev_len) FROM "+\
##        table+"_page_len_till_quarter GROUP BY byear, bquarter ORDER BY byear, bmonth")
        
    ##    Now for revisions. We have to deal with the first revision of each tree.
    ##    In the first revision of every page, rev_parent==NULL. 
    ##    Later, UNION that group with the first revisions group //Must prove it against testbed dump
    
    #    Length in bytes of the current rev and the previous one
        dbaccess.dropView(cursor, table+"_contrib_len")
        dbaccess.createView(cursor, view=table+"_contrib_len",\
        columns="rev_id, page_id, author, contrib_len, timestamp",\
        query="(SELECT cur.rev_id, cur.page_id, cur.author, (cur.rev_len-prev.rev_len) AS contrib_len, "+\
        " cur.rev_timestamp FROM "+table+" AS cur, "+table+\
        " AS prev WHERE cur.rev_parent_id IS NOT NULL AND cur.rev_parent_id=prev.rev_id)"+\
        " UNION (SELECT rev_id, page_id, author, rev_len, rev_timestamp FROM "+table+\
        " WHERE rev_parent_id IS NULL)")

    #    Sum of the length of the contributions for every author; per month
        dbaccess.dropView(cursor, table+"_contrib_len_evol_months")
        dbaccess.createView(cursor, view=table+"_contrib_len_evol_months",\
        columns="author, sum_contrib_len, month, year",\
        query="SELECT author, SUM(contrib_len), MONTH(timestamp) as month,"+\
        " YEAR(timestamp) as year FROM "+table+\
        "_author_contrib_len GROUP BY author, year, month ORDER BY author, year, month")
    #    The same per quarter
        dbaccess.dropView(cursor, table+"_contrib_len_evol_quarters")
        dbaccess.createView(cursor, view=table+"contrib_len_evol_quarters",\
        columns="author, sum_contrib_len, quarter, year",\
        query="SELECT author, SUM(contrib_len), QUARTER(timestamp) as quarter,"+\
        " YEAR(timestamp) as year FROM "+table+\
        "_author_contrib_len GROUP BY author, year, quarter ORDER BY author, year, quarter")

    def __gral_stats(self,cursor, table):
        #  IT IS MANDATORY TO CALL __content_evolution BEFORE CALLING THIS METHOD
        ##  Total num of pages with at least one edit in that month, total number of contribs, 
        ##  total num of users who made at least 1 edit in that month (alive_users)
        dbaccess.dropView(cursor, table+"_overall_statistics1_months")
        dbaccess.createView(cursor, view=table+"_overall_statistics1_months",\
        columns="month, year, page_count, tot_contribs, alive_users",\
        query="SELECT MONTH(rev_timestamp) AS month, YEAR(rev_timestamp) AS year, COUNT(DISTINCT page_id),"+\
        " COUNT(DISTINCT rev_id), COUNT(DISTINCT author) FROM "+table+" GROUP BY year, month ORDER BY "+\
        " year, month")
        
        ####################################
        ## Parameters from Wikistats by Erik Zachte
        ####################################
        ## Wikipedians: contributors
        ## Wikipedians who edited at least 10 times since they arrived
        ## Warning!! This view does not deal with dead wikipedians, those who did not
        ## came back in subsequent months
        dbaccess.dropView(cursor, table+"_author_contrib_till_month")
        dbaccess.createView(cursor, view=table+"_author_contrib_till_month",\
        columns="author, sum_contribs, bmonth, byear",\
        query="SELECT author, SUM(tot_revisions), b.month, b.year"+\
        " FROM "+table+"_revs_author_logged_months"+" AS a, "+table+"_list_months"+\
        " AS b WHERE(a.month<=b.month) AND (a.year<=b.year)"+\
        " GROUP BY b.year, b.month, author")
        
        dbaccess.dropView(cursor, table+"_contributors_evol_months")
        dbaccess.createView(cursor, view=table+"_contributors_evol_months",\
        columns="month, year, contributors_sum",query="SELECT bmonth, byear,"+\
        " COUNT(DISTINCT(author)) FROM "+table+"_author_contrib_till_month "+\
        " WHERE sum_contribs>=10 GROUP BY byear, bmonth ORDER BY byear, bmonth")
        
        ## Wikipedians: active wikipedians
        # Wikipedians who contributed 5 times or more in this month
        dbaccess.dropView(cursor, table+"_active_authors_months")
        dbaccess.createView(cursor, view=table+"_active_authors_months",\
        columns="month, year, active_authors",\
        query="SELECT month, year, COUNT(DISTINCT(author)) FROM "+table+\
        "_revs_author_logged_months WHERE tot_revisions>=5 GROUP BY year, month")
        
        ## Wikipedians: very active wikipedians
        # Wikipedians who contributed 100 times or more in this month
        dbaccess.dropView(cursor, table+"_very_active_authors_months")
        dbaccess.createView(cursor, view=table+"_very_active_authors_months",\
        columns="month, year, active_authors",\
        query="SELECT month, year, COUNT(DISTINCT(author)) FROM "+table+\
        "_revs_author_logged_months WHERE tot_revisions>=100 GROUP BY year, month")
        
        ## Articles: Total number of pages (official count and alternative count)
        ## Offical count --> Articles that contain at least one internal link
        ## Alternative count --> Articles that contain at least one internal link and 200 characters readable text,
        ## disregarding wiki- and html codes, hidden links, etc.; also headers do not count
        ## (other columns of wikistats are based on the official count method)
        # TODO: jfelipe- Think about implementing strip of wiki text and special HTML codes
        # But it seems not to be very straightforward
        # SKIPPING STRIPPED VERSIONS OF ARTICLES' CONTENTS BY THE MOMENT
        
        ## IMPORTANT NOTE!!
        ## WIkiXRay will compute tables for both official articles and the complete set of articles
        ## Measurements regarding official articles will have a page_off_ suffix
        # OFFICIAL ARTICLES IDENTIFICATION NOT YET IMPLEMENTED
        
        
        ## Articles: new articles per day in current month (MEAN)
        ## new articles per day in current month (MEAN)
        
        
        
        ## Articles: edits per article; per month
        # Mean number of revisions per article; per month
        dbaccess.dropView(cursor, table+"_revs_per_page_id_months")
        dbaccess.createView(cursor, view=table+"_revs_per_page_id_months",\
        columns="month, year, revs_per_article", query="SELECT month, year,"+\
        " (SUM(tot_revisions)/COUNT(DISTINCT(page_id))) FROM "+table+\
        "_revs_page_id_logged_months GROUP BY year, month"+\
        " ORDER BY year, month")
        
        ## Articles: bytes per article; per month
        # Mean size of article in bytes; per month
        dbaccess.dropView(cursor, table+"_bytes_per_article_months")
        dbaccess.createView(cursor, view=table+"_bytes_per_article_months",\
        columns="month, year, bytes_per_article", query="SELECT a.month, a.year,"+\
        " (b.page_len_sum/a.page_num) FROM "+table+"_page_num_evol_months AS a, "+table+\
        "_page_len_evol_months AS b"+\
        " WHERE (a.month=b.month) AND (a.year=b.year) ORDER BY a.year, a.month")
        
        ## Articles: articles over 0.5 Kb (%); per month
        # Percentage of articles with at least 0.5 Kb readable text; per month
        ## BY THE MOMENT, WE DON'T PRECISELY IDENTIFY READABLE TEXT
        dbaccess.dropView(cursor, table+"_pages_over_05k_months")
        dbaccess.createView(cursor, view=table+"_pages_over_05k_months",
        columns="month, year, page_perc", query="SELECT b.month, b.year,"+\
        " (COUNT(DISTINCT(a.page_id))/b.page_num) FROM "+table+"_page_len_till_month AS a, "+\
        table+"_page_num_evol_months AS b WHERE (a.bmonth=b.month) AND (a.Byear=b.year) GROUP BY"+\
        " b.year, b.month, a.page_id ORDER BY b.year, b.month")
        
        ## Articles: articles over 2 Kb (%); per month
        # Percentage of articles with at least 2 Kb readable text; per month
        ## BY THE MOMENT, WE DON'T PRECISELY IDENTIFY READABLE TEXT, SO WE COUNT RAW CONTENTS
        dbaccess.dropView(cursor, table+"_pages_over_2k_months")
        dbaccess.createView(cursor, view=table+"_pages_over_2k_months",
        columns="month, year, page_perc", query="SELECT b.month, b.year,"+\
        " (COUNT(DISTINCT(a.page_id))/b.page_num) FROM "+table+"_page_len_till_month AS a, "+\
        table+"_page_num_evol_months AS b WHERE (a.bmonth=b.month) AND (a.byear=b.year) GROUP BY"+\
        " b.year, b.month, a.page_id ORDER BY b.year, b.month")
        
        ## Database: edits per month
        # Edits in past month (incl. redirects, incl. unregistered contributors, incl. bots)
        # SEE: table _overall_statistics1_months previously generated in this method
        ## Database: database size
        # Combined size of all articles (incl. redirects)
        # SEE: table _page_len_evol_months previously generated in method __content_evolution
        
        ## Database: words
        # Total number of words (excl. redirects, html/wiki codes and hidden links)
        #TODO:
        ## We are still not excluding links or tags so far
        
        
        ## Links: Internal links
        # Total number of internal links (excl. redirects, stubs and link lists)
        #TODO:
        ## To implement when we were able to identify links
        
        
        ## Links: Links to other Wikipedias
        # Total number of links to other Wikipedias
        #TODO:
        ## To implement when we were able to identify links
        
        ## Links: images
        # Total number of images presented
        #TODO:
        ## To implement when we were able to identify links
        
        ## Links: external links
        # Total number of links to other sites
        #TODO:
        ## To implement when we were able to identify links
        
        
        ## Links: redirects
        # Total number of redirects
        ## This is correctly implemented  at present time
        # Already generated
        # Just retrieve _page_num_evol_months or any other adhoc view for 
        # the special purpose namespace redirects
        
        ##    Total size of contribs; per month
        dbaccess.dropView(cursor, table+"_tot_contribs_len_months")
        dbaccess.createView(cursor, view=table+"_contrib_len_evol_months",\
        columns="month, year, tot_contribs_len", query="SELECT  month,"+\
        " year, SUM(sum_contrib_len) FROM "+table+\
        "_author_contrib_len_evol_months GROUP BY year, month")
        
        ##Size of pages and number of different authors who have edited them
        dbaccess.dropView(cursor, table+"_stats_pagelen_difauthors")
        dbaccess.createView(cursor, view=table+"_stats_pagelen_difauthors",\
        columns="page_id, page_len, diff_authors", query="SELECT p.page_id, p.page_len, "+\
        "t.diff_author FROM page as p, "+table+"_diff_author_page_id_logged"+\
        " AS t WHERE p.page_id=t.page_id")
        
    def test_funciones(self):
        self.acceso = dbaccess.get_Connection("localhost", 3306, self.conf.msqlu, self.conf.msqlp,\
        "wx_"+self.language+self.conf.dumptype)
        __total_rev(self.acceso[1], table="stats_nlwiki", target="author")
        ##	targets=["page_id"]
        ##	for target in targets:
        ##		__total_rev(self.acceso[1], language, target)
        ##		__total_rev_target(self.acceso[1], language, target)
        ##		__total_rev_time(self.acceso[1],"years",language, target)
        ##		__total_rev_target_time(self.acceso[1],"years",language, target)
        ##	__total_article_init_author(self.acceso[1], language)
        ##	__article_init_author_time(self.acceso[1],"years",language)
        
        ##    __article_rev_author_time(self.acceso[1], "years", language)
        ##	__total_rev_time(self.acceso[1],"months",language, "page_id")
        ##	__total_article_init_author(self.acceso[1], language, target="author")
        ##	__content_evolution(self.acceso[1], language)
        dbaccess.close_Connection(self.acceso[0])
