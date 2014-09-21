#!/usr/bin/python

import sys
import os
import base64
import pdb
import codecs
import urllib2
import urllib
import re
import xml.etree.ElementTree as ET
import csv
import nltk
import re
import pprint
import logging

sys.path.append('../lib')
import config

reload(sys);
sys.setdefaultencoding("utf8")


"""
input artistname
exist in Neo?
        yes: 
                are there artworks from him?
                yes: 
                        exit
                no: 
                        find all artworks 
                        for-each:
                                getM
                                for title:
                                        doNER
                                                if res:
                                                        is_res_in_Neo?:
                                                                yes:
                                                                        create_rel_to_artist_from_artwork 
                                                                no:
                                                                        is_res_in_Globus?:
                                                                                yes:
                                                                                        create_artist_and_rel_to_artist_from_artwork
                                                                                no:
                                                                                        create_res_and_rel_to_artist_from_artwork

        no: 
                create
                find_his_artworks
"""

def doTitleClean(tmpTitle):
        retval = tmpTitle
        m=re.match('(.*);',tmpTitle)
        if m:
                danishPart=m.group(1)
                retval = danishPart
        return retval

def doDate(tmpdateString):
        # "1804" 1613/1614 Enten 1564 eller 1566 1600-tallet" "Ca. 1576" "20-12-1920" "Ca. 1640-1660"
        # date -d "1801-01-01" "+%s"
        dateString=re.sub(' ','',tmpdateString)
        res="0"
        mon="06"
        day="12"
        
        m=re.match('(\d{2})-(\d{2})-(\d{4})',dateString)
        if m:
                day=m.group(1)
                mon=m.group(2)
                year=m.group(3)
                newstr=str(year) + "-" + str(mon) + "-" + str(day)
                cmd="/usr/bin/java getOldDate  \"" + newstr + "\""
                #cmd="date -d \"" + newstr + "\" \"+%s\""
                res = os.popen(cmd,"r").read()
                return res.rstrip()

        m=re.match('([\d]{4})',dateString)
        if m:
                year=m.group(0)
                newstr=str(year) + "-" + mon + "-" + day
                #cmd="date -d \"" + newstr + "\" \"+%s\""
                cmd="/usr/bin/java getOldDate " + newstr 
                res=os.popen(cmd,"r").read()
                return res.rstrip()

        else:
                return res
                

