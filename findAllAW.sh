#!/bin/bash

theme=$1
option=$2
srcfile="/tmp/test.js"
dstfile="/tmp/tmpdest.json"
finalfile="/tmp/dest.json"

cat  <<_EOF_ > $srcfile

cursor = db.smkdata.find({'title_dk':"$theme"},{'title_dk':1,'artist_name':1,'artist_data':0,'id':0,'prod_technique_dk':0,'object_type':0,'object_production_date_latest':0,'object_production_date_earliest':0,'acq_method':0,'acq_source':0,'_id':0});
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}
_EOF_
/usr/local/bin/mongo --quiet localhost:27017 $srcfile | sed 's/}/},/g' > $dstfile 
cat $dstfile | sed '1 s/{/[{/' | sed '$s/},/}]/' > $finalfile
cat $finalfile




