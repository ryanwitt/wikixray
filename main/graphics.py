from rpy import *
import dbaccess, math, os

#SE DEBEN TOMAR LOS VALORES GENERALES DE IDIOMAS DEL FICHERO DE CONFIGURACION COMUN DE LA APLICACION
#SE DEBEN GENERAR SUBDIRECTORIOS INDEPENDIENTES EN EL DIRECTORIO GRAPHICS PARA ALMACENAR LOS RESULTADOS DE CADA IDIOMA

def contributions(idiomas):
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
	filenames=["boxplot_log.png", "histogram_log.png", "histogram_log_low.png", "histogram_log_high.png", "ecdf_log_low.png", "ecdf_log_high.png", "data/page_len_log.data", "/data/histograms.info", "ecdf_total.png"]
	
	for idioma in idiomas:
		print "Creando histogramas para el idioma ... "+idioma
		#IMPRIMIR A OTRO ARCHIVO LOS NOMBRES DE ARCHIVOS DE GRAFICOS, SEGUN EL ORDEN DEL SCRIPT DE R histogram.R
		f=open("./data/hist_files_names.data",'w')
		for line in filenames:
			f.write("./graphics/"+idioma+"/"+line+"\n")
		f.close()
		acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", idioma+"_tab_page")
	
		#ESTIMANDO SOLO LAS PAGINAS QUE CORRESPONDEN A ARTICULOS, CON NAMESPACE=MAIN=0
		#dbaccess.dropTab_SQL(acceso[1], "aux")
		#dbaccess.query_SQL(acceso[1],"page_id, page_len","page", where="page_namespace=0", order="page_len", create="aux")
		result=dbaccess.query_SQL(acceso[1], "page_id, page_len", "aux")
		dbaccess.close_Connection(acceso[0])
		data=__tup_to_list(result)
		page_len=data.pop()
		for i in range(len(page_len)):
			if page_len[i]!=0:
				page_len[i]=math.log10(page_len[i])
		
		#IMPRIMIR A OTRO ARCHIVO la lista con los valores de tamaño de pagina con los que hacer los histogramas
		f=open("./graphics/"+idioma+"/data/page_len_log.data", 'w')
		for value in page_len:
			f.writelines(str(value)+"\n")
		f.close()
		
		#LLAMAR A LA FUNCION Histogram.R
		succ=os.system("R --vanilla < ./histogram.R > debug_R")
		if succ==0:
			print "Funcion histogram ejecutada con exito para el lenguage... "+idioma
		

def summary_evol(idiomas):

##	Mucho cuidado al seleccionar los valores de la tabla de evolucion en numero de articulos, tam, etc.
##  Se debe seleccionar por si acaso procede, siempre como GROUP BY(pageCount, limitDate), ya que 
##  en periodos de inactiviad se repetiran algunas entradas en la tabla
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
        
        data2=__tup_to_list(result2, 1)
        dates_x=data2.pop()
        page_Len_Sum=data2.pop()
        
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

##  Introducir en la lista de datos los resultados de las queries en el orden adecuado
##  de forma que coincidan con los nombres de ficheros que pasamos a R      
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
        
        #Pasar los nombres de los archivos al script de R a través de un archivo
        f=open("./data/summary_files_names.data",'w')
        for line in filenames:
            f.write("./graphics/"+idioma+"/data/"+line+"\n")
        f.close()
        
        #Idem con los archivos de salida gráfica
        f=open("./data/summary_files_out.data",'w')
        for line in filenames_out:
            f.write("./graphics/"+idioma+"/"+line+"\n")
        f.close()
            
        #LLAMAR A LA FUNCION summary_evol.R
        
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
        
##        Ordenamos los resultados para que se puedan ajustar a una Power Law
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
        
        #Pasar los nombres de los archivos al script de R a través de un archivo
        f=open("./data/measuring_files_names.data",'w')
        for line in filenames:
            f.write("./graphics/"+idioma+"/data/"+line+"\n")
        f.close()
        
        #Idem con los archivos de salida gráfica
        f=open("./data/measuring_files_out.data",'w')
        for line in filenames_out:
            f.write("./graphics/"+idioma+"/"+line+"\n")
        f.close()
            
        #LLAMAR A LA FUNCION measuring_Wiki.R
        
        succ=os.system("R --vanilla < ./measuring_Wiki.R > debug_R")
        if succ==0:
            print "Funcion summary_evol ejecutada con exito para el lenguage... "+idioma
    
#####################################################################
## FUNCTIONAL METHODS FOR SEVERAL CONCRETE AND REPETITIVE JOBS
#####################################################################
    
def __lorenz_Curve(values):
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
            listay.append(aux[i][1])
            listay.append(aux[i][1])
    return [listax, listay]

def __makeDataFile(idioma, filename, data):
		f=open("./graphics/"+idioma+"/data/"+filename, 'w')
		for value in data:
			f.writelines(str(value)+"\n")
		f.close()

def __makeDatesFile(idioma, filename, dates):
        f=open("./graphics/"+idioma+"/data/page_dates.data", 'w')
        for adate in dates:
            f.writelines(str(adate).split()[0]+"\n")
        f.close()
        
def create_dirs(idiomas):
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

def work():
    ##	idiomas=["eswiki","svwiki", "itwiki", "ptwiki", "nlwiki", "plwiki", "dewiki"]
    idiomas=["eswiki"]
    create_dirs(idiomas)
    ##	contributions(idiomas)
    ##	histogram(idiomas)
##    summary_evol(idiomas)
    measuring(idiomas)
    
work()
