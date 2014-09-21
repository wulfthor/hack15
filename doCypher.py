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
