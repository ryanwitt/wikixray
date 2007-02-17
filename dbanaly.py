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
Creates additional database tables with relevant quantitative data (including
evolution in time for important parameters).

@see: quantAnalay_main

@authors: Jose Felipe Ortega
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jfelipe@gsyc.escet.urjc.es
"""

import dbaccess, datetime
#import gnuplotter

def info_authors(conf, language="furwiki"):
	"""
	Método para el tratamiento de datos por usuario
	"""
	#Obtener una conexion a la BD que corresponda
	acceso = dbaccess.get_Connection("localhost", 3306, conf.msqlu, conf.msqlp, language+conf.dumptype.lstrip("dump"))
	
	#Variables de configuracion locales
	target="author"
	intervals=["days", "weeks", "months", "quarters", "years"]
	
	############################
	#NUMERO DE REVISIONES TOTALES POR CADA ID DE AUTOR
	
	__total_rev(acceso[1], language, target)
	
	############################
	#NUMERO TOTAL DE ARTÍCULOS DIFERENTES QUE HA REVISADO UN AUTOR
	
	__total_rev_per_target(acceso[1], language, target)
	
	############################
	#NUMERO TOTAL DE ARTICULOS DIFERENTES QUE HA COMENZADO UN AUTOR
	#Se considera como comienzo la primera revision de un articulo????
	__total_article_init_author(acceso[1], language)
	
	############################
	#REVISIONES TOTALES DE CADA ID DE AUTOR PARA VARIOS INTERVALOS ESPECIFICADOS EN INTERVALS
	
	for interval in intervals:
		__total_rev_time(acceso[1], interval,language, target)
	
	############################
	#NUMERO DE ARTÍCULOS DIFERENTES QUE HA REVISADO UN AUTOR, PARA VARIOS INTERVALOS ESPECIFICADOS EN INTERVALS
	
	for interval in intervals:
		__total_rev_per_target_time(acceso[1], interval,language, target)
	
	############################
	#NUMERO DE ARTICULOS DIFERENTES QUE HA COMENZADO UN AUTOR, POR MESES SEMANAS Y DIAS (años, trimestres...)
	#Se considera como comienzo la primera revision de un articulo
	
	for interval in intervals:
		__article_init_author_time(acceso[1], interval,language)

	#Cerramos la base de datos
	dbaccess.close_Connection(acceso[0])
		
def info_articles(conf, language="furwiki"):
	"""
	Método para el tratamiento de datos por articulo
	"""
	#Obtener una conexion a la BD que corresponda
	acceso = dbaccess.get_Connection("localhost", 3306, conf.msqlu, conf.msqlp, language+conf.dumptype.lstrip("dump"))
	
	#Variables de configuracion locales
	target="page_id"
	intervals=["days", "weeks", "months", "quarters", "years"]
	
	###########################
	#REVISIONES TOTALES POR CADA ID DE ARTICULO
	###########################
	__total_rev(acceso[1], language, target)
	
	###########################
	#NUMERO TOTAL DE AUTORES DISTINTOS QUE HAN REVISADO UN ARTÍCULO
	__total_rev_per_target(acceso[1], language, target)
	
	###########################
	#REVISIONES TOTALES POR CADA ARTICULO x meses, semanas y dias
	for interval in intervals:
		__total_rev_time(acceso[1], interval,language, target)
	
	###########################
	#NUMERO DE AUTORES DISTINTOS QUE HAN REVISADO UN ARTÍCULO x meses, semanas y dias
	for interval in intervals:
		__total_rev_per_target_time(acceso[1], interval,language, target)
	
	#Cerramos la base de datos
	dbaccess.close_Connection(acceso[0])


def info_contents(conf, language="furwiki"):
	
	###########################
	#ANALISIS DEl CONTENIDO
	###########################
	##PODEMOS VER LA EVOLUCION DEL TAMAÑO DE LOS ARTICULOS USANDO page.page_len (tam articulo sin comprimir)
	##Tamaños de contribuciones ¿?
	acceso = dbaccess.get_Connection("localhost", 3306, conf.msqlu, conf.msqlp, language+conf.dumptype.lstrip("dump"))
	__content_evolution(acceso[1], language)
	dbaccess.close_Connection(acceso[0])
	#DATOS POR ARTICULO

def flux_capacitor(conf, language="furwiki"):
	"""
	Metodo para crear una tabla en la base de datos con la informacion relevante para los analisis
	Tambien se encarga de convertir los timestamp de las revisiones al tipo DATE de MySQL
	
	Finalmente, se encarga de crear las tablas para los resultados intermedios, de manera que luego se 
	puedan introducir directamente los datos al hacer la query en el metodo correspondiente
	"""
	#Obtener una conexion a la BD que corresponda
	acceso = dbaccess.get_Connection("localhost", 3306, conf.msqlu, conf.msqlp, language+conf.dumptype.lstrip("dump"))
	dbaccess.dropTab_SQL(acceso[1], "stats_"+language)
	dbaccess.raw_query_SQL(acceso[1], "CREATE TABLE stats_" + language + " SELECT rev_id, page_id, page_title, page_namespace, page_len, rev_user AS author, rev_user_text AS author_text, rev_timestamp FROM revision, page WHERE rev_page=page_id")
	
	dbaccess.raw_query_SQL(acceso[1],"ALTER TABLE stats_"+language+" MODIFY rev_timestamp DATETIME")
	dbaccess.raw_query_SQL(acceso[1],"ALTER TABLE stats_"+language+" ADD INDEX timestamp (rev_timestamp)")
	
	##TABLAS PARA RESULTADOS INTERMEDIOS
	#Cerramos la base de datos
	dbaccess.close_Connection(acceso[0])

#################################
#METODOS PRIVADOS DE AUTORES Y ARTICULOS
#################################

def __total_rev(cursor, language, target="author"):
	#target=author Contribuciones por cada usuario sin anonimos
	#target=article Contribuciones por cada artículo, sin incluir revisores anonimos
	dbaccess.dropTab_SQL(cursor, "stats_Contrib_NoAnnons_"+target+"_"+language)
	Total_Contrib_NoAnnons=dbaccess.query_SQL(cursor,target+", count(*) AS theCount","stats_"+language,"page_namespace=0 AND author NOT LIKE '0'","theCount", target, "stats_Contrib_NoAnnons_"+target+"_"+language+" ")
	#Idem con anonimos integrados
	dbaccess.dropTab_SQL(cursor, "stats_Contrib_"+target+"_"+language)
	Total_Contrib=dbaccess.query_SQL(cursor, target+", count(*) AS theCount","stats_"+language, where="page_namespace=0", order="theCount", group=target, create="stats_Contrib_"+target+"_"+language+" ")

	if target == "author":
		target = "author_text"
	#Idem solo anonimos clasificados por IP
	dbaccess.dropTab_SQL(cursor, "stats_Contrib_Annons_"+target+"_"+language)
	Total_Contrib_Annons=dbaccess.query_SQL(cursor, target+", count(*) AS theCount","stats_"+language, "page_namespace=0 AND author='0'",order="theCount", group=target, create="stats_Contrib_Annons_"+target+"_"+language+" ")
	
	
def __total_rev_per_target(cursor, language, target="author"):
	"""
	target=author Recupera el numero total de articulos diferentes que ha revisado cada autor hasta la fecha actual
	
	target=article Recupera el numero total de autores diferentes que ha revisado cada articulo hasta la fecha actual
	"""
	if target=="author":
		field_distinct="page_id"
	elif target=="page_id":
		field_distinct="author"
	dbaccess.dropTab_SQL(cursor, "stats_Article_NoAnnons_"+target+"_"+language)	
	total_Article_NoAnnons=dbaccess.query_SQL(cursor, target+", COUNT(DISTINCT "+field_distinct+") AS theCount","stats_"+language,"page_namespace=0 AND author NOT LIKE '0'","theCount", target, "stats_Article_NoAnnons_"+target+"_"+language+" ")
	
	dbaccess.dropTab_SQL(cursor, "stats_Article_"+target+"_"+language)
	total_Article=dbaccess.query_SQL(cursor, target+", COUNT(DISTINCT "+field_distinct+") AS theCount","stats_"+language, where="page_namespace=0", order="theCount", group=target, create="stats_Article_"+target+"_"+language+" ")
	
	if target == "author":
		target = "author_text"
	
	dbaccess.dropTab_SQL(cursor, "stats_Article_Annons_"+target+"_"+language)
	total_Article_Annons=dbaccess.query_SQL(cursor, target+", COUNT(DISTINCT "+field_distinct+") AS theCount","stats_"+language,"page_namespace=0 AND author='0'","theCount", target, "stats_Article_Annons_"+target+"_"+language+" ")
	#print total_Distinct_Article_NoAnnons

def __total_article_init_author(cursor, language, target="author"):
	"""
	#NUMERO TOTAL DE ARTICULOS DIFERENTES QUE HA COMENZADO UN AUTOR en el idioma estudiado
	#Se considera como comienzo la primera revision de un articulo????
	"""
	"""
	Creacion de una tabla intermedia para almacenamiento de los datos precisos para las queries de esta funcion
	"""
	dbaccess.dropTab_SQL(cursor, "stats_Article_Min_Timestamp")
	min_Timestamp = dbaccess.query_SQL(cursor, "page_id, MIN(rev_timestamp) AS ts", "stats_"+language, where="page_namespace=0",group="page_id", create="stats_Article_Min_Timestamp")
	
	dbaccess.dropTab_SQL(cursor, "stats_Article_Init_NoAnnons_"+target+"_"+language)
	total_Article_Init_NoAnnons= dbaccess.query_SQL(cursor, target+", COUNT(*) AS theCount", "stats_"+language+" t1, stats_Article_Min_Timestamp t2", "t1.page_namespace=0 AND t1.page_id=t2.page_id AND t1.rev_timestamp=t2.ts AND t1.author NOT LIKE '0'", order="theCount", group=target, create="stats_Article_Init_NoAnnons_"+target+"_"+language+" ")
	
	dbaccess.dropTab_SQL(cursor, "stats_Article_Init_"+target+"_"+language)
	total_Article_Init= dbaccess.query_SQL(cursor, target+", COUNT(*) AS theCount", "stats_"+language+" t1, stats_Article_Min_Timestamp t2", "t1.page_namespace=0 AND t1.page_id=t2.page_id AND t1.rev_timestamp=t2.ts", order="theCount", group=target, create="stats_Article_Init_"+target+"_"+language+" ")
	
	if target == "author":
		target = "author_text"
	dbaccess.dropTab_SQL(cursor, "stats_Article_Init_Annons_"+target+"_"+language)
	total_Article_Init_Annons= dbaccess.query_SQL(cursor, target+", COUNT(*) AS theCount", "stats_"+language+" t1, stats_Article_Min_Timestamp t2", "t1.page_namespace=0 AND t1.page_id=t2.page_id AND t1.rev_timestamp=t2.ts AND t1.author='0'", order="theCount", group=target, create="stats_Article_Init_Annons_"+target+"_"+language+" ")
	#print total_Article_Init_NoAnnons
	
def __total_rev_time(cursor,interval,language, target="author"):
	"""
	target=author Numero total de revisiones realizadas por un autor desglosada en intervalos temporales
	
	target=article Numero total de revisiones sufridas por un articulo desglosada en intervalos temporales
	"""
	type_interval_select={"days":"DAYOFYEAR(rev_timestamp) AS day, YEAR(rev_timestamp) AS year ", "weeks":"WEEK(rev_timestamp,1) AS week, YEAR(rev_timestamp) AS year ", "months":"MONTH(rev_timestamp) AS month, YEAR(rev_timestamp) AS year ", "quarters":"QUARTER(rev_timestamp) AS quarter, YEAR(rev_timestamp) AS year ", "years":"YEAR(rev_timestamp) AS year "}
	type_interval_group={"days":"year, day", "weeks":"year, week", "months":"year, month", "quarters":"year, quarter", "years":"year"}
	
	if interval in type_interval_select:
		dbaccess.dropTab_SQL(cursor, "stats_Contrib_NoAnnons_"+interval+"_"+target+"_"+language)
		total_rev_author_time_NoAnnons= dbaccess.query_SQL(cursor, target+", " + type_interval_select[interval] + ", COUNT(*)", "stats_"+language, "page_namespace=0 AND author NOT LIKE '0'", group= target+", " + type_interval_group[interval], create="stats_Contrib_NoAnnons_"+interval+"_"+target+"_"+language+" ")
		
		dbaccess.dropTab_SQL(cursor, "stats_Contrib_"+interval+"_"+target+"_"+language)
		total_rev_author_time= dbaccess.query_SQL(cursor, target+", " + type_interval_select[interval] + ", COUNT(*)", "stats_"+language, where="page_namespace=0",group= target+", " + type_interval_group[interval], create="stats_Contrib_"+interval+"_"+target+"_"+language+" ")
		
		if target == "author":
			target = "author_text"
		dbaccess.dropTab_SQL(cursor, "stats_Contrib_Annons_"+interval+"_"+target+"_"+language)
		total_rev_author_time_Annons= dbaccess.query_SQL(cursor, target+", " + type_interval_select[interval] + ", COUNT(*)", "stats_"+language, "page_namespace=0 AND author='0'", group= target+", " + type_interval_group[interval], create="stats_Contrib_Annons_"+interval+"_"+target+"_"+language+" ")
	else:
		print "Has escogido un intervalo temporal no soportado"
	
def __total_rev_per_target_time(cursor,interval,language, target="author"):
	"""
	target = author Recupera el numero total de articulos diferentes que ha revisado cada autor hasta la fecha actual
	desglosando la info en intervalos temporales
	
	target = article Recupera el numero total de autores diferentes que han revisado un artículo hasta la fecha actual,
	desglosando la info en intervalos temporales
	"""
	type_interval_select={"days":"DAYOFYEAR(rev_timestamp) AS day, YEAR(rev_timestamp) AS year ", "weeks":"WEEK(rev_timestamp,1) AS week, YEAR(rev_timestamp) AS year ", "months":"MONTH(rev_timestamp) AS month, YEAR(rev_timestamp) AS year ", "quarters":"QUARTER(rev_timestamp) AS quarter, YEAR(rev_timestamp) AS year ", "years":"YEAR(rev_timestamp) AS year "}
	type_interval_group={"days":"year, day", "weeks":"year, week", "months":"year, month", "quarters":"year, quarter", "years":"year"}
	
	if target=="author":
		field_distinct="page_id"
	elif target=="page_id":
		field_distinct="author"

	if interval in type_interval_select:
		
		dbaccess.dropTab_SQL(cursor, "stats_Article_NoAnnons_"+interval+"_"+target+"_"+language)
		article_rev_author_time_NoAnnons= dbaccess.query_SQL(cursor, target+", COUNT(DISTINCT "+field_distinct+") AS theCount, " + type_interval_select[interval] + " ", "stats_"+language, "page_namespace=0 AND author NOT LIKE '0'", group= target+", " + type_interval_group[interval], create="stats_Article_NoAnnons_"+interval+"_"+target+"_"+language+" ")
		
		dbaccess.dropTab_SQL(cursor, "stats_Article_"+interval+"_"+target+"_"+language)
		article_rev_author_time= dbaccess.query_SQL(cursor, target+", COUNT(DISTINCT "+field_distinct+") AS theCount, " + type_interval_select[interval] + " ", "stats_"+language, where="page_namespace=0",group= target+", " + type_interval_group[interval], create="stats_Article_"+interval+"_"+target+"_"+language+" ")
		
		if target == "author":
			target = "author_text"
		
		dbaccess.dropTab_SQL(cursor, "stats_Article_Annons_"+interval+"_"+target+"_"+language)
		article_rev_author_time_Annons= dbaccess.query_SQL(cursor, target+", COUNT(DISTINCT "+field_distinct+") AS theCount, " + type_interval_select[interval] + " ", "stats_"+language, "page_namespace=0 AND author='0'", group= target+", " + type_interval_group[interval], create="stats_Article_Annons_"+interval+"_"+target+"_"+language+" ")
	else:
		print "Has escogido un intervalo temporal no soportado"

def __article_init_author_time(cursor,interval,language, target="author"):
	"""
	#NUMERO TOTAL DE ARTICULOS DIFERENTES QUE HA COMENZADO UN AUTOR en el idioma estudiado
	#Desglosando la info en intervalos temporales
	"""
	
	"""
	############################################
	¡¡¡¡¡WARNING!!!!!!
	Es necesario llamar con anterioridad al metodo __total_article_init_author puesto que de otro modo no se crea la tabla temporal
	intermedia para que funcione este metodo
	############################################
	"""
	
	type_interval_select={"days":"DAYOFYEAR(rev_timestamp) AS day, YEAR(rev_timestamp) AS year ", "weeks":"WEEK(rev_timestamp,1) AS week, YEAR(rev_timestamp) AS year ", "months":"MONTH(rev_timestamp) AS month, YEAR(rev_timestamp) AS year ", "quarters":"QUARTER(rev_timestamp) AS quarter, YEAR(rev_timestamp) AS year ", "years":"YEAR(rev_timestamp) AS year "}
	type_interval_group={"days":"year, day", "weeks":"year, week", "months":"year, month", "quarters":"year, quarter", "years":"year"}
	
	if interval in type_interval_select:
		
		dbaccess.dropTab_SQL(cursor, "stats_Article_Init_NoAnnons_"+interval+"_"+target+"_"+language)
		total_rev_author_time_NoAnnons= dbaccess.query_SQL(cursor, target+", " + type_interval_select[interval] + ", COUNT(*)",  "stats_"+language+" t1, stats_Article_Min_Timestamp t2", "t1.page_namespace=0 AND t1.page_id=t2.page_id AND t1.rev_timestamp=t2.ts AND t1.author NOT LIKE '0'", group= target+", " + type_interval_group[interval], create="stats_Article_Init_NoAnnons_"+interval+"_"+target+"_"+language+" ")
		
		dbaccess.dropTab_SQL(cursor, "stats_Article_Init_"+interval+"_"+target+"_"+language)
		total_rev_author_time= dbaccess.query_SQL(cursor, target+", " + type_interval_select[interval] + ", COUNT(*)",  "stats_"+language+" t1, stats_Article_Min_Timestamp t2", "t1.page_namespace=0 AND t1.page_id=t2.page_id AND t1.rev_timestamp=t2.ts ", group= target+", " + type_interval_group[interval], create="stats_Article_Init_"+interval+"_"+target+"_"+language+" ")
		
		if target == "author":
			target = "author_text"
		
		dbaccess.dropTab_SQL(cursor, "stats_Article_Init_Annons_"+interval+"_"+target+"_"+language)
		total_rev_author_time_Annons= dbaccess.query_SQL(cursor, target+", " + type_interval_select[interval] + ", COUNT(*)",  "stats_"+language+" t1, stats_Article_Min_Timestamp t2", "t1.page_namespace=0 AND t1.page_id=t2.page_id AND t1.rev_timestamp=t2.ts AND author='0'", group= target+", " + type_interval_group[interval], create="stats_Article_Init_Annons_"+interval+"_"+target+"_"+language+" ")
	else:
		print "Has escogido un intervalo temporal no soportado"

###########################################################

def __content_evolution(cursor, language="furwiki"):
	
	####################
	#MEJORA PARA LA VELOCIDAD DE ACCESO
	####################
	
	dbaccess.dropTab_SQL(cursor, "stats_"+language+"_NS0")
	dbaccess.raw_query_SQL(cursor, "CREATE TABLE stats_" + language + "_NS0 " " SELECT rev_id, page_id, page_len,rev_timestamp FROM revision, page WHERE rev_page=page_id AND page_namespace=0")
	
	dbaccess.raw_query_SQL(cursor,"ALTER TABLE stats_"+language+"_NS0 ADD PRIMARY KEY (rev_id)")
	dbaccess.raw_query_SQL(cursor,"ALTER TABLE stats_"+language+"_NS0 MODIFY rev_timestamp DATETIME")
	dbaccess.raw_query_SQL(cursor,"ALTER TABLE stats_"+language+"_NS0 ADD INDEX pid (page_id)")
	dbaccess.raw_query_SQL(cursor,"ALTER TABLE stats_"+language+"_NS0 ADD INDEX timestamp (rev_timestamp)")
	
	#dbaccess.dropTab_SQL(cursor, "stats_Evolution_Content_weeks_"+language)
	fecha=dbaccess.query_SQL(cursor,"MIN(rev_timestamp)", "stats_"+language)
	fecha_min=fecha[0][0]
	fecha=dbaccess.query_SQL(cursor,"MAX(rev_timestamp)", "stats_"+language)
	fecha_max=fecha[0][0]
	
	#delta=datetime.timedelta(weeks=1)
	#fecha=fecha_min
	#fecha+=delta
	
	#dbaccess.query_SQL(cursor,"COUNT(DISTINCT stats.page_id) AS pageCount, SUM(a.page_len) AS pageLenSum, COUNT(stats.rev_id) contribs, MAX(stats.rev_timestamp) AS limitDate","stats_"+language+" stats, aux a", where="stats.page_namespace=0 AND a.page_namespace=0 AND stats.page_id=a.page_id AND stats.rev_timestamp < '"+fecha.isoformat(' ')+"'", create="stats_Evolution_Content_weeks_"+language+" ")
	
	#dbaccess.query_SQL(cursor,"COUNT(DISTINCT page_id) AS pageCount, SUM(page_len) AS pageLenSum, COUNT(rev_id) contribs, MAX(rev_timestamp) AS limitDate","stats_"+language+"_NS0 ", where="rev_timestamp < '"+fecha.isoformat(' ')+"'", create="stats_Evolution_Content_weeks_"+language+" ")
	#while (fecha<=fecha_max):
		#fecha+=delta
		
		#dbaccess.query_SQL(cursor,"COUNT(DISTINCT stats.page_id) AS pageCount, SUM(a.page_len) AS pageLenSum, COUNT(stats.rev_id) contribs, MAX(stats.rev_timestamp) AS limitDate","stats_"+language+" stats, aux a", where="stats.page_namespace=0 AND a.page_namespace=0 AND stats.page_id=a.page_id AND stats.rev_timestamp < '"+fecha.isoformat(' ')+"'", insert="stats_Evolution_Content_weeks_"+language+" ")
		
		#dbaccess.query_SQL(cursor,"COUNT(DISTINCT page_id) AS pageCount, SUM(page_len) AS pageLenSum, COUNT(rev_id) contribs, MAX(rev_timestamp) AS limitDate","stats_"+language+"_NS0 ", where="rev_timestamp < '"+fecha.isoformat(' ')+"'", insert="stats_Evolution_Content_weeks_"+language+" ")
	
	#dbaccess.dropTab_SQL(cursor, "stats_Evolution_Content_months_"+language)
	dbaccess.dropTab_SQL(cursor, "stats_Evolution_authors_months_"+language)
	delta=datetime.timedelta(weeks=4)
	fecha=fecha_min
	fecha+=delta
	
	dbaccess.query_SQL(cursor,"COUNT(DISTINCT stats.page_id) AS pageCount, SUM(a.page_len) AS pageLenSum, COUNT(stats.rev_id) contribs, MAX(stats.rev_timestamp) AS limitDate","stats_"+language+"_NS0 stats, aux a", where="stats.page_id=a.page_id AND stats.rev_timestamp < '"+fecha.isoformat(' ')+"'", create="stats_Evolution_Content_months_"+language+" ")
	
	#dbaccess.query_SQL(cursor,"COUNT(DISTINCT page_id) AS pageCount, SUM(page_len) AS pageLenSum, COUNT(rev_id) contribs, MAX(rev_timestamp) AS limitDate","stats_"+language+"_NS0 ", where="rev_timestamp < '"+fecha.isoformat(' ')+"'", create="stats_Evolution_Content_months_"+language+" ")
	dbaccess.query_SQL(cursor, "COUNT(DISTINCT rev_user) as authors", "revision", where="rev_user NOT LIKE 0 AND rev_timestamp < '"+fecha.isoformat(' ')+"'", create="stats_Evolution_author_months_"+language+" ")
	while (fecha<=fecha_max):
		fecha+=delta
		
		dbaccess.query_SQL(cursor,"COUNT(DISTINCT stats.page_id) AS pageCount, SUM(a.page_len) AS pageLenSum, COUNT(stats.rev_id) contribs, MAX(stats.rev_timestamp) AS limitDate","stats_"+language+"_NS0 stats, aux a", where="stats.page_id=a.page_id AND stats.rev_timestamp < '"+fecha.isoformat(' ')+"'", insert="stats_Evolution_Content_months_"+language+" ")
		dbaccess.query_SQL(cursor, "COUNT(DISTINCT rev_user) as authors", "revision", where="rev_user NOT LIKE 0 AND rev_timestamp < '"+fecha.isoformat(' ')+"'", insert="stats_Evolution_author_months_"+language+" ")
		
		#dbaccess.query_SQL(cursor,"COUNT(DISTINCT page_id) AS pageCount, SUM(page_len) AS pageLenSum, COUNT(rev_id) contribs, MAX(rev_timestamp) AS limitDate","stats_"+language+"_NS0 ", where="rev_timestamp < '"+fecha.isoformat(' ')+"'", insert="stats_Evolution_Content_months_"+language+" ")
	
	
	#DISTRIBUCION DE PAGINAS ENTRE LOS DISTINTOS NAMESPACES
	dbaccess.dropTab_SQL(cursor, "stats_nspace_"+language)
	dbaccess.query_SQL(cursor,"page_namespace as namespace, COUNT(*) as pages_nspace", "page", group="page_namespace", create="stats_nspace_"+language)

	#TAMAÑO DE PAGINA Y NUMERO DE AUTORES DISTINTOS QUE LA HAN EDITADO

	dbaccess.dropTab_SQL(cursor, "stats_pagelen_difauthors_"+language)
	dbaccess.query_SQL(cursor,"p.page_id, p.page_len, st.theCount as authors", "aux as p, stats_Article_NoAnnons_page_id_"+language+" as st", where="p.page_id=st.page_id", create="stats_pagelen_difauthors_"+language)

def test_funciones(conf, language="furwiki"):
	acceso = dbaccess.get_Connection("localhost", 3306, conf.msqlu, conf.msqlp, language+conf.dumptype.lstrip("dump"))
	"""
	targets=["page_id"]
	for target in targets:
		__total_rev(acceso[1], language, target)
		__total_rev_per_target(acceso[1], language, target)
		__total_rev_time(acceso[1],"years",language, target)
		__total_rev_per_target_time(acceso[1],"years",language, target)
	__total_article_init_author(acceso[1], language)
	__article_init_author_time(acceso[1],"years",language)
	"""	
		#__article_rev_author_time(acceso[1], "years", language)
	#__total_rev_time(acceso[1],"months",language, "page_id")
	#__total_article_init_author(acceso[1], language, target="author")
	__content_evolution(acceso[1], language)
	dbaccess.close_Connection(acceso[0])
"""
####################
#Escritura de datos a un archivo
####################
myfile = open('archivo.txt', 'w')
for row in TotalContrib_NoAnnons:
	myfile.write("%d\t%d\n"%(row[0],row[1]))
myfile.close()
####################
"""
