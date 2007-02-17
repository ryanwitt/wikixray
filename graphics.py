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
import dbaccess, math, os

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
            #LINKSTABLES MAY HELP, but in these dump versions they are all empty!!!
            
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
            print "Funcion measuring.R ejecutada con exito para el lenguage... "+idioma
    
#####################################################################
## FUNCTIONAL METHODS FOR SEVERAL CONCRETE AND REPETITIVE JOBS
#####################################################################
    
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
    r.dev_off()
    #r.lines(r.lowess(log(lista)))
    
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
    f=open("./graphics/"+idioma+"/data/page_dates.data", 'w')
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
##idiomas=["dawiki", "skwiki", "idwiki", "slwiki", "srwiki", "bgwiki", "ltwiki", "rowiki", "trwiki", "etwiki", "hrwiki"]
##idiomas=["frwiki", "dewiki"]
##work(idiomas)
