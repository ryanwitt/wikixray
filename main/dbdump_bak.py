import os, datetime, dbaccess

"""
El objetivo de esta clase es descargar las bases de datos comprimidas de los diferentes idiomas
que van a ser objeto de estudio por parte del programa.

Una vez descargadas, en formazo 7zip para optimizar el espacio de almacenamiento, se descomprime
la base de datos de cada idioma a su correspondiente base de datos en MySQL local.

De esta forma, la BD de cada idioma queda ya preparada para su correspondiente análisis.
"""
java_path="/home/jfelipe/Programas/jre1.5.0_06/bin/java"
mwdumper_path="../../mwdumper.jar"

def download_bd (language="furwiki"):
	# Recibe como parámetro el idioma que queremos descargar
	# La funcion usará w-get para descubrir la última versión correcta del volcado de ese idioma
	
	#Fecha adecuada para la versión del dump a descargar
	#Si no existe dump para esa fecha, vamos hacia atrás hasta recoger el último disponible
	date_object=datetime.date.today()
	str_date=date_object.isoformat().replace("-","")
	delta=datetime.timedelta(days=1)
	fetched=False
	url="http://download.wikimedia.org/"+language+"/"+str_date+"/"+language+"-"+str_date+"-"+"pages-meta-history.xml.7z"
	#pattern="http://download.wikimedia.org/furwiki/20060921/furwiki-20060921-pages-meta-history.xml.7z"
	while not fetched:
		#print "Tratando de recuperar el archivo... \n"+url
		#print pattern
		success=os.system("wget -P dumps -o log_"+language+" --limit-rate=20k "+url)
		if success== 0:
			fetched=True
			return (language+"-"+str_date+"-"+"pages-meta-history.xml.7z")
		else:
			date_object-=delta
			str_date_old=str_date
			str_date=date_object.isoformat().replace("-","")
			url=url.replace(str_date_old,str_date)
			
		print "status= %i" % success	

def unzip_bd (filename, language="furwiki"):
	# Recibe como parámetro el idioma que queremos descomprimir
	ok=__init_bd(language)
	
	if ok == 0:
		# La funcion llama al script de descompresión y pasa a traves de un pipe la info a mwdumper y de ahí a MySQL
		command="7za e -so dumps/"+filename+ " | "+java_path+" -jar "+mwdumper_path+" --format=sql:1.5 | mysql -u root -pphoenix "+language
		success=os.system(command)
		if success == 0:
			print "BD descomprimida para el idioma ... "+language+"\n\n"
		else:
			print "Ocurrio algun problema al descomprimir BD del idioma ... "+language+"\n\n"
		
	else:
		print "Error de inicialización de la BD"

def __init_bd(language="furwiki"):
	# Construye la BD en MySQL para poder importar el dump del idioma indicado como argumento
	print "Inicializando BD para "+ language +"\n"
	acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix")
	dbaccess.createDB_SQL(acceso[1],language)
	dbaccess.close_Connection(acceso[0])
	command="mysql -u root -pphoenix " + language + " < tables_21_02_2006.sql > output.txt"
	ok=os.system(command)
	if ok == 0:
		return ok
	else:
		print "Problema al crear la BD"
		return -1
	
	

