import dbdump
import dbanaly
import qA_conf as q
import graphics

""" STEPS

1. Download and decompress  db dumps for each Wikipedia language version we want to analyse.

2. DB analysis for each language version:
	a. Authors
	b. Articles
	c. Contents
	
3. Call the graphics module to generate charts, plots and statistical results for each language version
"""

#Take config form file
conf=q.qA_conf()

#Lista de idiomas que queremos analizar
ListaIdiomas=conf.langs
#ListaIdiomas=["eswiki", "plwiki"]

print "STARTING DATABASE DUMP DECOMPRESSION...\n"
for idioma in ListaIdiomas:
	fichero=dbdump.download_bd(conf,idioma)
	#fichero=idioma+"-latest-stub-meta-history.xml.gz"
	dbdump.unzip_bd(conf,fichero,idioma)
print "DATABASE DUMP DECOMPRESSION FINISHED...\n"

print "INITIATING DATABASE ANALYSIS...\n"
    
for idioma in ListaIdiomas:
    print "ANALYSIS FOR LANGUAGE VERSION " + idioma + "\n\n"
    dbanaly.flux_capacitor(conf,idioma)
    print "INITIATING AUTHOR ANALYSIS FOR LANGUAGE VERSION " + idioma + "\n\n"
    dbanaly.info_authors(conf,idioma)
    print "AUTHOR ANALYSIS COMPLETED FOR LANGUAGE VERSION " + idioma + "\n\n"
    print "INITIATING ARTICLE ANALYSIS FOR LANGUAGE VERSION " + idioma + "\n\n"
    dbanaly.info_articles(conf,idioma)
    print "AUTHOR ANALYSIS COMPLETED FOR LANGUAGE VERSION " + idioma + "\n\n"
    print "INITIATING CONTENTS ANALYSIS FOR LANGUAGE VERSION " + idioma + "\n\n"
    dbanaly.info_contents(conf,idioma)
    print "CONTENTS ANALYSIS COMPLETED FOR LANGUAGE VERSION " + idioma + "\n\n"
    
print "GENERATING GRAPHICS AND STATISTICAL RESULTS FOR LANGUAGE VERSION " + idioma + "\n\n"
graphics.work(ListaIdiomas)
print "GRAPHICS AND STATISTICAL RESULTS GENERATED FOR LANGUAGE VERSION " + idioma + "\n\n"
    
print "DATABASE ANALYSIS COMPLETED...\n"
print "END OF SCRIPT EXECUTION. GOOD LUCK WITH RESULTS INTERPRETATION.\n"

