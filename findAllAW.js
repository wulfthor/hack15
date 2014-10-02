cursor = db.smkdata.find({},{'_id':0});
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}