def doArtWork(artList):

        '''
        filter NNP
        if its a name
                lookup if artist exists
                if not
                        create artist (how?)
                else
                        create relation:
                        MATCH a1:Artist, a2:Artist
                        WHERE a1.kunstnernavn = akn AND a2.kunstnernavn = NNP
                        CREATE (a2)-[:WAS_PAINTEDBY]->(a1)
                        CREATE (a1)-[:HAS_PAINTED]->(a2)


        '''
        filter 
        #titel "Port af Ditlev Blunck."
        #kunstnernavn "Bendz, Wilhelm ": 
        #inventarnummer "KMS1653":       
        #datering "1819-1832 ":  teknik "Olie pred":        
        #optagelse "\\foto-02\globus\globus\40412628\img0070.jpg ":

        #MATCH (actor:Actor)
        #WHERE actor.name = "Tom Hanks"
        #CREATE (movie:Movie {title:'Sleepless in Seattle'})
        #CREATE (actor)-[:ACTED_IN]->(movie);

        #CREATE (actor:Actor {name:"Tom Hanks"});
        #CREATE (movie:Movie {title:'Sleepless in Seattle'})
        #CREATE (actor)-[:ACTED_IN]->(movie);

        mkMatch="MATCH (artist:Artist) "
        mkMatch=mkMatch + "WHERE artist.kunstnernavn = "

        mkArtWorkCr="CREATE (artwork:Artwork {"
        mkArtWorkRel="CREATE (artist)-[:CREATED_ARTWORK]->(artwork);"

        # title
        ati=artList[0]
        m=re.search('(^\w+) "(.*)"',ati, re.I)
        atikey = m.group(1)
        atival = m.group(2)
        atiretval = doTitleClean(atival)
        #pdb.set_trace()
        cmd = "/usr/local/twm/bin/testNLT.py " + "\"" + atiretval + "\"" 
        res = os.popen(cmd,"r").read()
        logging.debug("cmd: " + cmd)
        logging.debug("RES: " + res)
        mkArtWorkCr = mkArtWorkCr + atikey + ":'" + atiretval + "',"


        # kunstnernavn
        akn=artList[1]
        m=re.search('(^\w+) "(.*)"',akn, re.I)
        aknkey = m.group(1)
        aknval = m.group(2)
        aknretval=doName(aknval)
        mkMatch=mkMatch + "'" + aknretval['wholeN'] + "'"
        aknretval['wholeN']


        # inventarnr
        ain=artList[2]
        m=re.search('(^\w+) "(.*)"',ain)
        ainkey = m.group(1)
        ainval = m.group(2)
        mkArtWorkCr = mkArtWorkCr + ainkey + ":'" + ainval + "',"

        # date
        add=artList[3]
        m=re.search('(^\w+) "(.*)"',add)
        addkey = m.group(1)
        addval = m.group(2)
        addretval = doDate(addval)
        mkArtWorkCr = mkArtWorkCr + addkey + ":'" + addretval + "',"

        # teknik
        atk=artList[4]
        m=re.search('(^\w+) "(.*)"',atk)
        atkkey = m.group(1)
        atkval = m.group(2)
        mkArtWorkCr = mkArtWorkCr + atkkey + ":'" + atkval + "',"

        # link to img
        aim=artList[5]
        m=re.search('(^\w+) "(.*)"',aim)
        aimkey = m.group(1)
        aimval = m.group(2)
        aimretval = aimval
        #pdb.set_trace()
        #aimretval = re.sub('\\','%5C',aimval)
        mkArtWorkCr = mkArtWorkCr + aimkey + ":'" + aimretval + "',"
        '''
        mkArtistCypherStr = mkArtistCypherStr + knmkey + ":\"" + strN + "\","
        mkArtistCypherStr = mkArtistCypherStr + "firstname:\"" + surN + "\","
        mkArtistCypherStr = mkArtistCypherStr + "lastname:\"" + famN + "\","
        mkArtistCypherStr = mkArtistCypherStr + knakey + ":\"" + knaval + "\","
        mkArtistCypherStr = mkArtistCypherStr + kbikey + ":" + kbiretval + ","
        mkArtistCypherStr = mkArtistCypherStr + kdekey + ":" + kderetval + "})"
        '''
        logging.debug('MK: ' + mkMatch)
        mkArtWorkCr = re.sub(',$','',mkArtWorkCr)
        mkArtWorkCr = mkArtWorkCr + "})"


        outfile.write(mkMatch)
        outfile.write("\n")
        logging.debug('MC: ' + mkArtWorkCr)
        outfile.write(mkArtWorkCr)
        outfile.write("\n")
        logging.debug('MR: ' + mkArtWorkRel)
        outfile.write(mkArtWorkRel)
        outfile.write("\n")
        outfile.write("\n")

        # finishing line

        return mkArtWorkCr

