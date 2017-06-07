from __future__ import print_function
import numpy as np
import pandas as pd
import os
import csv
import hashlib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("mode", help="train or test")
parser.add_argument("coverage", help="complete or incomplete")
args = parser.parse_args()
if args.mode == 'test' and args.coverage == 'complete':
    path = "joined_test_new_field.csv"
elif args.mode == 'test' and args.coverage == 'incomplete':
    path = "joined_test_without_new_field.csv"
elif args.mode == 'train' and args.coverage == 'complete':
    path = "joined_withNewFeature.csv"
else:
    path = "joined.csv"
categorical = ["creativeID", "userID", "positionID", "connectionType", "telecomsOperator", "weekDay", "Hour", "clickTimeCategory", "ageCategory", "adID", "camgaignID", "advertiserID", "Ad_appID", "appPlatform", "gender", "education", "marriageStatus", "haveBaby", "hometown", "residence", "sitesetID", "positionType", "appCategory", "appFirstLevelCategory", "hometownProvince", "residenceProvince", "isHometownAndResidenceProvinceSame"]
if args.coverage == 'complete': 
    numerical = ["age", "appAdIdCount", "appCampaignIdCount", "appCount", "appUserCount", "UserAppCateCount", "userCountPerPosition", "userCountPerSite"]
else:
    numerical = ["age", "appAdIdCount", "appCampaignIdCount", "advertiserIDCount", "camgaignIDCount", "adIDCount", "positionCountPerSite", "userCountPerPosition", "userCountPerSite", "NumberOfAppPerCategory", "creativeIDUserCount"]
    numerical = ["age", "appAdIdCount", "appCampaignIdCount"]
numerical = []
NR_BINS = 3000000

def decomposeObjStr(string):
    return map(lambda obj: [obj.split(':')[0].strip(), int(obj.split(':')[1])],string.strip('{}').split(','))

def hashstr(input):
    return str(int(hashlib.md5(input.encode('utf8')).hexdigest(), 16)%(NR_BINS-1)+1)

def csvToFFM():
    joinedData = csv.DictReader(open(path, 'r'))
    if args.mode == 'test':
        if args.coverage == 'complete':
            fname = "ffm_test_complete.txt"
        else:
            fname = "ffm_test_incomplete.txt"
    else:
        if args.coverage == 'complete':
            fname = "ffm_complete.txt"
        else:
            fname = "ffm_incomplete.txt"

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
            if (numericalLabel == "CategoryCount" and row[numericalLabel]!=-1):
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

