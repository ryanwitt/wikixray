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
Reads config file and returns appropiate params for other modules

@see: quantAnalay_main

@authors: Jose Felipe Ortega
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jfelipe@gsyc.escet.urjc.es
"""
__metaclass__=type

class quantAnalay_conf:
#Una clase para leer el fichero de configuracion y devolver los parametros necesarios a los restantes modulos del programa

	def __init__(self):
		#Almacena la lista de argumentos del programa
		f = open('config')

		try:
			self.list_args=f.readlines()
			print self.list_args
		finally:
			f.close()
