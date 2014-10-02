#!/usr/bin/python

import sys
import os
import base64
import pdb
import urllib2
import urllib
import re
import csv
import re
import pprint
import logging
from py2neo import cypher

def doName(tmpName):
	retval=re.sub('\'',' ap ',tmpName)
	return retval

def doDate(earlS,lateS):
	retVal=""
#earlS = 1778-01-01T00:00:00Z
#lateS = 1778-12-31T00:00:00Z
	tmpEarl=earlS.split("-")
	tmpLate=lateS.split("-")
	yE=int(tmpEarl.pop(0))
	yL=int(tmpLate.pop(0))
	mE=tmpEarl.pop(0)
	mL=tmpLate.pop(0)
	dE=tmpEarl.pop(0).split("T")
	dL=tmpLate.pop(0).split("T")

	if (yE != yL):
		tmpx=(((yL + 0.0) - (yE+0.0))/2)
		retVal=str(int(round(tmpx) + yE))
	elif mE == "01" and  mL == "12":
		retVal=str(yL) + "-06-01"
	else:
		retVal=str(yE) + "-" + mE + "-" + dE[0]
			
	return retVal

def main():
#	Abraham Bloemaert;1566;25-12-1566;1566-12-25;1651;27-01-1651;1651-01-27;Hollandsk;original
#	Andrea Proccaccini;(?);(?);(?);(?);(?);(?);(?);original
#	MATCH (y:Year { year:1860}) MERGE (a:Artist {name:'Alphonse Mucha',nation:'Tjekkisk'}) CREATE (a)-[:BORN]->(y);
#	MATCH (y:Year { year:1894}), (a:Artist {name:'Alphonse Mucha'}) CREATE (a)-[:DIED]->(y);
#	MATCH (x) WHERE HAS (x.x) MERGE (y { y:"y" }) CREATE (y)-[:REL]->(x);
#	MATCH (y:Year { year:1858}), (x:Year {year:1895}) MERGE  (a:Artist {name:'Axel Schmidt',nation:'Dansk'}) CREATE (a)-[:BORN]->(y), (a)-[:DIED]->(x);

	reload(sys);
	sys.setdefaultencoding("utf8")
	myhome="/usr/local/twm"
	artistList=[]
	limit=1777
	dummyB=4321
	dummyD=4391
	logging.basicConfig(filename=myhome+'/logs/thw.log',level=logging.DEBUG)
	session = cypher.Session("http://localhost:7474")

	fh=open(sys.argv[1],"r")
	fhlines=fh.readlines()
#----------
	for line in fhlines:
		print line
		statement=""
		tmpLine=line.split("@")
		tmpacq_date=tmpLine.pop().rstrip()
		acq_date=re.sub('[^0-9-]','',tmpacq_date)
		print "D:acq:" + acq_date
		lateD=tmpLine.pop()
		print "D:lateD:" + lateD
		earlD=tmpLine.pop()
		print "D:earlD:" + earlD
		title=tmpLine.pop(0)
		print "T:title: " + title
		artist=tmpLine.pop().rstrip()
		print "A:artist:" + artist
		realDate=doDate(earlD,lateD)
		print "RD:realDate:" + realDate

		print "\n"

#	----------
#	MATCH (a:Artist { name:'Kasper Heiberg'}),(y:Year {year:1922}),(x:Year {year:1999})  MERGE  (w:Artwork {title:'Axel Schmidt'}) CREATE (a)-[:PAINTED]->(w), (w)-[:CRY]->(y), w-[:ACQY]->(x);
		cyP="MERGE "
		cyAr=" (w:Artwork {title:'"
		cyPA=" CREATE (a)-[:PAINTED]->(w)"
		cyPD=" (w)-[:CRY]->(y)"
		cyAD=" (w)-[:ACQY]->(x)"
		cyA="MATCH (a:Artist { year:"
		logging.debug(line)
		tmpLine=line.split(";")
		artist=doName(tmpLine.pop(0).rstrip())
		if (re.search('ubekendt',artist,re.IGNORECASE)):
			logging.debug('unkown ' + line)
			continue
		if artist in artistList:
			logging.debug('Already done: ' + artist)
			continue
			
		print "A:artist:" + artist
		cyAr = cyAr + ("%s'," % artist)
		artistList.append(artist)
		trash=tmpLine.pop()
		nation=tmpLine.pop().rstrip()
		print "A:nation:" + nation
		cyAr = cyAr + ("nation:'%s'})" % nation)

