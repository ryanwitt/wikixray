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
Main module of WikiXRay, responsible for calling the other functional modules.

@see: quantAnalay_main

@authors: Jose Felipe Ortega
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jfelipe@gsyc.escet.urjc.es
"""

import dbdump, dbanaly, graphics
import dbanaly
import qA_conf as q
import graphics

""" 
STEPS

1. Download and decompress  db dumps for each Wikipedia language version we want to analyse.

2. DB analysis for each language version:
	a. Authors
	b. Articles
	c. Contents
	
3. Call the graphics module to generate charts, plots and statistical results for each language version
"""
if __name__ == '__main__':
    #Take config form file
    conf=q.qA_conf()
    
    #Lista de idiomas que queremos analizar
    #ListaIdiomas=conf.langs
    ListaIdiomas=["furwiki"]
    
    print "STARTING DATABASE DUMP DECOMPRESSION...\n"
    for idioma in ListaIdiomas:
        dump=dbdump.dump(language=idioma,msqlu=conf.msqlu, msqlp=conf.msqlp)
        dump.download()
        dump.decompress()
    print "DATABASE DUMP DECOMPRESSION FINISHED...\n"
    
    print "INITIATING DATABASE ANALYSIS...\n"
        
    for idioma in ListaIdiomas:
        print "ANALYSIS FOR LANGUAGE VERSION " + idioma + "\n\n"
        dbanaly=dbanaly.dbanaly(conf,idioma)
        print "AUTHOR ANALYSIS SET UP FOR LANGUAGE VERSION " + idioma + "\n\n"
        dbanaly.infoAuthors()
        print "AUTHOR ANALYSIS SET UP COMPLETED FOR LANGUAGE VERSION " + idioma + "\n\n"
        print "ARTICLE ANALYSIS SET UP FOR LANGUAGE VERSION " + idioma + "\n\n"
        dbanaly.infoPages()
        print "ARTICLE ANALYSIS SET UP COMPLETED FOR LANGUAGE VERSION " + idioma + "\n\n"
        print "INITIATING CONTENTS ANALYSIS FOR LANGUAGE VERSION " + idioma + "\n\n"
        dbanaly.infoContents()
        print "CONTENTS ANALYSIS COMPLETED FOR LANGUAGE VERSION " + idioma + "\n\n"
        
##    print "GENERATING GRAPHICS AND STATISTICAL RESULTS FOR LANGUAGE VERSION " + idioma + "\n\n"
##    graphics.work(ListaIdiomas)
##    print "GRAPHICS AND STATISTICAL RESULTS GENERATED FOR LANGUAGE VERSION " + idioma + "\n\n"
##        
##    print "DATABASE ANALYSIS COMPLETED...\n"
    print "END OF SCRIPT EXECUTION. GOOD LUCK WITH RESULTS INTERPRETATION.\n"
    
