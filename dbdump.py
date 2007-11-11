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
Module for downloading database dump of any of the langauge editions we want to 
analyze. Once downloaded in 7zip format (storage optimization), we decompress the
dump to a local MySQL database.
This way, we have prepared the database for the next steps in the quantitative
analysis process.

@see: quantAnalay_main

@authors: Jose Felipe Ortega
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jfelipe@gsyc.escet.urjc.es
"""

import os, datetime, dbaccess

class dump(object):
    """
    A class modelling dumps object for every Wikipedia's database dump we process
    """
    def __init__(self, language="furwiki", dumptype="research", msqlu="", msqlp=""):
        """
        It receives the language and dumptype to download
        It returns an int =0 if the DB was successfully set up, =-1 if there was an error
        """
        self.language=language       #language to download
        self.dumptype=dumptype      #type of dump      
        self.filename=""        #dump's filename in Wikimedia's server
        if (msqlu=="" or msqlp==""):
            print "Error initializing DB dump object. You must provide a valid MySQL username and password"
            return -1
        else:
            self.msqlu=msqlu   #MySQL username for accessing and editing the DB
            self.msqlp=msqlp   #MySQL password
        #We can manage two different types of dumps, stubs (without the text of every revision) and pages
        #(containing the text of every revision)
        self.urld="http://download.wikimedia.org/"+self.language+"/latest/"+\
        self.language+"-latest-pages-meta-history.xml.7z"  #File to download
        #patterns for files
        #http://download.wikimedia.org/furwiki/20060921/furwiki-20060921-pages-meta-history.xml.7z
        #http://download.wikimedia.org/amwiki/20061014/amwiki-20061014-stub-meta-history.xml.gz
        
        ## Initialize DB in MySQL: create DB and tables definitions
        print "Initializing DB for --> "+ self.language +"\n"
        #Retrieving connection and cursor to access the DB
        acceso = dbaccess.get_Connection("localhost", 3306, self.msqlu, self.msqlp,"mysql")
        dbaccess.createDB_SQL(acceso[1],"wx_"+self.language+"_"+self.dumptype)
        if self.dumptype=="research":
            command="mysql -u "+self.msqlu+" -p"+self.msqlp+" " +\
            "wx_"+self.language+"_"+self.dumptype+" < tables_research.sql > debug_mysql.log"
        elif self.dumptype=="standard":
            command="mysql -u "+self.msqlu+" -p"+self.msqlp+" " +\
            "wx_"+self.language+"_"+self.dumptype+" < tables_standard.sql > debug_mysql.log"
        ok=os.system(command)
        if ok == 0:
            acceso = dbaccess.get_Connection("localhost", 3306, self.msqlu, self.msqlp,\
            "wx_"+self.language+"_"+self.dumptype)
            dbaccess.raw_query_SQL(acceso[1], "alter table page max_rows = 200000000000 avg_row_length = 50")
            dbaccess.raw_query_SQL(acceso[1], "alter table revision max_rows = 200000000000 avg_row_length = 50")
            if self.dumptype=="standard":
                dbaccess.raw_query_SQL(acceso[1], "alter table text max_rows = 200000000000 avg_row_length = 50")
            dbaccess.close_Connection(acceso[0])
        else:
            print "Error! There was a problem initializing definitions for DB tables"
            dbaccess.close_Connection(acceso[0])
            
    def download_bd (self):
        """
        Downloads the necessary dump files from http://download.wikimedia.org
        """
        # Arguments are the self.language and dump type to download
        # This method uses wget to discover the most up to date version for that type of dump in that language edition
        print "Trying to recover dump file... "+self.urld+"\n"
        success=os.system("wget -P dumps -o log_"+self.language+" --ignore-length "+self.urld)
        if success== 0:
            print "File successfully downloaded..."
            self.filename=self.language+"-latest-pages-meta-history.xml.7z"
            return success
        else:
            # Error retrieving main dump
            print "There was an error recovering the main dump for the "+self.language+" language edition"
            print "Most probably, the dump does not exist. Check on http://download.wikimedia.org."
            return -1
    
    def unzip_bd (self):
        """
        Decompress the DB dumps into MySQL
        """	
        if self.dumptype=="research":
            #Then we call our parser "dump_sax_research.py"to load data into MySQL
            command_7z="7za e -so dumps/"+self.filename+ " | "+"python dump_sax_research.py "+\
            "-u "+self.msqlu+" -p "+self.msqlp+" -d "+"wx_"+self.language+"_"+self.dumptype
            success=os.system(command_7z)
            if success == 0:
                print "DB "+"wx_"+self.language+\
                self.dumptype+" successfully decompressed...\n\n"
            else:
                print "Error! There was an error trying to decompress database --> "+\
                "wx_"+self.language+self.dumptype
                
        elif self.dumptype=="standard":
            print("Initiating decompression and parsing...")
            command_7z="7za e -so dumps/"+self.filename+ " | "+"python dump_sax.py "+\
            "-u "+self.msqlu+" -p "+self.msqlp+" -d "+"wx_"+self.language+"_"+self.dumptype
            succ=os.system(command_7z)
            if succ == 0:
                print "DB --> "+"wx_"+self.language+self.dumptype+\
                " successfully decompressed\n\n"
            else:
                print "Error! There was an error decompressing DB ... "+\
                "wx_"+self.language+self.dumptype
        else:
            print "Error! Unexpected type of dump received"
            
        print "Generating indexes for tables page and revision...\n"
        print "Depending on the dump size this may take a while...\n"
        acceso = dbaccess.get_Connection("localhost", 3306, self.msqlu,\
        self.msqlp, "wx_"+self.language+"_"+self.dumptype)
        #Generate adequate indexes and keys in tables page and revision
        print "Generating index for page_len...\n"
        dbaccess.raw_query_SQL(acceso[1],"ALTER TABLE page ADD INDEX (page_len)")
        print "Modifying rev_timestamp to support DATETIME and creating index...\n"
        dbaccess.raw_query_SQL(acceso[1],"ALTER TABLE revision MODIFY rev_timestamp DATETIME")
        dbaccess.raw_query_SQL(acceso[1],"ALTER TABLE revision ADD INDEX timestamp (rev_timestamp)")
        print "Generating index for rev_page and rev_timestamp...\n"
        dbaccess.raw_query_SQL(acceso[1],"ALTER TABLE revision ADD INDEX page_timestamp(rev_page, rev_timestamp)")
        print "Generating index for rev_user and rev_timestamp...\n"
        dbaccess.raw_query_SQL(acceso[1],"ALTER TABLE revision ADD INDEX user_timestamp(rev_user, rev_timestamp)")
        print "Generating index for rev_user_text and timestamp...\n"
        dbaccess.raw_query_SQL(acceso[1],"ALTER TABLE revision ADD INDEX usertext_timestamp(rev_user_text(15), rev_timestamp)")
        dbaccess.close_Connection(acceso[0])
        print "Database ready for quantitative analysis...\n"
        print "Let's go on... Cross your fingers... ;-) \n\n\n"

if __name__ == '__main__':
    foobar=dump(dumptype="standard",msqlu="root", msqlp="phoenix")
    foobar.download_bd()
    foobar.unzip_bd()

