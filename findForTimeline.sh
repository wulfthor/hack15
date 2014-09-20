#!/bin/bash

theme=$1
option=$2
srcfile="/tmp/test.js"
dstfile="/tmp/tmpdest.json"
finalfile="/tmp/dest.json"

cat  <<_EOF_ > $srcfile

cursor = db.stories.find({'caption':"$theme"},{'byline':0,'FullBody':0,'newspaperEditionDate':0,'headline':0,'sectionName':0,'sectionId':0,'wordcount':0,'newspaperPageNumber':0,'Trail':0,'webPublicationDate':0,'Tags':0,'newsPaperEditionDate':0,'_id':0});
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}
_EOF_
/usr/bin/mongo --quiet localhost:27017/harvest $srcfile | sed 's/}/},/g' > $dstfile 
cat $dstfile | sed '1 s/{/[{/' | sed '$s/},/}]/' > $finalfile




