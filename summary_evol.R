#This script analyzes and plots some summary useful information about the 
#Wikipedia database we are processing.

#Presently, it focus on general 2-D plots, linear adjustments and correlation graphics

input=scan("data/summary_files_names.data", list(""))
filenames=input[[1]]

input=scan("data/summary_files_out.data", list(""))
filenames_out=input[[1]]

input=scan(filenames[1], list(""))
datesx=input[[1]]

input=scan(filenames[2], list(""))
pageCount=input[[1]]

#Probar a hacerlo con escala logaritmica, por si acaso
png(filenames_out[1])
plot(pageCount, lty=3, col=1, main="Evolution in time of the total number of articles", xlab="weeks", ylab="tot_num_pages")
lines(lowess(pageCount),lty=3, col=2)
dev.off()
png(filenames_out[2])
plot(pageCount, log="y", lty=3, col=1, main="Evolution in time of the total number of articles", xlab="weeks", ylab="tot_num_pages")
lines(lowess(pageCount), log="y",lty=3, col=2)
dev.off()
png(filenames_out[3])
plot(pageCount, log="xy", lty=3, col=1, main="Evolution in time of the total number of articles", xlab="weeks", ylab="tot_num_pages")
lines(lowess(pageCount), log="xy",lty=3, col=2)
dev.off()

input=scan(filenames[3], list(""))
pageLenSum=input[[1]]
png(filenames_out[4])
plot(pageLenSum, lty=3, col=1, main="Evolution in time of the total size of articles", xlab="weeks", ylab="tot_num_pages")
lines(lowess(pageLenSum),lty=3, col=2)
dev.off()
png(filenames_out[5])
plot(pageLenSum, log="y", lty=3, col=1, main="Evolution in time of the total size of articles", xlab="weeks", ylab="tot_num_pages")
lines(lowess(pageLenSum), log="y",lty=3, col=2)
dev.off()
png(filenames_out[6])
plot(pageLenSum, log="xy", lty=3, col=1, main="Evolution in time of the total size of articles", xlab="weeks", ylab="tot_num_pages")
lines(lowess(pageLenSum), log="xy",lty=3, col=2)
dev.off()

input=scan(filenames[4], list(""))
contribs=input[[1]]
png(filenames_out[7])
plot(contribs, lty=3, col=1, main="Evolution in time of the total contribs", xlab="weeks", ylab="tot_num_pages")
lines(lowess(contribs),lty=3, col=2)
dev.off()
png(filenames_out[8])
plot(contribs, log="y", lty=3, col=1, main="Evolution in time of the total contribs", xlab="weeks", ylab="tot_num_pages")
lines(lowess(contribs), log="y",lty=3, col=2)
dev.off()
png(filenames_out[9])
plot(contribs, log="xy", lty=3, col=1, main="Evolution in time of the total contribs", xlab="weeks", ylab="tot_num_pages")
lines(lowess(contribs), log="xy",lty=3, col=2)
dev.off()

input=scan(filenames[5], list(""))
nspaces=input[[1]]

input=scan(filenames[6], list(""))
nspacesDistrib=input[[1]]

input=scan(filenames[7], list(""))
diffArticles=input[[1]]

input=scan(filenames[8], list(""))
authors=input[[1]]

input=scan(filenames[9], list(""))
diffAuthors=input[[1]]

png(filenames_out[10])
plot(diffArticles, lty=3, col=1, log="y",main="Different articles edited per author", xlab="authors", ylab="Different edited articles")
# lines(lowess(diffArticles), lty=3, col=2)
dev.off()

png(filenames_out[11])
plot(diffAuthors, lty=3, col=1, log="y",main="Different authors per article", xlab="article", ylab="Different authors")
# lines(lowess(diffAuthors), lty=3, col=2)
dev.off()

input=scan(filenames[10], list(""))
autautxplen=input[[1]]

input=scan(filenames[11], list(""))
plenautxplen=input[[1]]

png(filenames_out[12])
plot(autautxplen, plenautxplen, lty=3, col=1, log="y", main="Different authors per article against article size", xlab="Different authors", ylab="Article size")
# lines(lowess(diffAuthors), lty=3, col=2)
dev.off()

#page_len_log=read.table(filenames[7])