def doArtist(artList):

        # kunstnerbirth "1804 ":        kunstnerdeath "1832 ":  kunstnernationalitet "dansk ":  
        # kunstnervirkested "Danmark; Italien ":  kunstnerdodsted "Vicenza ":
        #
        # CREATE (actor:Actor {name:"Tom Hanks"});
        mkArtistCypherStr="CREATE (artist:Artist {"

        kbi=artList[0]
        m=re.search('(^\w+) "(.*)"',kbi, re.I)
        kbikey = m.group(1)
        kbival = m.group(2)
        kbiretval=doDate(kbival)


        #kunster death
        kde=artList[1]
        m=re.search('(^\w+) "(.*)"',kde, re.I)
        kdekey = m.group(1)
        kdeval = m.group(2)
        kderetval=doDate(kdeval)

        #kunstner nationalitet
        kna=artList[2]
        m=re.search('(^\w+) "(.*)"',kna, re.I)
        knakey = m.group(1)
        knaval = re.sub(' ','',m.group(2))

        # kunstnervirkested
        kvi=artList[3]
        m=re.search('(^\w+) "(.*)"',kvi)
        kvikey = m.group(1)
        kvival = re.sub(' ','',m.group(2))

        # kunstnerdeathlocation
        kdd=artList[4]
        m=re.search('(^\w+) "(.*)"',kdd)
        kddkey = m.group(1)
        kddval = re.sub(' ','',m.group(2))

        #kunstnernavn
        knm=artList[6]
        m=re.search('(^\w+) "(.*)"',knm, re.I)
        knmkey = m.group(1)
        knmval = m.group(2)
        knmretvaldict = doName(knmval)

        mkArtistCypherStr = mkArtistCypherStr + knmkey + ":\"" + knmretvaldict['wholeN'] + "\","
        mkArtistCypherStr = mkArtistCypherStr + "firstname:\"" + knmretvaldict['firstN'] + "\","
        mkArtistCypherStr = mkArtistCypherStr + "lastname:\"" +  knmretvaldict['lastN']+ "\","
        mkArtistCypherStr = mkArtistCypherStr + kvikey + ":\"" +  kvival + "\","
        mkArtistCypherStr = mkArtistCypherStr + kddkey + ":\"" +  kddval + "\","
        mkArtistCypherStr = mkArtistCypherStr + knakey + ":\"" + knaval + "\","
        mkArtistCypherStr = mkArtistCypherStr + kbikey + ":" + kbiretval + ","
        mkArtistCypherStr = mkArtistCypherStr + kdekey + ":" + kderetval + "});"
        outfile.write(mkArtistCypherStr)
        outfile.write("\n")
        return mkArtistCypherStr

def doName(tmpnamestr):
        retN = {}
        whN = ""
        famN = ""
        tmpN = ""
        surN = ""
        namestr = re.sub(' ','',tmpnamestr)
        m=re.search('(.*),(.*)',namestr)
        m=re.search('(.*),(.*)',namestr)
        if m:
                firstN=m.group(2)
                lastN=m.group(1)
                tmpN=firstN + "_" + lastN
                whN=firstN + " " + lastN
        retN['firstN'] = firstN
        retN['lastN'] = lastN
        retN['wholeUnN'] = tmpN
        retN['wholeN'] = whN

        return retN


##############################################################
#
# titel "Kunstnere holder hvil ved et vejskilt "Roma". ":
# kunstnernavn "Bendz, Wilhelm ":
# inventarnummer "KKS1972-38/12":
# datering "1825 ":
# teknik "Blyant":
# optagelse "\\foto-02\globus\globus\GLOBUS 2012\kks1972-38_12.jpg ":

# (shakespeare:Author { firstname: 'William', lastname: 'Shakespeare' })
# (theTempest:Play { title: 'The Tempest' }),
# (theTempest:Play { title: 'The Tempest' }),
# (shakespeare)-[:WROTE_PLAY { year: 1610}]->(theTempest),
# titel "Billedhuggeren Hermann Ernst Freund
# inventarnummer "KKS266"
# datering "1829 "
# kunstnernavn "Bendz, Wilhelm "
# (WBendz:Person { firstname: 'Wilhelm', lastname: 'Bendz' })
# (KKS266:Artwork { title: 'Billedhuggeren Hermann Ernst Freund', teknik: 'Blyant' }),
# (WBendz)-[:WROTE_Artwork { year: 1829}]->(KKS266),
# (HEFreund:Person { firstname: 'Hermann Ernst', lastname: 'Freund' })
# (HEFreund)-[:_Artwork { year: 1829}]->(KKS266),
#
##############################################################

myfile = sys.argv[1]
ofile = sys.argv[2]

persons=[]
ages=[]
title=[]

infile=open(myfile,'r')
outfile=open(ofile,'w')

myhome="/usr/local/twm"
logging.basicConfig(filename=myhome+'/logs/thw.log',level=logging.DEBUG)

lines=infile.readlines()
# (WBendz)-[:WROTE_Artwork { year: 1829}]->(KKS266),
for line in lines:
        m=re.match('^kunstnerbirth',line)
        items=line.split('\t')
        if m:
                mkArtistLine=doArtist(items)
                items=items[5:12]

        mkArtWork=doArtWork(items)
        #if not artName['wholeN'] in persons:
        #        cypherline = "("+artName['wholeN']+"Person { firstname: '" + artName['firstN'] + "'lastname: '" + artName['lastN'] + "'})"
        #        persons.append(artName['wholeN'])
        #else:
        #print "got " + cypherline
