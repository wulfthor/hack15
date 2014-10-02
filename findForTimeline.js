cursor = db.stories.find({},{'byline':0,'newspaperEditionDate':0,'headline':0,'sectionName':0,'sectionId':0,'wordcount':0,'newspaperPageNumber':0,'Trail':0,'webPublicationDate':0,'Tags':0,'newsPaperEditionDate':0,'_id':0});
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}
