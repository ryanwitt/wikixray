
        #Script to plot a 2D graph : by plot2D : inherits from graphRMySQL
        #Load library
        library(RMySQL)
        #Connect to the DB
        con <- dbConnect(dbDriver("MySQL"),dbname="wx_glwiki_research",user="pepito",password="fenix")
        #Fetch query as data.frame
        results <- dbGetQuery(con,"SELECT ABS(contrib_len) FROM articles_glwiki_contrib_len WHERE contrib_len<0")
        #Open graphic device
        postscript("prueba2.eps")
        #Plot histogram (probabilities) and density function
        linedens=density(log10(results[,1]))
        hist(log10(results[,1]), prob=T, ylim=c(0,max(linedens$y)),
        xlab="rev_id", ylab="density", main="Test histogram graph")
        lines(linedens, col="navy", lty=1, lwd=1)
        #Close graphic device
        dev.off()
        #Disconnect from the DB
        dbDisconnect(con)
        