#!/usr/bin/python

import xml.dom.minidom
import datetime
import sys
import os
import base64
import pdb
import codecs
import urllib2
import urllib
import re
import xml.etree.ElementTree as ET
import csv
import nltk
import re
import pprint
import logging

sys.path.append('../lib')
import config
import doWiki

reload(sys);
sys.setdefaultencoding("utf8")

def doTitleClean(tmpTitle):
        retval = tmpTitle
        m=re.match('(.*);',tmpTitle)
        if m:
                danishPart=m.group(1)
                retval = danishPart
        return retval

def doDate(tmpdateString):
        # "1804" 1613/1614 Enten 1564 eller 1566 1600-tallet" "Ca. 1576" "20-12-1920" "Ca. 1640-1660"
        # date -d "1801-01-01" "+%s"
        dateString=re.sub(' ','',tmpdateString)
        res="0"
        mon="06"
        day="12"
        
        m=re.match('(\d{2})-(\d{2})-(\d{4})',dateString)
        if m:
                day=m.group(1)
                mon=m.group(2)
                year=m.group(3)
                newstr=str(year) + "-" + str(mon) + "-" + str(day)
                cmd="/usr/bin/java getOldDate  \"" + newstr + "\""
                #cmd="date -d \"" + newstr + "\" \"+%s\""
                res = os.popen(cmd,"r").read()
                return res.rstrip()

        m=re.match('([\d]{4})',dateString)
        if m:
                year=m.group(0)
                newstr=str(year) + "-" + mon + "-" + day
                #cmd="date -d \"" + newstr + "\" \"+%s\""
                cmd="/usr/bin/java getOldDate " + newstr 
                res=os.popen(cmd,"r").read()
                return res.rstrip()

        else:
                return res
                

