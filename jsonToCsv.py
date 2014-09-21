#!/usr/bin/python

import csv, json, sys
reload(sys)
sys.setdefaultencoding("utf8")

input = open(sys.argv[1])
data = json.load(input)
input.close()

output = csv.writer(sys.stdout)

output.writerow(data[0].keys())  # header row

for row in data:
    output.writerow(row.values())
    print(row.keys())
