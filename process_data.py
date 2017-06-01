from __future__ import print_function
import numpy as np
import pandas as pd
import os
import csv
import hashlib
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("mode", help="train or test")
args = parser.parse_args()
if args.mode == 'test':
    path = "joined_test.csv"
else:
    path = "joined.csv"
categorical = ["clickTime", "creativeID", "userID", "positionID", "connectionType", "telecomsOperator", "adID", "camgaignID", "advertiserID", "Ad_appID", "appPlatform", "gender", "education", "marriageStatus", "haveBaby", "hometown", "residence", "sitesetID", "positionType", "appCategory"]
numerical = ["age"]
NR_BINS = 3000000

def hashstr(input):
    return str(int(hashlib.md5(input.encode('utf8')).hexdigest(), 16)%(NR_BINS-1)+1)

def csvToFFM():
    joinedData = csv.DictReader(open(path, 'r'))
    if args.mode == 'test':
        fname = "ffm_test.txt"
    else:
        fname = "ffm.txt"

    ffmFile = open(fname, 'w')
    for row in joinedData:
        ffmFile.write(row['label']+" ")
        line = []
        for index, categoricalLable in enumerate(categorical):
            if (categoricalLable == "clickTime"):
                row[categoricalLable] = row[categoricalLable][2:4]
            tempstr = "{0}:{1}:1".format(index, hashstr(categoricalLable+row[categoricalLable]))
            line.append(tempstr)
        for newIndex, numericalLabel in enumerate(numerical):
            tempstr = "{0}:{1}:{2}".format(index + newIndex + 1, hashstr(numericalLabel), row[numericalLabel])
            line.append(tempstr)
        ffmFile.write(" ".join(line) + "\n")
    ffmFile.close()

if __name__ == "__main__":
    csvToFFM()

