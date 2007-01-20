from rpy import *
import dbaccess, math

def test():
	idiomas=["svwiki", "ptwiki", "nlwiki", "jawiki", "frwiki", "dewiki"]
	for idioma in idiomas:
		acceso = dbaccess.get_Connection("localhost", 3306, "operator", "operator", idioma+"_stub")
		#dbaccess.query_SQL(acceso[1], "page_id, page_namespace", "page", where="page_namespace=0", create="pag_namespace")
		tcnoann=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_NoAnnons_author_"+idioma)
		tcauthor=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_author_"+idioma)
		tc_ann=dbaccess.query_SQL(acceso[1]," * ","stats_Contrib_Annons_author_text_"+idioma)
		dbaccess.close_Connection(acceso[0])
		data=__tup_to_list(tcnoann)
		listay_tcnoann=data.pop()
		listax=data.pop()
		data=__tup_to_list(tcauthor)
		listay_tcauthor=data.pop()
		listax=data.pop()
		data=__tup_to_list(tc_ann)
		listay_tc_ann=data.pop()
		listax=data.pop()
		r.png("graphics/gini_TContrib_NoAnn_"+idioma+".png")
		__lorenz_Curve(listay_tcnoann)
		r.png("graphics/gini_TContrib_"+idioma+".png")
		__lorenz_Curve(listay_tcauthor)
		r.png("graphics/gini_TContrib_Ann_"+idioma+".png")
		__lorenz_Curve(listay_tc_ann)
		#T=raw_input("press any key...")

def histogram():
	acceso = dbaccess.get_Connection("localhost", 3306, "root", "phoenix", "eswiki_tab_page")
	
	#ESTIMANDO SOLO LAS PAGINAS QUE CORRESPONDEN A ARTICULOS, CON NAMESPACE=MAIN=0
	#dbaccess.query_SQL(acceso[1],"page_id, page_len","page", where="page_namespace=0", order="page_len", create="aux")
	result=dbaccess.query_SQL(acceso[1], "page_id, page_len", "aux")
	dbaccess.close_Connection(acceso[0])
	data=__tup_to_list(result)
	page_len=data.pop()
	for i in range(len(page_len)):
		if page_len[i]!=0:
			page_len[i]=math.log10(page_len[i])
	
	r.png("graphics/boxplot_eswiki_log.png")
	r.boxplot(page_len)
	r.png("graphics/histogram_eswiki_log.png")
	r.assign("histogram",r.hist(page_len, xlab="Article size (log)", probability=r.TRUE, ylab="Density", main="Histogram of article size"))
	density=r.histogram["density"]
	mids=r.histogram["mids"]
	cut_index=density.index(min(density[len(density)/4:len(density)*3/4]))
	
	page_len.sort()
	page_len_low=[]
	page_len_high=[]
	for i in range(len(page_len)):
		if(page_len[i]<mids[cut_index]):
			page_len_low.append(page_len.pop(i))
		else:
			page_len_high=page_len[i:]
			break


	r.png("graphics/histogram_eswiki_log_low.png")
	r.hist(page_len_low, xlab="Article size (log)", probability=r.TRUE, ylab="Density", main="Histogram of article size (Lower half)")
	r.lines(r.density(page_len_low))
	r.rug(page_len_low)
	r.png("graphics/histogram_eswiki_log_high.png")
	r.hist(page_len_high, xlab="Article size (log)", probability=r.TRUE, ylab="Density", main="Histogram of article size (Higher half)")
	r.lines(r.density(page_len_high))
	r.rug(page_len_high)
	r.png("prueba.png")
	prueba=page_len_low[::100]
	r.plot(r.ecdf(prueba), xlab="Article size (log)", ylab="ECDF(Article Size(log))", do_points=r.FALSE,verticals=r.TRUE)
	r.png("graphics/ecdf_eswiki_log_low.png")
	#r.plot(r.ecdf(page_len_low), xlab="Article size (log)", ylab="ECDF(Article Size(log))", do_points=FALSE,verticals=r.TRUE)
	r.assign("x", r.seq(min(page_len_low), max(page_len_low), 0.1))
	r.plot(r.x, r.pnorm(r.x, mean=r.mean(page_len_low), sd=r.sd(page_len_low)),lty=3)
	r.png("graphics/ecdf_eswiki_high_high.png")
	#r.plot(r.ecdf(page_len_high), xlab="Article size (log)", ylab="ECDF(Article Size(log))", do_points=FALSE,verticals=r.TRUE)
	r.assign("x", r.seq(min(page_len_high), max(page_len_high), 0.1))
	r.plot(r.x, r.pnorm(r.x, mean=r.mean(page_len_high), sd=r.sd(page_len_high)),lty=3)
	"""
	#print page_len
	#page_len_dens=r.density(page_len[0:-2500])
	page_len_low=page_len[0:int(len(page_len)*0.335)]
	page_len_mid=page_len[int(len(page_len)*0.335):int(len(page_len)*0.97)]
	page_len_high=page_len[int(-len(page_len)*0.03):]
	for i in range(len(page_len_high)):
		page_len_high[i]=float(page_len_high[i])/1024.0
	print r.summary(page_len_low)
	print r.summary(page_len_low)
	print r.summary(page_len_mid)
	print r.summary(page_len_mid)
	print r.summary(page_len_high)
	print r.summary(page_len_high)
	
	r.png("graphics/histogram_eswiki__lower.png")
	# r.seq(min(page_len[0:-5000]), max(page_len[0:-5000])+1000, by=1000),
	r.hist(page_len_low, xlab="Article size", ylab="Frequency", main="Histogram of article size")
	r.png("graphics/histogram_eswiki__middle.png")
	r.hist(page_len_mid, xlab="Article size", ylab="Frequency", main="Histogram of article size")
	r.png("graphics/histogram_eswiki_K_upper.png")
	r.hist(page_len_high, xlab="Article size", ylab="Frequency", main="Histogram of article size")
	#r.lines(page_len_dens, col=2)
	
	r.png("graphics/boxplot_eswiki_Bytes_low.png")
	r.boxplot(page_len_low)
	r.png("graphics/boxplot_eswiki_Bytes_middle.png")
	r.boxplot(page_len_mid)
	r.png("graphics/boxplot_eswiki_KBytes_high.png")
	r.boxplot(page_len_high)
	#r.png("graphics/stem-leaf_eswiki_KBytes.png")
	#r.stem(page_len[:])
	"""
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
	r.png("graphics/gini.png")
	r.plot(x_values, y_values_lorenz, xlab="(%)Authors",ylab="(%)Cumulative contribution", main="Cumulative distribution function", type="l", col=2)
	r.legend(10, 80, legend="Gini Coefficient = %f" % g_coeff)
	r.legend(10, 100, legend=r.c("Line of perfect equality", "Lorenz curve"), col=r.c(1,2), pch=r.c(1,2))
	r.lines(x_values, x_values)
	#r.dev.off()
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

def __tup_to_list(result):
	aux=list(result)
	for i in range(len(aux)):
		aux[i]=list(aux[i])
	listax=[]
	listay=[]
	for i in range(len(aux)):
		listax.append(int(aux[i][0]))
		listay.append(int(aux[i][1]))
	return [listax, listay]

#histogram()
histogram()


