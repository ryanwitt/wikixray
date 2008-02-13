# coding=utf8
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
Read the config file and returns appropiate params to other modules

@see: quantAnalay_main

@authors: Jose Felipe Ortega
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jfelipe@gsyc.escet.urjc.es
"""

class qA_conf(object):
#Una clase para leer el fichero de configuracion y devolver los parametros necesarios a los restantes modulos del programa

	def __init__(self):
		#Almacena la lista de argumentos del programa
		f = open('config')

		try:
			self.list_args=f.readlines()
			#print self.list_args
		finally:
			f.close()

	def getJavaPath(self):
		return self.list_args[0].split("=").pop().strip("\n")
	
	def getMwPath(self):
		return self.list_args[1].split("=").pop().strip("\n")
	
	def getMySQLUser(self):
		return self.list_args[2].split("=").pop().strip("\n")
	
	def getMySQLPass(self):
		return self.list_args[3].split("=").pop().strip("\n")
	
	def getLangs(self):
		return self.list_args[4].split("=").pop().strip("\n").split()
	
	def getDumpType(self):
		return self.list_args[5].split("=").pop().strip("\n")
	
	jpath = property(getJavaPath)
	mwpath = property(getMwPath)
	msqlu = property(getMySQLUser)
	msqlp = property(getMySQLPass)
	langs = property(getLangs)
	dumptype = property(getDumpType)