def doArtWork(artList):

        '''
        filter NNP
        if its a name
                lookup if artist exists
                if not
                        create artist (how?)
                else
                        create relation:
                        MATCH a1:Artist, a2:Artist
                        WHERE a1.kunstnernavn = akn AND a2.kunstnernavn = NNP
                        CREATE (a2)-[:WAS_PAINTEDBY]->(a1)
                        CREATE (a1)-[:HAS_PAINTED]->(a2)


        '''
        #titel "Port af Ditlev Blunck."
        #kunstnernavn "Bendz, Wilhelm ": 
        #inventarnummer "KMS1653":       
        #datering "1819-1832 ":  teknik "Olie pred":        
        #optagelse "\\foto-02\globus\globus\40412628\img0070.jpg ":

        #MATCH (actor:Actor)
        #WHERE actor.name = "Tom Hanks"
        #CREATE (movie:Movie {title:'Sleepless in Seattle'})
        #CREATE (actor)-[:ACTED_IN]->(movie);

        #CREATE (actor:Actor {name:"Tom Hanks"});
        #CREATE (movie:Movie {title:'Sleepless in Seattle'})
        #CREATE (actor)-[:ACTED_IN]->(movie);

        mkMatch="MATCH (artist:Artist) "
        mkMatch=mkMatch + "WHERE artist.kunstnernavn = "

        mkArtWorkCr="CREATE (artwork:Artwork {"
        mkArtWorkRel="CREATE (artist)-[:CREATED_ARTWORK]->(artwork);"

        # title
        relPersonAttrDict = {}
        ati=artList[0]
        m=re.search('(^\w+) "(.*)"',ati, re.I)
        atikey = m.group(1)
        atival = m.group(2)
        atiretval = doTitleClean(atival)
        #pdb.set_trace()
        cmd = "/home/thw/bin/testNLT.py " + "\"" + atiretval + "\"" 
        res = os.popen(cmd,"r").read()
        res = res.rstrip()
        logging.debug("cmd: " + cmd)
        logging.debug("RES: " + res)
        tmpLookupPerson = re.sub(' ','',res)

        # NER returned something
        # if in CS -> getPerson and related artworks
        # if not: -> look for node on semantic web

        if len(res) > 2:
                lookupcmd = "ssh root@apitest.smk.dk '/home/thw/bin/lookupPerson.sh " + tmpLookupPerson + "'"
                lookupres = os.popen(lookupcmd,'r').read()
                m=re.search(r'(\d+) row',lookupres)

                # This should be a hit
                pdb.set_trace()

                if m:

                        #do the person lookup

                        logging.debug('lookup: ' + m.group(1))

                        if m.group(1) == '0':
                                logging.debug(' person not in db: ')

                                # lookup on wiki
                        else:
                                logging.debug(' person in db: ')
                                relPersonCSID = getRelPersonCSID(res)
                                relPersonAttrDict = getRelPersonAttr(relPersonCSID,config.artistAttrList)
                                for k,v in relPersonAttrDict.iteritems():
                                        logging.debug(k+" -> "+v)
                                logging.debug(' relP: ' + relPersonCSID)
                else:
                        sys.exit('Error - no connection to CS')

        mkArtWorkCr = mkArtWorkCr + atikey + ":'" + atiretval + "',"


        # kunstnernavn
        akn=artList[1]
        m=re.search('(^\w+) "(.*)"',akn, re.I)
        aknkey = m.group(1)
        aknval = m.group(2)
        aknretval=doName(aknval)
        mkMatch=mkMatch + "'" + aknretval['wholeN'] + "'"
        aknretval['wholeN']


        # inventarnr
        ain=artList[2]
        m=re.search('(^\w+) "(.*)"',ain)
        ainkey = m.group(1)
        ainval = m.group(2)
        mkArtWorkCr = mkArtWorkCr + ainkey + ":'" + ainval + "',"

        # date
        add=artList[3]
        m=re.search('(^\w+) "(.*)"',add)
        addkey = m.group(1)
        addval = m.group(2)
        addretval = doDate(addval)
        mkArtWorkCr = mkArtWorkCr + addkey + ":'" + addretval + "',"

        # teknik
        atk=artList[4]
        m=re.search('(^\w+) "(.*)"',atk)
        atkkey = m.group(1)
        atkval = m.group(2)
        mkArtWorkCr = mkArtWorkCr + atkkey + ":'" + atkval + "',"

        # link to img
        aim=artList[5]
        m=re.search('(^\w+) "(.*)"',aim)
        aimkey = m.group(1)
        aimval = m.group(2)
        aimretval = aimval
        #pdb.set_trace()
        #aimretval = re.sub('\\','%5C',aimval)
        mkArtWorkCr = mkArtWorkCr + aimkey + ":'" + aimretval + "',"
        '''
        mkArtistCypherStr = mkArtistCypherStr + knmkey + ":\"" + strN + "\","
        mkArtistCypherStr = mkArtistCypherStr + "firstname:\"" + surN + "\","
        mkArtistCypherStr = mkArtistCypherStr + "lastname:\"" + famN + "\","
        mkArtistCypherStr = mkArtistCypherStr + knakey + ":\"" + knaval + "\","
        mkArtistCypherStr = mkArtistCypherStr + kbikey + ":" + kbiretval + ","
        mkArtistCypherStr = mkArtistCypherStr + kdekey + ":" + kderetval + "})"
        '''
        logging.debug('MK: ' + mkMatch)
        mkArtWorkCr = re.sub(',$','',mkArtWorkCr)
        mkArtWorkCr = mkArtWorkCr + "})"


        outfile.write(mkMatch)
        outfile.write("\n")
        logging.debug('MC: ' + mkArtWorkCr)
        outfile.write(mkArtWorkCr)
        outfile.write("\n")
        logging.debug('MR: ' + mkArtWorkRel)
        outfile.write(mkArtWorkRel)
        outfile.write("\n")
        outfile.write("\n")

        # finishing line

        return mkArtWorkCr

