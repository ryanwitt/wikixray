#This script takes a data.frame from Python QuantAnaly graphics module
#To calculate and plot some useful histograms and statistics about the data.

#Currently applied to article size

#Load library for Kurtosis and Skewness methods
library(moments)
#Read the data file with article sizes

input=scan("data/hist_files_names.data", list(""))
filenames=input[[1]]
page_len_log=read.table(filenames[7])

#Open a file for the boxplot of aggregate page_len_log
#"graphics/boxplot_eswiki_log.png"
png(filenames[1])
boxplot(page_len_log[,1])
dev.off()
#Open a file for the histogram of aggregate page_len_log
#"graphics/histogram_eswiki_log.png"
png(filenames[2])
dens=density(page_len_log[,1])
histogram=hist(page_len_log[,1], xlab="Article size (log)", probability=TRUE, ylab="Density", main="Histogram of article size", ylim=range(0,max(dens$y)))
lines(dens)
dev.off()

png(filenames[9])
plot(ecdf(page_len_log[,1]), main="Cumulative Distrib. Func. for log(Article size)", xlab="log(Article size)", ylab="ecdf(log(Article size))",do.points=FALSE, verticals=TRUE)
dev.off()

#Subdivide page_len_log in two samples groups, based on histogram info

resumen=summary(histogram$mids)
q1=resumen["1st Qu."]
q3=resumen["3rd Qu."]

focus_mids=histogram$mids[q1<histogram$mids & histogram$mids<q3]
focus_dens=histogram$density[q1<histogram$mids & histogram$mids<q3]
cutpoint_dens=min(focus_dens)
cutpoint_mids=focus_mids[focus_dens==cutpoint_dens]

page_len_low=page_len_log[,1][page_len_log[,1]<cutpoint_mids]
page_len_high=page_len_log[,1][page_len_log[,1]>=cutpoint_mids]

#Print histogram for the lower group of samples
#"graphics/histogram_eswiki_log_low.png"
png(filenames[3])
dens=density(page_len_low)
hist(page_len_low, xlab="Article size (log)", probability=TRUE, ylab="Density", main="Histogram of article size (Lower half)", ylim=range(0,max(dens$y)))
lines(dens)
dev.off()
#Same for the upper group of samples
#"graphics/histogram_eswiki_log_high.png"
png(filenames[4])
dens=density(page_len_high)
hist(page_len_high, xlab="Article size (log)", probability=TRUE, ylab="Density", main="Histogram of article size (Higher half)", ylim=range(0,max(dens$y)))
lines(dens)
dev.off()
#Print ECDF for lower group of samples
#"graphics/ecdf_eswiki_log_low.png"
png(filenames[5])
#plot(ecdf(page_len_low), xlab="Article size (log)", ylab="ECDF(Article Size(log))", do.points=FALSE, verticals=TRUE)
plot(ecdf(page_len_low), do.points=FALSE, verticals=TRUE)
x=seq(min(page_len_low), max(page_len_low), 0.1)
lines(x, pnorm(x, mean=mean(page_len_low), sd=sd(page_len_low)),lty=3, col=2)
dev.off()
#Same for the upper group of samples	
#"graphics/ecdf_eswiki_high_high.png"
png(filenames[6])
#plot(ecdf(page_len_high), xlab="Article size (log)", ylab="ECDF(Article Size(log))", do.points=FALSE, verticals=TRUE)
plot(ecdf(page_len_high), do.points=FALSE, verticals=TRUE)
x=seq(min(page_len_high), max(page_len_high), 0.1)
lines(x, pnorm(x, mean=mean(page_len_high), sd=sd(page_len_high)),lty=3, col=2)
dev.off()
#Print out some useful values about the sample groups
sink(filenames[8])

#Summaries and fivenumbers
print("Summary for var page_len_low")
print(summary(page_len_low))
print("Tukey five numbers for var page_len_low")
print(fivenum(page_len_low))
print("Summary for var page_len_high")
print(summary(page_len_high))
print("Tukey five numbers for var page_len_high")
print(fivenum(page_len_high))

print("*************************")
print("*************************")
print("Skewness and Kurtosis coefficientes for page_len_low")
print("Skewness")
print(skewness(page_len_low))
print("Kurtosis")
print(kurtosis(page_len_low))
print("Skewness and Kurtosis coefficientes for page_len_high")
print("Skewness")
print(skewness(page_len_low))
print("Kurtosis")
print(kurtosis(page_len_low))
print("*************************")
print("*************************")

#Shapiro-Wilkes normality test
shapiro_low=page_len_low[seq(1, length(page_len_low), by=10000)]
print("Shapiro-Wilkes normality test for page_len_low")
print(shapiro.test(shapiro_low))

shapiro_high=page_len_high[seq(1, length(page_len_high), by=10000)]
print("Shapiro-Wilkes normality test for page_len_high")
print(shapiro.test(shapiro_high))

#Switch off output pipes
sink()


