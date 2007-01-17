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