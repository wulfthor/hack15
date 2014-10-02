#!/usr/bin/python

import re


fh=open("/tmp/inocming","r")

lines=fh.readlines()

nList=[]

for line in lines:
  print line
  names=line.split(',')
  for name in names:
    if name in nList:
      continue
    else:
      nList.append(name)


for test in nList:
  print test





