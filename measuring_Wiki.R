#This script plots graphics for measuring wikipedia

#Read input and output files names list
input=scan("data/measuring_files_names.data", list(""))
filenames=input[[1]]

input=scan("data/measuring_files_out.data", list(""))
filenames_out=input[[1]]

input=scan(filenames[1], list(""))
totalEdits=input[[1]]

input=scan(filenames[2], list(""))
noannonsEdits=input[[1]]

input=scan(filenames[3], list(""))
annonsEdits=input[[1]]

#Probar a hacerlo con escala logaritmica, por si acaso
png(filenames_out[1])
plot(totalEdits, lty=3, col=1, main="Total edits per author", xlab="authors", ylab="tot_num_edtis")
lines(lowess(totalEdits), log="y",lty=3, col=2)
dev.off()
png(filenames_out[2])
plot(noannonsEdits, log="y", lty=3, col=1, main="Total edits per logged author", xlab="authors", ylab="tot_num_edits")
lines(lowess(noannonsEdits), log="y",lty=3, col=2)
dev.off()
png(filenames_out[3])
plot(annonsEdits, log="y", lty=3, col=1, main="Total edits per anonymous author", xlab="authors", ylab="tot_num_edits")
lines(lowess(annonsEdits), log="y",lty=3, col=2)
dev.off()

input=scan(filenames[4], list(""))
autperarticdesc=input[[1]]

input=scan(filenames[5], list(""))
articperautdesc=input[[1]]

input=scan(filenames[6], list(""))
articperannondesc=input[[1]]

png(filenames_out[4])
plot(autperarticdesc, log="y",lty=3, col=1, main="Number of different authors per article", xlab="articles", ylab="tot_num_authors")
lines(lowess(autperarticdesc), log="y",lty=3, col=2)
dev.off()
png(filenames_out[5])
plot(articperautdesc, log="y", lty=3, col=1, main="Number of different articles per logged author", xlab="authors", ylab="tot_num_articles")
lines(lowess(articperautdesc), log="y",lty=3, col=2)
dev.off()
png(filenames_out[6])
plot(articperannondesc, log="y", lty=3, col=1, main="Number of different articles per anonymous author", xlab="authors", ylab="tot_num_articles")
lines(lowess(articperannondesc), log="y",lty=3, col=2)
dev.off()