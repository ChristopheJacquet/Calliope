#!/usr/bin/python
# coding=utf-8

import sqlite3
import re
import codecs


# read the index file
mots = codecs.open("mots_latins.txt", "r", encoding="iso-8859-1")


conn = sqlite3.connect('mots.sqlite')

c = conn.cursor()

c.execute('DROP TABLE IF EXISTS mots')

c.execute('CREATE TABLE mots (mot PRIMARY KEY, longueurs)')

##c.execute('BEGIN TRANSACTION')

# ABACI ; abaci_ ; ''-,3pp ; abacus, abaci_ : m

#motif = re.compile("^(\w+)\s+;.([A-Za-z_\(\)]+)\s")     # insérer même mots ambigus
motif = re.compile("^(\w+)\s+;(.)([A-Za-z_\(\)]+)\s")

ambigus = 0

for line in mots:
    m = motif.match(line)
    if m!= None:
        mot = m.group(1).lower()
        longueurs = m.group(3).replace("(", "").replace(")", "").lower()
        if m.group(2) != " ":
            longueurs = longueurs.replace("'", "").replace("_", "")
            ambigus += 1
        #print(u"{0} {1}".format(mot, longueurs))
        c.execute("INSERT INTO mots (mot, longueurs) VALUES (?, ?)", (mot, longueurs))
    else:
        print u"Ligne non reconnue: {0}".format(repr(line))

##c.execute('END TRANSACTION')

conn.commit()

c.close()
    

mots.close()


print( "{0} ambigus".format(ambigus) )