# BIRTH
		tmpbirthY=tmpLine.pop(0).rstrip()
		if not tmpbirthY.find("(?)"):
			logging.debug("unknown data on %s" % artist)
			continue
		birthY=re.sub('[^0-9-]','',tmpbirthY)
		try:
			birthYint=int(birthY)
		except ValueError:
			birthYint=dummyB;
		print "D:BY:" + birthY
		if (birthYint < limit):
			logging.debug("too old %s" % birthY)
			continue
		cyA = cyA + ("%s}) " % birthY)
#cyA="MATCH (y:Year { year:"
#cyF = cyA + cyP + cyAr + cyBE
		tmpbirthD=tmpLine.pop(0).rstrip()
		birthD=re.sub('[^0-9-]','',tmpbirthD)
		print "D:BD:" + birthD

# DEATH
#	MATCH (y:Year { year:1858}), (x:Year {year:1895}) MERGE  (a:Artist {name:'Axel Schmidt',nation:'Dansk'}) CREATE (a)-[:BORN]->(y), (a)-[:DIED]->(x);
		cyB="(x:Year { year:"
		trash=tmpLine.pop(0).rstrip()
		tmpDeathY=tmpLine.pop(0).rstrip()
		if not tmpDeathY.find("(?)"):
			logging.debug("still alive %s" % artist)
			continue
		deathY=re.sub('[^0-9-]','',tmpDeathY)
		print "D:DY:" + deathY
		if (deathY < limit):
			logging.debug("too old %s" % deathY)
			continue
		cyB = cyB + ("%s}) " % deathY)
		cyF = cyA + ", " + cyB + cyP + cyAr + cyBE + ", " + cyDE + ";"
		tmpDeathD=tmpLine.pop(0).rstrip()
		deathD=re.sub('[^0-9-]','',tmpDeathD)
		print "D:DD:" + deathD
		print "cyNF:" + cyF
		tx.append(cyF)
		tx.execute()
		tx.commit()

if __name__ == '__main__':
	main()
#!/usr/bin/python

import sys
import os
import base64
import pdb
import urllib2
import urllib
import re
import csv
import re
import pprint
import logging
from py2neo import cypher


def doDate(earlS,lateS):
	retVal=""
#earlS = 1778-01-01T00:00:00Z
#lateS = 1778-12-31T00:00:00Z
	tmpEarl=earlS.split("-")
	tmpLate=lateS.split("-")
	yE=int(tmpEarl.pop(0))
	yL=int(tmpLate.pop(0))
	mE=tmpEarl.pop(0)
	mL=tmpLate.pop(0)
	dE=tmpEarl.pop(0).split("T")
	dL=tmpLate.pop(0).split("T")

	if (yE != yL):
		tmpx=(((yL + 0.0) - (yE+0.0))/2)
		retVal=str(int(round(tmpx) + yE))
	elif mE == "01" and  mL == "12":
		retVal=str(yL) + "-06-01"
	else:
		retVal=str(yE) + "-" + mE + "-" + dE[0]
			
	return retVal

def main():
	reload(sys);
	sys.setdefaultencoding("utf8")
	myhome="/usr/local/twm"
	logging.basicConfig(filename=myhome+'/logs/thw.log',level=logging.DEBUG)
	session = cypher.Session("http://localhost:7474")
	tx = session.create_transaction()

	fh=open(sys.argv[1],"r")
	fhlines=fh.readlines()
