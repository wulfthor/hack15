#!/bin/bash 

srcfile="/tmp/test.js"
dstfile="/tmp/tmpdest.json"
finalfile="/tmp/dest.json"

qString="{"
dString="{"
while [[ $# > 0 ]]
do
key="$1"
shift

case $key in
    -x|--category)
	qString="$qString \"$1\""
    shift
    ;;
    -y|--content)
	qString="${qString}:$1"
    shift
    ;;
    -t|--title)
    title_dk="$1"
	dString="${dString},'title_dk':$1"
    shift
    ;;
    -k|--artist)
    artist_name="$1"
	dString="${dString},'artist_name':$1"
    shift
    ;;
    -kd|--artists_data)
    artists_data="$1"
	dString="${dString},'artists_data':$1"
    shift
    ;;
    -i|--id)
    id="$1"
	dString="${dString},'id':$1"
    shift
    ;;
    -a|--acqdate)
    acq_date="$1"
	dString="${dString},'acq_date':$1"
    shift
    ;;
    -e|--dateE)
    object_production_date_earliest="$1"
	dString="${dString},'object_production_date_earliest':$1"
    shift
    ;;
    -l|--dateL)
    object_production_date_latest="$1"
	dString="${dString},'object_production_date_latest':$1"
    shift
    ;;
    -dt|--dateText)
    object_production_date="$1"
	dString="${dString},'object_production_date':$1"
    shift
    ;;
    -t|--technique)
    prod_technique_dk="$1"
	dString="${dString},'prod_technique_dk':$1"
    shift
    ;;
    -h|--help)
    helpString="usage: doOps.sh -x [artist_name|id|title_dk] -y [<content>] -[t|k|kd|i|a|e|l|t] [0|1]"
	echo "$helpString"
	exit 0
    ;;
esac
done

dString=`echo $dString | sed 's/{,/{/g'`
totalString="${qString} },${dString},'_id':0}"
echo "Vi har $totalString"

cat  <<_EOF_ > $srcfile

cursor = db.smkdata.find($totalString);
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}
_EOF_
/usr/local/bin/mongo --quiet localhost:27017 $srcfile | sed 's/}/},/g' > $dstfile 
cat $dstfile | sed '1 s/{/[{/' | sed '$s/},/}]/' > $finalfile
cat $finalfile




