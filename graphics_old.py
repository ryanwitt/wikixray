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

@authors: Jose Felipe Ortega
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jfelipe@gsyc.escet.urjc.es
"""

from rpy import *
import dbaccess, math, os, test_admins

#WE TAKE DE LANGUAGE LIST FROM THE COMMON CONFIG FILE
#WE CREATE INDEPENDENT SUBDIRECTORIES WITHIN THE GRAPHICS DIRECTORY 
#TO STORE RESULTS FOR EACH LANGUAGE VERSION

def contributions(idiomas):
    """
    Create some graphs and files with statistical results about authors contributions
    
    @type  idiomas: list of strings
    @param idiomas: list of strings indicating the language versions to process
    """
    for idioma in idiomas:
        acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", idioma+"_stub")
        #acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", idioma+"_pages")
        #dbaccess.query_SQL(acceso[1], "page_id, page_namespace", "page", where="page_namespace=0", create="pag_namespace")
        tcnoann=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_NoAnnons_author_"+idioma)
        tcauthor=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_author_"+idioma)
        #tc_ann=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_Annons_author_text_"+idioma)
        dbaccess.close_Connection(acceso[0])
        
        data=__tup_to_list(tcnoann)
        listay_tcnoann=data.pop()
        listax=data.pop()
        data=__tup_to_list(tcauthor)
        listay_tcauthor=data.pop()
        listax=data.pop()
        #data=__tup_to_list(tc_ann)
        #listay_tc_ann=data.pop()
        #listax=data.pop()
        r.png("graphics/"+idioma+"/gini_TContrib_NoAnn_"+idioma+".png")
        __lorenz_Curve(listay_tcnoann)
        r.png("graphics/"+idioma+"/gini_TContrib_"+idioma+".png")
        __lorenz_Curve(listay_tcauthor)
        #r.png("graphics/"+idioma+"/gini_TContrib_Ann_"+idioma+".png")
        #__lorenz_Curve(listay_tc_ann)
        #T=raw_input("press any key...")

def comparative_contributions():
    listaidiomas=["dewiki", "jawiki", "frwiki", "plwiki", "nlwiki", "itwiki", "ptwiki", "eswiki", "svwiki"]
##    lista=["eswiki", "svwiki"]
    
    r.png("graphics/AAA/gini_comparative_top10.png")
    flag=0
    for idioma in listaidiomas:
        print "Starting comparative Gini analysis for language..."+idioma+"\n"
        acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", idioma+"_stub")
        tcnoann=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_NoAnnons_author_"+idioma)
        dbaccess.close_Connection(acceso[0])
        data=__tup_to_list(tcnoann)
        listay_tcnoann=data.pop()
        listax=data.pop()
        if flag==0:
            _lorenz_Comp_Curves(listay_tcnoann,flag)
            flag=1
        else:
            _lorenz_Comp_Curves(listay_tcnoann,flag)
    r.dev_off()
    print "Comparative graphic for Gini curves finished!!"

def histogram(idiomas):
    """
    Create histograms depicting article size distribution for a certain language version
    
    @type  idiomas: list of strings
    @param idiomas: list of strings indicating the language versions to process
    """
    filenames=["boxplot_log.png", "histogram_log.png", "histogram_log_low.png", "histogram_log_high.png", "ecdf_log_low.png", "ecdf_log_high.png", "data/page_len_log.data", "/data/histograms.info", "ecdf_total.png"]
    
    for idioma in idiomas:
        print "Creando histogramas para el idioma ... "+idioma
        #Print to another file the names of graphics files, following the order in the GNU R script histogram.R
        f=open("./data/hist_files_names.data",'w')
        for line in filenames:
            f.write("./graphics/"+idioma+"/"+line+"\n")
        f.close()
        acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", idioma+"_stub")
    
        #Considering only database pages corresponding to articles, with NAMESPACE=MAIN=0
        #dbaccess.dropTab_SQL(acceso[1], "aux")
        #dbaccess.query_SQL(acceso[1],"page_id, page_len","page", where="page_namespace=0", order="page_len", create="aux")
        result=dbaccess.query_SQL(acceso[1], "page_id, page_len", "aux")
        dbaccess.close_Connection(acceso[0])
        data=__tup_to_list(result)
        page_len=data.pop()
        for i in range(len(page_len)):
            if page_len[i]!=0:
                page_len[i]=math.log10(page_len[i])
        
        #Print to another file a list with article sizes to plot histograms
        f=open("./graphics/"+idioma+"/data/page_len_log.data", 'w')
        for value in page_len:
            f.writelines(str(value)+"\n")
        f.close()
        
        #CALL THE GNU R SCRIPT Histogram.R
        succ=os.system("R --vanilla < ./histogram.R > debug_R")
        if succ==0:
            print "Funcion histogram ejecutada con exito para el lenguage... "+idioma
        

def summary_evol(idiomas):
    """
    Create some graphs summarizing the evolution in time of critical quantitative
    parameters for each language version to explore
    
    @type  idiomas: list of strings
    @param idiomas: list of strings indicating the language versions to process
    """
##	¡¡WARNING!! Please be careful when selecting values from tables storing evolution in time of number of articles, size etc.
##  You must always use a GROUP BY(pageCount, limitDate) clause, due to 
##  periods of inactivity that could generate duplicate entries in the graphics
    filenames=["page_dates.data", "page_Count_evol.data", "page_Len_Sum_log.data", "contribs_evol.data", "nspaces.data", "nspace_distrib.data", "diffArticles.data", "authors.data", "diff_authors_x_article.data", "authors_authors_per_pagelen.data", "pagelen_authors_per_pagelen.data"]

    filenames_out=["Tot_num_articles_absx_absy.png", "Tot_num_articles_absx_logy.png", "Tot_num_articles_logx_logy.png", "Tot_pagelensum_absx_absy.png", "Tot_pagelensum_absx_logy.png", "Tot_pagelensum_logx_logy.png", "Tot_contribs_absx_absy.png", "Tot_contribs_absx_logy.png", "Tot_contribs_logx_logy.png", "Diffs_articles_per_author.png", "Diffs_authors_per_article.png", "Diff_authors_against_page_len.png"]
    
    for idioma in idiomas:
        acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", idioma+"_stub")
        #acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", idioma+"_pages")
        result=dbaccess.query_SQL(acceso[1], "pageCount, limitDate", "stats_Evolution_Content_months_"+idioma, group="(limitDate)")
        result2=dbaccess.query_SQL(acceso[1], "pageLenSum, limitDate", "stats_Evolution_Content_months_"+idioma, group="(limitDate)")
        result3=dbaccess.query_SQL(acceso[1], "contribs, limitDate", "stats_Evolution_Content_months_"+idioma, group="(limitDate)")
        
        resultnspace=dbaccess.query_SQL(acceso[1], "pages_nspace, namespace", "stats_nspace_"+idioma)
        
        diffArticlesNoann=dbaccess.query_SQL(acceso[1], "author, theCount", "stats_Article_NoAnnons_author_"+idioma)
        
        diffInitNoann=dbaccess.query_SQL(acceso[1], "author, theCount", "stats_Article_Init_NoAnnons_author_"+idioma)
        
        totRevperArticle=dbaccess.query_SQL(acceso[1], "page_id, theCount", "stats_Contrib_NoAnnons_page_id_"+idioma)
        
        diffAuthorperArticle=dbaccess.query_SQL(acceso[1], "page_id, theCount", "stats_Article_NoAnnons_page_id_"+idioma)
        
        dautxplen=dbaccess.query_SQL(acceso[1], "page_len, authors", "stats_pagelen_difauthors_"+idioma)
        
        dbaccess.close_Connection(acceso[0])
        
        data=__tup_to_list(result, 1)
        dates_x=data.pop()
        page_Count=data.pop()
        
##        if idioma=="frwiki":
        data2=__tup_to_list(result2, 2)
        dates_x=data2.pop()
        dates_x.pop(0)
        dates_x.pop(0)
        page_Len_Sum=data2.pop()
        page_Len_Sum.pop(0)
        page_Len_Sum.pop(0)
##        else:
##            data2=__tup_to_list(result2, 1)
##            dates_x=data2.pop()
##            page_Len_Sum=data2.pop()
        
        data3=__tup_to_list(result3, 1)
        dates_x=data3.pop()
        contribs=data3.pop()
        
        datanspace=__tup_to_list(resultnspace)
        namespaces=datanspace.pop()
        pages_nspace=datanspace.pop()
        
        dataDiffArticlesNoann=__tup_to_list(diffArticlesNoann)
        diffArticles=dataDiffArticlesNoann.pop()
        authors=dataDiffArticlesNoann.pop()
        
        dataDiffInitNoann=__tup_to_list(diffInitNoann)
        diffInitArticles=dataDiffInitNoann.pop()
        authors=dataDiffInitNoann.pop()
        
        datatotRevperArticle=__tup_to_list(totRevperArticle)
        totalRev=datatotRevperArticle.pop()
        article=datatotRevperArticle.pop()
        
        datadiffAuthorperArticle=__tup_to_list(diffAuthorperArticle)
        diffAuthors=datadiffAuthorperArticle.pop()
        article=datadiffAuthorperArticle.pop()
        
        datadautxplen=__tup_to_list(dautxplen)
        autxplen=datadautxplen.pop()
        lenautxplen=datadautxplen.pop()

##  Introduce in data list results form queries in the proper order
##  corresponding with the name files we pass to the GNU R script summary_evol.R      
        for i in range(len(page_Len_Sum)):
            if page_Len_Sum[i]!=0:
                page_Len_Sum[i]=math.log10(page_Len_Sum[i])
                
        dataList=[dates_x, page_Count, page_Len_Sum, contribs, namespaces, pages_nspace, diffArticles, authors, diffAuthors, autxplen, lenautxplen]

        for filename, data in zip (filenames, dataList):
            if(filename.find('date')!=-1):
                __makeDatesFile(idioma, filename, data)
            else:
                __makeDataFile(idioma, filename, data)
        
        ######################################
        
        #Pass data filenames to the GNU R script with a file
        f=open("./data/summary_files_names.data",'w')
        for line in filenames:
            f.write("./graphics/"+idioma+"/data/"+line+"\n")
        f.close()
        
        #Idem with graphic output filenames
        f=open("./data/summary_files_out.data",'w')
        for line in filenames_out:
            f.write("./graphics/"+idioma+"/"+line+"\n")
        f.close()
            
        #CALL THE GNU R SCRIPT summary_evol.R
        
        succ=os.system("R --vanilla < ./summary_evol.R > debug_R")
        if succ==0:
            print "Funcion summary_evol ejecutada con exito para el lenguage... "+idioma
        
        ##		print "paso 1"
        ##		r.png("graphics/"+idioma+"/gini_Diff_Articles_NoAnn_"+idioma+".png")
        ##		__lorenz_Curve(diffArticles)
        
        ##		print "paso 2"
        ##		r.png("graphics/"+idioma+"/gini_Diff_Init_Articles_NoAnn_"+idioma+".png")
        ##		__lorenz_Curve(diffInitArticles)
        
        ###COMPUTER INTENSIVE!!###
        #r.png("graphics/"+idioma+"/gini_Total_Revisions_per_Article_NoAnn_"+idioma+".png")
        #_lorenz_Curve(totalRev)
        

def measuring(idiomas):
    """
    Create some graphs following the research presented by Jakob Voss in his paper
    Mesuring Wikipedia (ISSI 2005)
    
    @type  idiomas: list of strings
    @param idiomas: list of strings indicating the language versions to process
    """
##   Generates some graphics reproducing those in Measuring Wikipedia article
    filenames=["total_edits.data", "noannons_edits.data", "annon_edits.data", "authors_per_article_desc.data", "articles_per_logged_author_desc.data",  "articles_per_anonymous_author_desc.data"]
    
    filenames_out=["total_edits_per_author.png", "total_edits_per_noannon_author.png", "total_edits_per_annon_author.png", "diff_authors_per_article_descending.png", "diff_articles_per_logged_author_descending.png", "diff_articles_per_anonymous_author_descending.png"]
    
    for idioma in idiomas:
        acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", idioma+"_stub")
    ##    acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", idioma+"_pages")
        #Combined evolution graphics
        #ALL THESE GRAPHICS ARE ALREADY GENERATED BY ERIK ZATCHE'S OFFICIAL PERL SCRIPTS
            #Database size
            #Total number of words
            #Total number of internal links
            #Number of articles (including redirects)
            #Number of active wikipedians (more than 5 contributions in a given month)
            #Number of very active wikipedians (more than 100 contributions in a given month)
        
        #Namespace size
            #OK, it is generated in summary_evol() method
            
        #Evolution in time of article size (histogram)
            #IDEA: Download page.sql files for a language for each semester period
            
        #Number of distinct authors per article (descending sorted graphic)
            #Already generated in summary_evol, ONLY NEED TO SORT AND ADJUST IN GNU R
        diffAuthorperArticle=dbaccess.query_SQL(acceso[1], "page_id, theCount", "stats_Article_NoAnnons_page_id_"+idioma)
        
        #Number of distinct articles per author (descending sorted graphic)
            #Idem as in the previous case
        diffArticlesNoann=dbaccess.query_SQL(acceso[1], "author, theCount", "stats_Article_NoAnnons_author_"+idioma)
        diffArticlesAnn=dbaccess.query_SQL(acceso[1], "author_text, theCount", "stats_Article_Annons_author_text_"+idioma)        
        
        data=__tup_to_list(diffAuthorperArticle)
        lisdiffauthorartic=data.pop()
        data=__tup_to_list(diffArticlesNoann)
        lisdiffarticleaut=data.pop()
        data=__tup_to_list(diffArticlesAnn,2)
        lisdiffarticleannon=data.pop()
##        Ordenamos los resultados para que se puedan ajustar a una Power Law
        lisdiffauthorartic.sort(reverse=True)
        lisdiffarticleaut.sort(reverse=True)
        lisdiffarticleannon.sort(reverse=True)
        
        #Number of edtis per author
            #Retrieve results from database
            #We have already created GINI graphics for this parameter
            #ALSO AVAILABLE DATABASE TABLES WITH EVOLUTION IN TIME OF THIS PARAMETER
        
        tcnoann=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_NoAnnons_author_"+idioma)
        tcauthor=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_author_"+idioma)
        tc_ann=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_Annons_author_text_"+idioma)
        
        data=__tup_to_list(tcnoann)
        listcnoann=data.pop()
        data=__tup_to_list(tcauthor)
        listcauthors=data.pop()
        #BTW, we are also obtaining but not using the IP adresses of annon users
        data=__tup_to_list(tc_ann,2)
        listcann=data.pop()
        
##        Arranging results in a decreasing way to adjust them to a power law
        listcnoann.sort(reverse=True)
        listcauthors.sort(reverse=True)
        listcann.sort(reverse=True)
        
        #Ingoing and outgoing number of links per article
            #STILL TO BE DEVELOPED
            #NEED TO FIRST IDENTIFY LINKS FOR A GIVEN ARTICLE IN THE DATABASE
            #LINKS TABLES MAY HELP, but in these dump versions they are all empty!!!
            
            #BROKEN LINKS also need to be considered
        
        dbaccess.close_Connection(acceso[0])
        
        dataList=[listcauthors, listcnoann, listcann, lisdiffauthorartic, lisdiffarticleaut, lisdiffarticleannon]
        
        for filename, data in zip (filenames, dataList):
            if(filename.find('date')!=-1):
                __makeDatesFile(idioma, filename, data)
            else:
                __makeDataFile(idioma, filename, data)
        
        #Pass data filenames to the GNU R script with a file
        f=open("./data/measuring_files_names.data",'w')
        for line in filenames:
            f.write("./graphics/"+idioma+"/data/"+line+"\n")
        f.close()
        
        #Idem with graphic output filenames
        f=open("./data/measuring_files_out.data",'w')
        for line in filenames_out:
            f.write("./graphics/"+idioma+"/"+line+"\n")
        f.close()
            
        #CALL GNU R SCRIPT measuring_Wiki.R
        
        succ=os.system("R --vanilla < ./measuring_Wiki.R > debug_R")
        if succ==0:
            print "Funcion measuring_Wiki.R ejecutada con exito para el lenguage... "+idioma

def community_contrib(idiomas):
    for idioma in idiomas:
        list_admins=test_admins.process_admins(idioma)
        num_admins=list_admins.pop()
        where_clause1=list_admins.pop()
        acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", idioma+"_stub")
        admins_ids=dbaccess.raw_query_SQL(acceso[1], "SELECT DISTINCT(author) FROM stats_"+idioma+" WHERE "+where_clause1+" LIMIT "+str(num_admins))
##        MONTAR WHERE CLAUSE CON ADMINS IDS
        list_admins_ids=[]
        for item in list_admins_ids:
            list_admins_ids.append(int(item[0]))
        where_clause2=test_admins.process_users_ids(list_admins_ids,idioma)
        edits_admin_month=dbaccess.query_SQL(acceso[1], select="year, month, SUM(theCount)", tables="stats_Contrib_NoAnnons_months_author_"+idioma+" ", where=where_clause2, group="year, month ", order="year, month")
        dates_admins=[]
        admins_contribs=[]
        for element in edits_admin_month:
            dates_admins.append(list(element[0:2]))
            admins_contribs.append(int(element[2]))
##        PASAR A UN ARCHIVO PARA PLOT (FIG 2)
##        RECUPERAMOS CONTRIBUCIONES TOTALES POR MESES
        total_edits_month=dbaccess.query_SQL(acceso[1], select="year, month, SUM(theCount)", tables="stats_Contrib_months_author_"+idioma, group="year, month ")
        dates_contribs=[]
        total_contribs=[]
        for element in total_edits_month:
            dates_contribs.append(list(element[0:2]))
            total_contribs.append(int(element[2]))
##        DIVIDIR LA PRIMERA LISTA POR LA SEGUNDA
        perc_contribs_admins=[]
        for admin_contrib, total_contrib in zip(admins_contribs, total_contribs):
            perc_contribs_admins.append((float(admin_contrib)/total_contrib))
##        PASAR A UN ARCHIVO PARA PLOT (FIG 1)

##    FIG 4 TOTAL EDITS MADE BY USERS WITH DIFFERENT EDIT LEVELS
##    CREATE CLUSTER OF USERS IDENTIFIED BY CONTRIBUTIONS LEVEL
##    5 LEVELS: <100, 100-1K, 1K-5K, 5K-10K, >10K
        users_level1=[]
        users_level2=[]
        users_level3=[]
        users_level4=[]
        users_level5=[]
        level1=dbaccess.query_SQL(acceso[1], select="DISTINCT(author)", tables="stats_Contrib_author_"+idioma, where="theCount<=100")
        for userid in level1:
            users_level1.append(int(userid[0]))
        level2=dbaccess.query_SQL(acceso[1], select="DISTINCT(author)", tables="stats_Contrib_author_"+idioma, where="theCount>100 AND theCount<=1000")
        for userid in level2:
            users_level2.append(int(userid[0]))
        level3=dbaccess.query_SQL(acceso[1], select="DISTINCT(author)", tables="stats_Contrib_author_"+idioma, where="theCount>1000 AND theCount<=5000")
        for userid in level3:
            users_level3.append(int(userid[0]))
        level4=dbaccess.query_SQL(acceso[1], select="DISTINCT(author)", tables="stats_Contrib_author_"+idioma, where="theCount>5000 AND theCount<=10000")
        for userid in level4:
            users_level4.append(int(userid[0]))
        level5=dbaccess.query_SQL(acceso[1], select="DISTINCT(author)", tables="stats_Contrib_author_"+idioma, where="theCount>10000")
        for userid in level5:
            users_level5.append(int(userid[0]))
        where_clause_level1=test_admins.process_users_ids(users_level1,idioma)
        where_clause_level2=test_admins.process_users_ids(users_level2,idioma)
        where_clause_level3=test_admins.process_users_ids(users_level3,idioma)
        where_clause_level4=test_admins.process_users_ids(users_level4,idioma)
        where_clause_level5=test_admins.process_users_ids(users_level5,idioma)
        
        contribs_level1_month=dbaccess.query_SQL(acceso[1], select="year, month, SUM(theCount)", tables="stats_Contrib_months_author_"+idioma, where=where_clause_level1, group="year, month")
        contribs_level2_month=dbaccess.query_SQL(acceso[1], select="year, month, SUM(theCount)", tables="stats_Contrib_months_author_"+idioma, where=where_clause_level2, group="year, month")
        contribs_level3_month=dbaccess.query_SQL(acceso[1], select="year, month, SUM(theCount)", tables="stats_Contrib_months_author_"+idioma, where=where_clause_level3, group="year, month")
        contribs_level4_month=dbaccess.query_SQL(acceso[1], select="year, month, SUM(theCount)", tables="stats_Contrib_months_author_"+idioma, where=where_clause_level4, group="year, month")
        contribs_level5_month=dbaccess.query_SQL(acceso[1], select="year, month, SUM(theCount)", tables="stats_Contrib_months_author_"+idioma, where=where_clause_level5, group="year, month")
        list_level1=__process_contribs(contribs_level1_month, total_contribs)
        perc_contribs_level1=list_level1.pop()
        contribs_level1=list_level1.pop()
        dates_level1=list_level1.pop()
        
        list_level2=__process_contribs(contribs_level2_month, total_contribs)
        perc_contribs_level2=list_level2.pop()
        contribs_level2=list_level2.pop()
        dates_level2=list_level2.pop()
        
        list_level3=__process_contribs(contribs_level3_month, total_contribs)
        perc_contribs_level3=list_level3.pop()
        contribs_level3=list_level3.pop()
        dates_level3=list_level1.pop()
        
        list_level4=__process_contribs(contribs_level4_month, total_contribs)
        perc_contribs_level4=list_level4.pop()
        contribs_level4=list_level4.pop()
        dates_level4=list_level4.pop()
        
        list_level5=__process_contribs(contribs_level5_month, total_contribs)
        perc_contribs_level5=list_level5.pop()
        contribs_level5=list_level5.pop()
        dates_level5=list_level5.pop()
        
##    FIG 5 PLOT 4b
##    FIG 6 AVERAGE NUMBER OF EDITS PER USER PER MONTH FOR EACH LEVEL
##        RETRIEVE NUM USERS FOR EACH MONTH IN EACH LEVEL WHO HAVE MADE AT LEAST ONE CONTRIB
        num_users_1_month=dbaccess.query_SQL(acceso[1], select="COUNT(DISTINCT author)", tables="stats_Contrib_months_author_"+idioma, where=where_clause_level1, group="year, month")
        num_users_2_month=dbaccess.query_SQL(acceso[1], select="COUNT(DISTINCT author)", tables="stats_Contrib_months_author_"+idioma, where=where_clause_level2, group="year, month")
        num_users_3_month=dbaccess.query_SQL(acceso[1], select="COUNT(DISTINCT author)", tables="stats_Contrib_months_author_"+idioma, where=where_clause_level3, group="year, month")
        num_users_4_month=dbaccess.query_SQL(acceso[1], select="COUNT(DISTINCT author)", tables="stats_Contrib_months_author_"+idioma, where=where_clause_level4, group="year, month")
        num_users_5_month=dbaccess.query_SQL(acceso[1], select="COUNT(DISTINCT author)", tables="stats_Contrib_months_author_"+idioma, where=where_clause_level5, group="year, month")
        list_users_1_month=[]
        for element in num_users_1_month:
            list_users_1_month.append(int(element[0]))
        list_users_2_month=[]
        for element in num_users_2_month:
            list_users_2_month.append(int(element[0]))
        list_users_3_month=[]
        for element in num_users_3_month:
            list_users_3_month.append(int(element[0]))
        list_users_4_month=[]
        for element in num_users_4_month:
            list_users_4_month.append(int(element[0]))
        list_users_5_month=[]
        for element in num_users_5_month:
            list_users_5_month.append(int(element[0]))
        
##        DIVIDE TOT NUM CONTRIBS PER LEVEL PER MONTH BY THE NUM USERS FOR EACH MONTH IN EACH LEVEL
        avg_contribs_user_1_month=[]
        for contribmonth, usermonth in zip(contribs_level1, list_users_1_month):
            avg_contribs_user_1_month.append(float(contribmonth)/usermonth)
        avg_contribs_user_2_month=[]
        for contribmonth, usermonth in zip(contribs_level2, list_users_2_month):
            avg_contribs_user_2_month.append(float(contribmonth)/usermonth)
        avg_contribs_user_3_month=[]
        for contribmonth, usermonth in zip(contribs_level3, list_users_3_month):
            avg_contribs_user_3_month.append(float(contribmonth)/usermonth)
        avg_contribs_user_4_month=[]
        for contribmonth, usermonth in zip(contribs_level4, list_users_4_month):
            avg_contribs_user_4_month.append(float(contribmonth)/usermonth)
        avg_contribs_user_5_month=[]
        for contribmonth, usermonth in zip(contribs_level5, list_users_5_month):
            avg_contribs_user_5_month.append(float(contribmonth)/usermonth)
        
##        FIG 7 POPULATION GROWTH FOR EACH USER GROUP
##        SIMPLY RETRIEVE list_users_X_month
##        FIG 8 % OF TOTAL POPULATION OF EACH USER GROUP
        perc_users_1_months=[]
        perc_users_2_months=[]
        perc_users_3_months=[]
        perc_users_4_months=[]
        perc_users_5_months=[]
        for e1, e2, e3, e4, e5 in zip(list_users_1_month,list_users_2_month,list_users_3_month,list_users_4_month,list_users_5_month):
            total_users_month=e1+e2+e3+e4+e5
            perc_users_1_months.append((float(e1)/total_users_month))
            perc_users_2_months.append((float(e2)/total_users_month))
            perc_users_3_months.append((float(e3)/total_users_month))
            perc_users_4_months.append((float(e4)/total_users_month))
            perc_users_5_months.append((float(e5)/total_users_month))
            
###############################
##    FINAL DUTIES, TRANSFER DATA AND EXECUTE R SCRIPT
        filenames=["dates_admin_contrib.data","contribs_admins_months.data", "perc_contribs_months.data","dates_level1_contrib.data", "contribs_level1_months.data", "perc_contribs_level1_months.data", "dates_level2_contrib.data", "contribs_level2_months.data", "perc_contribs_level2_months.data","dates_level3_contrib.data", "contribs_level3_months.data", "perc_contribs_level3_months.data","dates_level4_contrib.data", "contribs_level4_months.data", "perc_contribs_level4_months.data","dates_level5_contrib.data" ,"contribs_level5_months.data", "perc_contribs_level5_months.data", "avg_contribs_user_1_month.data", "avg_contribs_user_2_month.data", "avg_contribs_user_3_month.data", "avg_contribs_user_4_month.data", "avg_contribs_user_5_month.data", "users_1_month.data", "users_2_month.data", "users_3_month.data", "users_4_month.data", "users_5_month.data", "perc_users_1_months.data","perc_users_2_months.data", "perc_users_3_months.data", "perc_users_4_months.data", "perc_users_5_months.data"]
        
        filenames_out=["Figure1.png", "Figure_2.png", "Figure4.png", "Figure5.png", "Figure6.png", "Figure7.png", "Figure8.png"]
        
        dataList=[dates_contribs, admins_contribs, perc_contribs_admins, dates_level1, contribs_level1, perc_contribs_level1,dates_level2, contribs_level2, perc_contribs_level2,dates_level3, contribs_level3, perc_contribs_level3, dates_level4, contribs_level4, perc_contribs_level4,dates_level5, contribs_level5, perc_contribs_level5, avg_contribs_user_1_month, avg_contribs_user_2_month, avg_contribs_user_3_month, avg_contribs_user_4_month, avg_contribs_user_5_month, list_users_1_month, list_users_2_month, list_users_3_month, list_users_4_month, list_users_5_month, perc_users_1_months, perc_users_2_months, perc_users_3_months, perc_users_4_months, perc_users_5_months]
        
        for filename, data in zip (filenames, dataList):
            if(filename.find('date')!=-1):
                f=open("./graphics/"+idioma+"/data/"+filename, 'w')
                for adate in data:
                    f.writelines(str(adate)+"\n")
                f.close()
            else:
                __makeDataFile(idioma, filename, data)
        
        #Pass data filenames to the GNU R script with a file
        f=open("./data/community_contrib_files_names.data",'w')
        for line in filenames:
            f.write("./graphics/"+idioma+"/data/"+line+"\n")
        f.close()
        
        #Idem with graphic output filenames
        f=open("./data/community_contrib_files_out.data",'w')
        for line in filenames_out:
            f.write("./graphics/"+idioma+"/"+line+"\n")
        f.close()
            
        #CALL GNU R SCRIPT measuring_Wiki.R
        
        succ=os.system("R --vanilla < ./community_contrib.R > debug_R")
        if succ==0:
            print "Funcion community_contrib.R ejecutada con exito para el lenguage... "+idioma

#####################################################################
## FUNCTIONAL METHODS FOR SEVERAL CONCRETE AND REPETITIVE JOBS
#####################################################################
def __process_contribs(contribs_level_month, total_contribs):
    dates_contribs=[]
    list_contribs_level=[]
    for element in contribs_level_month:
        dates_contribs.append(list(element[0:2]))
        list_contribs_level.append(int(element[2]))
##        REMEMBER TO PLOT the list contribs_level1 in FIG 5
    perc_contribs_level=[]
    for contrib_level, total_contrib in zip(list_contribs_level, total_contribs):
        perc_contribs_level.append((float(contrib_level)/total_contrib))
    return[dates_contribs, list_contribs_level, perc_contribs_level]

def __lorenz_Curve(values):
    """
    Uses RPY module to depict a Lorenz curve useful for GINI graphs
    
    @type  values: list of ints
    @param values: list of integers summarizing total contributions for each registered author
    """
    x_values=[]
    for i in range(0, len(values)+1):	
        x_values.append(100.0*(float(i)/len(values)))
    
    values.insert(0, 0)
    y_values_lorenz=[]
    for j in range(len(values)):
        y_values_lorenz.append(sum(values[0:j+1]))
    for k in range(len(y_values_lorenz)):
        y_values_lorenz[k]=100.0*(float(y_values_lorenz[k])/y_values_lorenz[len(y_values_lorenz)-1])
    
    g_coeff=__gini_Coef(values)
    r.plot(x_values, y_values_lorenz, xlab="(%)Authors",ylab="(%)Cumulative contribution", main="Cumulative distribution function", type="l", col=2)
    r.legend(10, 80, legend="Gini Coefficient = %f" % g_coeff)
    r.legend(10, 100, legend=r.c("Line of perfect equality", "Lorenz curve"), col=r.c(1,2), pch=r.c(1,2))
    r.lines(x_values, x_values)
    #r.lines(r.lowess(log(lista)))
    r.dev_off()

def _lorenz_Comp_Curves(values,flag=1):

    x_values=[]
    for i in range(0, len(values)+1):	
        x_values.append(100.0*(float(i)/len(values)))
    
    values.insert(0, 0)
    y_values_lorenz=[]
    for j in range(len(values)):
        y_values_lorenz.append(sum(values[0:j+1]))
    for k in range(len(y_values_lorenz)):
        y_values_lorenz[k]=100.0*(float(y_values_lorenz[k])/y_values_lorenz[len(y_values_lorenz)-1])
    
    g_coeff=__gini_Coef(values)
    if flag==0:
        r.plot(x_values, y_values_lorenz, xlab="(%)Authors",ylab="(%)Cumulative contribution", main="Cumulative distribution function", type="l", col=2)
##    r.legend(10, 80, legend="Gini Coefficient = %f" % g_coeff)
##    r.legend(10, 100, legend=r.c("Line of perfect equality", "Lorenz curve"), col=r.c(1,2), pch=r.c(1,2))
        r.lines(x_values, x_values)
    r.lines(x_values, y_values_lorenz)

def __gini_Coef(values, insert=False):
    """
    Plots a GINI graph for author contributions 
    
    @type  values: list of ints
    @param values: list of integers summarizing total contributions for each registered author
    @type  insert: boolean flag
    @param insert: warns the method about inserting a (0,0) tuple at the beginning of the graphic to depict an accurate curve
    """
    
    if insert:
        values.insert(0,0)
    sum_numerator=0
    sum_denominator=0
    for i in range(1, len(values)):
        sum_numerator+=(len(values)-i)*values[i]
        sum_denominator+=values[i]
    
    g_coeff= (1.0/(len(values)-1))*(len(values)-2*(sum_numerator/sum_denominator))
    return g_coeff

def __tup_to_list(result, flag=0):
    """
    A method to convert a tuple of bidimensional tuples return by a database query to a list
   of bidimensional lists we can use in other methods
    
    @type  result: tuple of bidimensional tuples
    @param result: the tuple received as a result of a database query
    @type  flag: int flag
    @param insert: indicates 0 (int, int) tuples; 1 (int, string) tuples; 2 (string, string) tuples
    """
##    NEED TO BE IMPROVED, UNNECESARY AUX VARIABLES, SEE PRUEBA.PY
    aux=list(result)
    for i in range(len(aux)):
        aux[i]=list(aux[i])
    listax=[]
    listay=[]
    for i in range(len(aux)):
        if flag==0:
            listax.append(int(aux[i][0]))
            listay.append(int(aux[i][1]))
        elif flag==1:
            listax.append(int(aux[i][0]))
            listay.append(aux[i][1])
        elif flag==2:
            listax.append(aux[i][0])
            listay.append(aux[i][1])
    return [listax, listay]

def __makeDataFile(idioma, filename, data):
    """
    Create data files to transfer results to GNU R
    
    @type  idioma: string
    @param idioma: indicates the language version we are processing
    @type  filename: string
    @param filename: name of the file to which we want to transfer data
    @type  data: list
    @param data: list of data we write in the file
    """
    f=open("./graphics/"+idioma+"/data/"+filename, 'w')
    for value in data:
        f.writelines(str(value)+"\n")
    f.close()

def __makeDatesFile(idioma, filename, dates):
    """
    Create files to transfer dates results to GNU R
    
    @type  idioma: string
    @param idioma: indicates the language version we are processing
    @type  filename: string
    @param filename: name of the file to which we want to transfer data
    @type  dates: list of string
    @param dates: list of dates we write in the file
    """
    f=open("./graphics/"+idioma+"/data/"+filename, 'w')
    for adate in dates:
        f.writelines(str(adate).split()[0]+"\n")
    f.close()
    
def create_dirs(idiomas):
    """
    Generates appropiate directory hierarchy to store graphics, data files and results files
    
    @type  idiomas: list of strings
    @param idioma: language versions we want to process
    """
    directorios=os.listdir("./")
    if ("graphics" not in directorios):
        os.makedirs("./graphics")
    else:
        dir_lang=os.listdir("./graphics/")
        for idioma in idiomas:
            if idioma not in dir_lang:
                os.makedirs("./graphics/"+idioma+"/data")
    if("data" not in directorios):
        os.makedirs("./data")

def work(idiomas):
    """
    Katapult function for the rest of the graphic methods in this module
    
    @type  idiomas: list of strings
    @param idiomas: indicates the language version we are processing
    """
    ##  idiomas=["eswiki"]
    create_dirs(idiomas)
    contributions(idiomas)
    histogram(idiomas)
    summary_evol(idiomas)
    measuring(idiomas)
    community_contrib(idiomas)
##idiomas=["dawiki", "skwiki", "idwiki", "slwiki", "srwiki", "bgwiki", "ltwiki", "rowiki", "trwiki", "etwiki", "hrwiki"]
##idiomas=["frwiki", "dewiki"]
##work(idiomas)
"""
def testcomp():
    comparative_contributions()

testcomp()
"""
