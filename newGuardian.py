#!/usr/bin/python

# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import requests
import datetime
import calendar
import urllib2
import json
import re
import pdb
import sys, getopt
from requests_oauthlib import OAuth1
from urlparse import parse_qs
from pymongo import MongoClient

# Connection to Mongo DB
try:
    client=MongoClient('192.168.10.31', 27017)
    print "Connected successfully!!!"
except pymongo.errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e 

db = client.harvest
stories = db.stories
key = "5332f3mgcz7kh8hfxdctehgh"
starturl="http://beta.content.guardianapis.com"
# open file

# insert story



def main():

        count=20
        method="searcht"
        origstring=""
        optionstr=""
        filelocation="/tmp/test.txt"
        test=0
        debug=0
        lang="da"

        try:
          opts, args = getopt.getopt(sys.argv[1:],"s:g:h:m:c:dta:f:i:j:w:")
          for o, a in opts:
            if o == "-s":
              origstring = a
              searchstring = urllib2.quote(a.encode('utf8'))
            elif o == "-g":
              fromdate = a
              optionstr=optionstr+"&from-date="+fromdate
            elif o == "-h":
              todate = a
              optionstr=optionstr+"&to-date="+todate
            elif o == "-i":
              tag = a
              optionstr=optionstr+"&tag=type/"+tag
            elif o == "-m":
              method = a
            elif o == "-c":
              count = a
              optionstr=optionstr+"&page-size="+count
            elif o == "-j":
              pagenumber = a
              optionstr=optionstr+"&page="+pagenumber
            elif o == "-w":
              wordcount = a
              optionstr=optionstr+"&min-wordcount=2&max-wordcount="+wordcount
            elif o == "-t":
              test = 1
            elif o == "-d":
              debug = 1
            elif o == "-f":
              filelocation = a
            elif o == "-l":
              lang = a
            else:
              assert False, "unhandled option"

        except getopt.GetoptError as err:
          print(err)
          sys.exit(2)


        baseurl=starturl + "/search?q=" + searchstring + optionstr
        endurl="&show-fields=all&show-tags=all&show-factboxes=all&show-elements=all&show-references=all&show-snippets=all&api-key=" + key
        #endurl="&show-fields=all&show-tags=all&show-factboxes=all&show-elements=all&show-references=all&show-snippets=all&api-key=mediahackdays2014"
        # http://content.guardianapis.com/search?q=cameron&tag=type%2Farticle&show-tags=all&api-key=mediahackdays2014
        #http://content.guardianapis.com/search?q=maria+miller&tag=type%2Fvideo&show-tags=all
        url=baseurl+endurl

        print url
        r = requests.get(url=url)
        #print json.dumps(input, sort_keys = False, indent = 4)
        #print json.dumps(r,sort_keys = False, indent = 4)
        newdata = json.loads(r.text)
        #wanted = {u'id',u'webTitle',u'newspaperPageNumber'}
        #[i for i in newdata[u'response'] if any(w in newdata for w in i[u'results'])]

        if debug:
          with open(filelocation,"w") as fh:
            json.dumps(r.text,fh)
          count=0
          #print len(newdata)
        if method == "timeline":
          for row in newdata:
            fh.write(newdata[count]['text'])
        elif method == "searcht":
          for k in newdata['response']['results']:
            data={}
            res=0
            tmpID=k['id'].encode('utf8')
            myID=tmpID.replace('/','_')
            #results = list(stories.find({'_id':myID}))
            cursor = stories.find({'_id':myID})
            obj = next(cursor, None)
            #pdb.set_trace()
            if obj:
              print "OK " + str(obj)
              continue
            else:
              print "NOT found " + myID

            data['_id']=tmpID.replace('/','_')
            print "ID:" + k['id'].encode('utf8') + myID


            print "sectionId:" + k['sectionId']
            mysectionId=k['sectionId']
            data['sectionId']=mysectionId

            print "sectionName:" + k['sectionName']
            mysectionName=k['sectionName']
            data['sectionName']=mysectionName

            print "WebPublicationDate:" + k['webPublicationDate']
            mytmpWebPublicationDate=k['webPublicationDate']
            myWebPublicationDate = mytmpWebPublicationDate.split("T")[0]
            myStoryDate=myWebPublicationDate.split("-")
            myDate=myStoryDate[2] + " " + monthToNum(myStoryDate[1]) + " " + myStoryDate[0]
            data['webPublicationDate']=myWebPublicationDate
            data['date']=myDate
            data['displaydate']=myDate

            print "WebTitle:" + k['webTitle']
            myTitle=k['webTitle']
            data['title']=myTitle

            print "readmoreurl:" + k['webUrl']
            myreadmoreurl=k['webUrl']
            data['readmoreurl']=myreadmoreurl

            print "TRAIL:" + k['fields']['trailText']
            myTrail=k['fields']['trailText']
            data['Trail']=myTrail

            print "headline:" + k['fields']['headline']
            myheadline=k['fields']['headline']
            data['headline']=myheadline

            try:
              print "byline:" + k['fields']['byline']
              mycaption=k['fields']['byline']
              #data['byline']=mycaption
              data['byline']=mycaption
              data['caption']=origstring
            except:
              print "ups on caption .."
              #data['caption']="lorem ipsum"

            try:
              print "wordcount:" + k['fields']['wordcount']
              mywordcount=k['fields']['wordcount']
              data['wordcount']=mywordcount
            except:
              print "ups on wordcount .."
              data['wordcount']=0

            try:
              print "photourl:" + k['fields']['thumbnail']
              mythumbnail=k['fields']['thumbnail']
              data['photourl']=mythumbnail
            except:
              print "No photo on wordcount .."
              data['photourl']=""

            #print "BODY:" + k['fields']['body']
            myBody=k['fields']['body']

            #print "BODY:" + k['fields']['body']
            myBody=k['fields']['body']
            # clean up for timeline
            timeBody=doClean(myBody)

            data['FullBody']=myBody
            data['body']=timeBody

  
            try:
              print "PAGENO:" + k['fields']['newspaperPageNumber']
              myPageNo=k['fields']['newspaperPageNumber']
              data['newspaperPageNumber']=myPageNo
            except:
              print "ups on newpaper .."
              data['newspaperPageNumber']=0

            try:
              print "DATE:" + k['fields']['newspaperEditionDate']
              myDate=k['fields']['newspaperEditionDate']
              data['newspaperEditionDate']=myDate
              #data['date']=myDate
            except:
              print "ups on eddate .."
              data['newspaperEditionDate']="1970-01-01"
              #data['date']="1970-01-01"

            tmpStr=""
            for j in k['tags']:
              tmpStr=tmpStr + "," + j['webTitle']

            print "--> " + tmpStr
            data['Tags']=tmpStr


            if test:
              print "Just testing ..."
              #stories.update(data, upsert=True)
            else:
              print "inserting data ..."
              stories.insert(data)

def doClean(bodytext):
  retval="lorem"
  retval=re.sub('<[^<]+?>', '', bodytext)
  return retval[:200]


def monthToNum(date):
  myDate=int(date.replace("0",""))

  monthDict={1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
  retval=monthDict[myDate]
  return retval

if __name__ == "__main__":
  main()
  #r = requests.get(url="https://api.twitter.com/1.1/statuses/mentions_timeline.json", auth=oauth)
  #r = requests.get(url="https://api.twitter.com/1.1/search/tweets.json?q=%23freebandnames&since_id=24012619984051000&max_id=250126199840518145&result_type=mixed&count=4", auth=oauth)
