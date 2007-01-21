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
Module for downloading database dump for each langauge version we want to 
analyze. Once downloaded in 7zip format (storage optimization), we decompress the
dump to a local MySQL database.

This way, we have prepared the database for the next steps in the quantitative
analysis process.

@see: quantAnalay_main

@authors: Jose Felipe Ortega
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jfelipe@gsyc.escet.urjc.es
"""

import os, datetime, dbaccess

def download_bd (conf, language="furwiki"):
	# Recibe como parámetro el idioma que queremos descargar
	# La funcion usará w-get para descubrir la última versión correcta del volcado de ese idioma
	
	str_types={"dump_pages":"pages-meta-history.xml.7z", "dump_stub":"stub-meta-history.xml.gz"}
	
	#Fecha adecuada para la versión del dump a descargar
	#Si no existe dump para esa fecha, vamos hacia atrás hasta recoger el último disponible
	#date_object=datetime.date.today()
	#str_date=date_object.isoformat().replace("-","")
	#delta=datetime.timedelta(days=1)
	fetched_d=False
	#url="http://download.wikimedia.org/"+language+"/"+str_date+"/"+language+"-"+str_date+"-"+str_types.get(conf.dumptype)
	url="http://download.wikimedia.org/"+language+"/latest/"+language+"-latest-"+str_types.get(conf.dumptype)
	#pattern="http://download.wikimedia.org/furwiki/20060921/furwiki-20060921-pages-meta-history.xml.7z"
	#http://download.wikimedia.org/amwiki/20061014/amwiki-20061014-stub-meta-history.xml.gz
	while not fetched:
		print "Tratando de recuperar el archivo... "+url+"\n"
		#print pattern
		success=os.system("wget -P dumps -o log_"+language+" --ignore-length "+url)
		if success== 0:
			fetched_d=True
			#return (language+"-"+str_date+"-"+str_types.get(conf.dumptype))
			return (language+"-latest-"+str_types.get(conf.dumptype))
		else:
			print "FALLO EN recuperacion del archivo latest para el lenguage --- "+language
			#date_object-=delta
			#str_date_old=str_date
			#str_date=date_object.isoformat().replace("-","")
			#url=url.replace(str_date_old,str_date)
			
		print "status= %i" % success	

def unzip_bd (conf, filename, language="furwiki"):
	# Recibe como parámetro el idioma que queremos descomprimir
	ok=__init_bd(conf, language)
	#print "traza ok = %i \n" % ok	
	if ok == 0:
		print("BD inicializada, descomprimiendo archivos...")
		if conf.dumptype=="dump_pages":
			# La funcion llama al script de descompresión y pasa a traves de un pipe la info a mwdumper y de ahí a MySQL
			command="7za e -so dumps/"+filename+ " | "+conf.jpath+" -jar "+conf.mwpath+" --format=sql:1.5 | mysql -u "+conf.msqlu+" -p"+conf.msqlp+" "+language+conf.dumptype.lstrip("dump")
			success=os.system(command)
			if success == 0:
				print "BD descomprimida para el idioma ... "+language+conf.dumptype.lstrip("dump")+"\n\n"
			else:
				print "Ocurrio algun problema al descomprimir BD del idioma ... "+language+conf.dumptype.lstrip("dump")+"\n\n"
		elif conf.dumptype=="dump_stub":
			command_unzip="gzip -d dumps/"+filename
			success=os.system(command_unzip)
			if success == 0:
				command_decompress=conf.jpath+" -jar "+conf.mwpath+" --format=sql:1.5 dumps/"+filename.replace(".gz", "")+" | mysql -u "+conf.msqlu+" -p"+conf.msqlp+" "+language+conf.dumptype.lstrip("dump")
				succ=os.system(command_decompress)
				if succ == 0:
					print "BD descomprimida para el idioma ... "+language+conf.dumptype.lstrip("dump")+"\n\n"
					command_zip="gzip dumps/"+filename.replace(".gz","")
					os.system(command_zip)
				else:
					print "Ocurrio algun problema al descomprimir BD del idioma ... "+language+conf.dumptype.lstrip("dump")+"\n\n"
			else:
				print "Problema de descompresion del archivo .zip\n"
				
		else:
			print "Error en la seleccion del tipo de archivo de descompresion"
	else:
		print "Error de inicialización de la BD\n"

def __init_bd(conf, language="furwiki", dump_type="dump_stub"):
	# Construye la BD en MySQL para poder importar el dump del idioma indicado como argumento
	
	print "Inicializando BD para "+ language +"\n"
	acceso = dbaccess.get_Connection("localhost", 3306, conf.msqlu, conf.msqlp)
	dbaccess.createDB_SQL(acceso[1],language+conf.dumptype.lstrip("dump"))
	dbaccess.close_Connection(acceso[0])
	command="mysql -u "+conf.msqlu+" -p"+conf.msqlp+" " + language+conf.dumptype.lstrip("dump") + " < tables_15_09_2006.sql > output.txt"
	ok=os.system(command)
	print "Superado el comando ..."	
	if ok == 0:
		acceso = dbaccess.get_Connection("localhost", 3306, conf.msqlu, conf.msqlp, language+conf.dumptype.lstrip("dump"))
		dbaccess.raw_query_SQL(acceso[1], "alter table page max_rows = 200000000000 avg_row_length = 50")
		dbaccess.raw_query_SQL(acceso[1], "alter table revision max_rows = 200000000000 avg_row_length = 50")
		dbaccess.raw_query_SQL(acceso[1], "alter table text max_rows = 200000000000 avg_row_length = 50")
		dbaccess.close_Connection(acceso[0])
		return ok
	else:
		print "Problema al crear la BD"
		return -1
	
	

