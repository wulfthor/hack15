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
#	Abraham Bloemaert;1566;25-12-1566;1566-12-25;1651;27-01-1651;1651-01-27;Hollandsk;original
#	MATCH (x) WHERE HAS (x.x) MERGE (y { y:"y" }) CREATE (y)-[:REL]->(x);
	reload(sys);
	sys.setdefaultencoding("utf8")
	myhome="/usr/local/twm"
	artistList=[]
	limit=1777
	logging.basicConfig(filename=myhome+'/logs/thw.log',level=logging.DEBUG)
	session = cypher.Session("http://localhost:7474")
	tx = session.create_transaction()

	fh=open(sys.argv[1],"r")
	fhlines=fh.readlines()
	for line in fhlines:
		cyP="MERGE (a:Artist {"
		cyA="MATCH (y:Year) { y.year:"
		logging.debug(line)
		tmpLine=line.split(";")
		artist=tmpLine.pop(0).rstrip()
		if artist in artistList:
			logging.debug('Already done: ' + artist)
			continue
			
		print "A:artist:" + artist
		cyP = cyP + ("name:'%s'," % artist)
		artistList.append(artist)
		trash=tmpLine.pop()
		nation=tmpLine.pop().rstrip()
		print "A:nation:" + nation
		cyP = cyP + ("nation:'%s'})" % nation)

		tmpbirthY=tmpLine.pop(0).rstrip()
		birthY=re.sub('[^0-9-]','',tmpbirthY)
		birthYint=int(birthY)
		print "D:BY:" + birthY
		if (birthYint < limit):
			logging.debug("too old %s" % birthY)
			continue
		cyA = cyA + ("'%s'}) " % birthY)
		cyF = cyA + cyP + " CREATE (a)-[:BORN]->(y);"
		tx.append(cyF)
		print "CC:" + cyF

		tmpbirthD=tmpLine.pop(0).rstrip()
		birthD=re.sub('[^0-9-]','',tmpbirthD)
		print "D:BD:" + birthD
		trash=tmpLine.pop(0).rstrip()
		tmpDeathY=tmpLine.pop(0).rstrip()
		deathY=re.sub('[^0-9-]','',tmpDeathY)
		print "D:DY:" + deathY
		tmpDeathD=tmpLine.pop(0).rstrip()
		deathD=re.sub('[^0-9-]','',tmpDeathD)
		print "D:DD:" + deathD

# send three statements to for execution but leave the transaction open
	tx.append("MERGE (a:Person {name:'Alice'}) "
			"RETURN a")
	tx.append("MERGE (b:Person {name:'Bob'}) "
			"RETURN b")
	tx.append("MATCH (a:Person), (b:Person) "
			"WHERE a.name = 'Alice' AND b.name = 'Bob' "
			"CREATE UNIQUE (a)-[ab:KNOWS]->(b) "
			"RETURN ab")
#tx.execute()

# send another three statements and commit the transaction
	tx.append("MERGE (c:Person {name:'Carol'}) "
			"RETURN c")
	tx.append("MERGE (d:Person {name:'Dave'}) "
			"RETURN d")
	tx.append("MATCH (c:Person), (d:Person) "
			"WHERE c.name = 'Carol' AND d.name = 'Dave' "
			"CREATE UNIQUE (c)-[cd:KNOWS]->(d) "
			"RETURN cd")
#	tx.commit()


if __name__ == '__main__':
	main()
