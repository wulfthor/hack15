#!/usr/bin/python

import re
import sys


reload(sys);
sys.setdefaultencoding("utf8")

fh=open(sys.argv[1],"r")
fhou=open("/tmp/outgoing","w")


lines=fh.readlines()

nList=[]

for line in lines:
  #print line
  names=line.split(',')
  for name in names:
    if name in nList:
      continue
    else:
      if re.match('^[^0-9]$',name):
        print "short ..." + name
      else:
        nList.append(name)
      #print "app: " + name


for test in sorted(nList):
  fhou.write(test + "\n")

fhou.close()
fh.close()