def getRelPersonAttr(csid,attrlist):

        '''
        getPersonstuffFromCSID.sh 6a0308c9-0eec-4b18-b614-1f96a6a9695d

        '''
        retval = {}

        retval = {}

        gCcmd ="/home/thw/bin/getPersonstuffFromCSID.sh " + csid
        resgC = os.popen(gCcmd,"r").read()
        resXml =  strip_ns(resgC)

        root = ET.fromstring(resXml)

        #api_results = ElementTree.parse(response).findall('.//track')
        #dom = xml.dom.minidom.parseString(resgC)
        #kunstnernationalitet -> urn:cspace:smk.dk:vocabularies:name(personNationality):item:name(dansk)'dansk'
        for key, val in config.artistAttrList.iteritems():
                element = root.findall('.//%s' % (val))
                try:
                        tmpval = element[0].text
                        m = re.search("urn.*\'(.*)\'$",tmpval)
                        if m:
                                retval[key] = m.group(1)
                        else:
                                retval[key] = element[0].text
                                logging.debug("got %s " % retval[key])
                except:
                        logging.error("error on %s -> %s " %(key,val))
                '''
                for elem in element:
                        retval = elem.text
                        logging("tes %s" % retval)
                '''
        logging.debug("done ..")
        return retval
        

def doArtist(artList):
        retval=""

        return retval

def getRelPersonCSID(nreName):

        retval = ""
        nospaceName = re.sub(' ','',nreName)
        plusSpacName = re.sub(' ','+',nreName)
        m = re.match(r'(\w+) (\w+)',nreName)
        if m:
                try:
                        fName=m.group(1)
                        lName=m.group(2)
                except:
                        logging("got error")

        #gCcmd = "/home/thw/bin/getPersonCsidFromName.sh " + lName 
        gCcmd = "/home/thw/bin/getPersonCsiFromFullName.sh " + plusSpacName
        resgC = os.popen(gCcmd,"r").read()
        m=re.search('<itemsInPage>(\d+)',resgC)
        if m:
                itemsfound=m.group(1)
        else:
                #should be match so exit with error
                sys.exit('Error in request to CollSpace')

        if itemsfound > 0:
                #root = ET.fromstring(resgC)
                dom = xml.dom.minidom.parseString(resgC)
                nodelist = dom.getElementsByTagName('list-item')
                for node in nodelist:
                         test=node.getElementsByTagName('csid')
                         mcsid=test[0].firstChild.nodeValue
                         retval = mcsid

        else:
                logging.info(nreName + " not found in CS-domaine.")
                retval = nreName + " not found in CS"

        return retval
        


def doArtist(artList):

        # kunstnerbirth "1804 ":        kunstnerdeath "1832 ":  kunstnernationalitet "dansk ":  
        # kunstnervirkested "Danmark; Italien ":  kunstnerdodsted "Vicenza ":
        #
        # CREATE (actor:Actor {name:"Tom Hanks"});
        mkArtistCypherStr="CREATE (artist:Artist {"

        kbi=artList[0]
        m=re.search('(^\w+) "(.*)"',kbi, re.I)
        kbikey = m.group(1)
        kbival = m.group(2)
        kbiretval=doDate(kbival)


        #kunster death
        kde=artList[1]
        m=re.search('(^\w+) "(.*)"',kde, re.I)
        kdekey = m.group(1)
        kdeval = m.group(2)
        kderetval=doDate(kdeval)

        #kunstner nationalitet
        kna=artList[2]
        m=re.search('(^\w+) "(.*)"',kna, re.I)
        knakey = m.group(1)
        knaval = re.sub(' ','',m.group(2))

        # kunstnervirkested
        kvi=artList[3]
        m=re.search('(^\w+) "(.*)"',kvi)
        kvikey = m.group(1)
        kvival = re.sub(' ','',m.group(2))

        # kunstnerdeathlocation
        kdd=artList[4]
        m=re.search('(^\w+) "(.*)"',kdd)
        kddkey = m.group(1)
        kddval = re.sub(' ','',m.group(2))

        #kunstnernavn
        knm=artList[6]
        m=re.search('(^\w+) "(.*)"',knm, re.I)
        knmkey = m.group(1)
        knmval = m.group(2)
        knmretvaldict = doName(knmval)

        mkArtistCypherStr = mkArtistCypherStr + knmkey + ":\"" + knmretvaldict['wholeN'] + "\","
        mkArtistCypherStr = mkArtistCypherStr + "firstname:\"" + knmretvaldict['firstN'] + "\","
        mkArtistCypherStr = mkArtistCypherStr + "lastname:\"" +  knmretvaldict['lastN']+ "\","
        mkArtistCypherStr = mkArtistCypherStr + kvikey + ":\"" +  kvival + "\","
        mkArtistCypherStr = mkArtistCypherStr + kddkey + ":\"" +  kddval + "\","
        mkArtistCypherStr = mkArtistCypherStr + knakey + ":\"" + knaval + "\","
        mkArtistCypherStr = mkArtistCypherStr + kbikey + ":" + kbiretval + ","
        mkArtistCypherStr = mkArtistCypherStr + kdekey + ":" + kderetval + "});"
        outfile.write(mkArtistCypherStr)
        outfile.write("\n")
        return mkArtistCypherStr

