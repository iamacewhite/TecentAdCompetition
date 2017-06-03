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
categorical = ["clickTime", "creativeID", "userID", "positionID", "connectionType", "telecomsOperator", "weekDay", "Hour", "clickTimeCategory", "ageCategory", "adID", "camgaignID", "advertiserID", "Ad_appID", "appPlatform", "gender", "education", "marriageStatus", "haveBaby", "hometown", "residence", "sitesetID", "positionType", "appCategory", "appFirstLevelCategory", "hometownProvince", "residenceProvince", "isHometownAndResidenceProvinceSame"]
numerical = ["age", "appAdIdCount", "appCampaignIdCount", "CategoryCount", "appCount", "appUserCount"]
NR_BINS = 3000000

def decomposeObjStr(string):
    return map(lambda obj: [obj.split(':')[0].strip(), int(obj.split(':')[1])],string.strip('{}').split(','))

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
        count = 0
        for index, categoricalLable in enumerate(categorical):
            if (categoricalLable == "clickTime"):
                row[categoricalLable] = row[categoricalLable][2:4]
            tempstr = "{0}:{1}:1".format(count, hashstr(categoricalLable+row[categoricalLable]))
            line.append(tempstr)
            count += 1
        for newIndex, numericalLabel in enumerate(numerical):
            if (numericalLabel == "CategoryCount"):
		categoryCount = decomposeObjStr(row[numericalLabel])
                for arr in categoryCount:
		    value = arr[1]
                    key = arr[0]
                    tempstr = "{0}:{1}:{2}".format(count, hashstr(numericalLabel + key), value)
                    line.append(tempstr)
                    count += 1
            else:
                tempstr = "{0}:{1}:{2}".format(count, hashstr(numericalLabel), row[numericalLabel])
                line.append(tempstr)
                count += 1
        ffmFile.write(" ".join(line) + "\n")
    ffmFile.close()

if __name__ == "__main__":
    csvToFFM()

