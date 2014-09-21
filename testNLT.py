#!/usr/bin/python

import nltk
import re
import pdb
import pprint
import sys
import logging

'''

to do
this needs to be captured by the pos-tagger
 "Marie Raffenberg, kunstnerens forlovede"
'''


def cleanDoc(doc):
        tmpDoc = ""
        tmpDoc = re.sub('\(|\)','',doc)
        m = re.match('^([A-Z])',tmpDoc)
        if m:
                repl =  m.group(1).lower()
                tmpDoc = re.sub(m.group(1),repl,tmpDoc)

        return tmpDoc
        

def ie_preprocess(doc):
        tmpDoc = cleanDoc(doc)
        logging.debug(tmpDoc)
        docList = tmpDoc.split(' ')
        filtered_doc = [w for w in docList if not w in nltk.corpus.stopwords.words('english')]
        resSt = ""
        sx = ' '.join(filtered_doc)
        logging.debug('sx: ' + sx)
        sentences = nltk.sent_tokenize(sx)
        logging.debug('st: ' + str(sentences))
        toksentences = [nltk.word_tokenize(sent) for sent in sentences]
        logging.debug('tok: ' + str(toksentences))

        tagsentences = [nltk.pos_tag(sent) for sent in toksentences]
        logging.debug('tag: ' + str(tagsentences))
        logging.debug(tagsentences)

        res=re.findall(r'(\w+)\', \'NNP',str(tagsentences))
        if len(res) > 1:
                resSt = res[0] + " " + res[1]
        return resSt


def main():
        myhome="/usr/local/twm"
        logging.basicConfig(filename=myhome+'/logs/thw.log',level=logging.DEBUG)

        retval = ie_preprocess(sys.argv[1])
        print retval
if __name__ == '__main__':
        main()