def doName(tmpnamestr):
        retN = {}
        whN = ""
        famN = ""
        tmpN = ""
        surN = ""
        namestr = re.sub(' ','',tmpnamestr)
        m=re.search('(.*),(.*)',namestr)
        m=re.search('(.*),(.*)',namestr)
        if m:
                firstN=m.group(2)
                lastN=m.group(1)
                tmpN=firstN + "_" + lastN
                whN=firstN + " " + lastN
        retN['firstN'] = firstN
        retN['lastN'] = lastN
        retN['wholeUnN'] = tmpN
        retN['wholeN'] = whN

        return retN

def strip_ns(xml_string):
        return re.sub('xmlns="[^"]+"', '', xml_string)

##############################################################
#
# titel "Kunstnere holder hvil ved et vejskilt "Roma". ":
# kunstnernavn "Bendz, Wilhelm ":
# inventarnummer "KKS1972-38/12":
# datering "1825 ":
# teknik "Blyant":
# optagelse "\\foto-02\globus\globus\GLOBUS 2012\kks1972-38_12.jpg ":

# (shakespeare:Author { firstname: 'William', lastname: 'Shakespeare' })
# (theTempest:Play { title: 'The Tempest' }),
# (theTempest:Play { title: 'The Tempest' }),
# (shakespeare)-[:WROTE_PLAY { year: 1610}]->(theTempest),
# titel "Billedhuggeren Hermann Ernst Freund
# inventarnummer "KKS266"
# datering "1829 "
# kunstnernavn "Bendz, Wilhelm "
# (WBendz:Person { firstname: 'Wilhelm', lastname: 'Bendz' })
# (KKS266:Artwork { title: 'Billedhuggeren Hermann Ernst Freund', teknik: 'Blyant' }),
# (WBendz)-[:WROTE_Artwork { year: 1829}]->(KKS266),
# (HEFreund:Person { firstname: 'Hermann Ernst', lastname: 'Freund' })
# (HEFreund)-[:_Artwork { year: 1829}]->(KKS266),
#
##############################################################
# curl -u admin@smk.dk:LauritsA0 http://localhost:8180/cspace-services/personauthorities/359b7d4a-f82f-492b-b6ec/items\?kw=Bendz
# curl -u admin@smk.dk:LauritsA0  http://localhost:8180/cspace-services/personauthorities/3575aeaa-75ee-424f-98ce/items/6a0308c9-0eec-4b18-b614-1f96a6a9695d
##############################################################

artistName = sys.argv[1]
ofile = sys.argv[2]

persons=[]
ages=[]
title=[]

infile=open(myfile,'r')
outfile=open(ofile,'w')

myhome="/home/thw"
logging.basicConfig(filename=myhome+'/logs/thw.log',level=logging.DEBUG)
logging.info(" ------- " + str(datetime.date.today()) + "--------")
lines=infile.readlines()
# (WBendz)-[:WROTE_Artwork { year: 1829}]->(KKS266),
for line in lines:
        m=re.match('^kunstnerbirth',line)
        items=line.split('\t')
        if m:
                mkArtistLine=doArtist(items)
                items=items[5:12]

        mkArtWork=doArtWork(items)
        #if not artName['wholeN'] in persons:
        #        cypherline = "("+artName['wholeN']+"Person { firstname: '" + artName['firstN'] + "'lastname: '" + artName['lastN'] + "'})"
        #        persons.append(artName['wholeN'])
