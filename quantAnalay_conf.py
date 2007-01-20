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
