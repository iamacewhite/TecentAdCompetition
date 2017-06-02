import pandas as pd
import numpy as np
import csv, os
import argparse
import json
import time

parser = argparse.ArgumentParser()
parser.add_argument("mode", help="train or test")
args = parser.parse_args()

path = './pre'

def appadIDCount():
    adFile = open(os.path.join(path, 'ad.csv'), 'r')
    adData = pd.read_csv(adFile)
    ids = pd.Series.unique(adData['appID'])
    adFile.close()
    adFile = open(os.path.join(path, 'ad.csv'), 'r')
    adDict = csv.DictReader(adFile)
    idCount = {}
    for id in ids:
        idCount[id] = set()
    for row in adDict:
        idCount[int(row['appID'])].add(row['adID'])
    count = []
    for id in ids:
        count.append(len(idCount[id]))
    adFile.close()
    result = pd.DataFrame({'appID': ids, 'appAdIdCount': count})
    return result

def appCampaignIDCount():
    adFile = open(os.path.join(path, 'ad.csv'), 'r')
    adData = pd.read_csv(adFile)
    ids = pd.Series.unique(adData['appID'])
    adFile.close()
    adFile = open(os.path.join(path, 'ad.csv'), 'r')
    adDict = csv.DictReader(adFile)
    idCount = {}
    for id in ids:
        idCount[id] = set()
    for row in adDict:
        idCount[int(row['appID'])].add(row['camgaignID'])
    count = []
    for id in ids:
        count.append(len(idCount[id]))
    adFile.close()
    result = pd.DataFrame({'appID': ids, 'appCampaignIdCount': count})
    return result

def splitFeature(filename,IDFieldName,FieidtoSpilt,NewFieldName,startIndex=None,endIndex=None,postprocessFunction=None,inplaceMergeSrc=None):
    with open(filename,'r') as csvFile:
        csvData = csv.DictReader(csvFile)
        IDs=[]
        tmps=[]

        for row in csvData:
            if not startIndex and not endIndex:
                tmp = row[FieidtoSpilt]
            elif not startIndex:
                tmp = row[FieidtoSpilt][:endIndex]
            elif not endIndex:
                tmp = row[FieidtoSpilt][startIndex:]
            else:
                tmp = row[FieidtoSpilt][startIndex:endIndex]

            if not tmp:
                tmp=0

            if postprocessFunction:
                tmp = postprocessFunction(int(tmp))

            tmps.append(int(tmp))
            if IDFieldName:
                IDs.append(int(row[IDFieldName]))   

    if inplaceMergeSrc is not None:
        inplaceMergeSrc[NewFieldName] = tmps
        result = inplaceMergeSrc
    else:
        result = pd.DataFrame({IDFieldName:IDs,NewFieldName:tmps})

    return result

def discreteFeature(filename,IDFieldName,FieidtoDiscrete,NewFieldName,startIndex=None,endIndex=None,threshold=[],inplaceMergeSrc=None,zeroRepresentUnknown=False):
    def discrete(value):
        if zeroRepresentUnknown and value == 0:
            return 0
        for index, curThreshold in enumerate(threshold):
            if value<curThreshold:
                return index+1
        return index+2
    return splitFeature(filename,IDFieldName,FieidtoDiscrete,NewFieldName,startIndex=startIndex,endIndex=endIndex,postprocessFunction=discrete,inplaceMergeSrc=inplaceMergeSrc)

def splitCategory(filename):
    return splitFeature(filename,'appID','appCategory','appFirstLevelCategory',endIndex=1)    

def splitHometown(filename):
    return splitFeature(filename,'userID','hometown','hometownProvince',endIndex=-2)

def splitResidence(filename):
    return splitFeature(filename,'userID','residence','residenceProvince',endIndex=-2)    

def splitWeekday(filename,inplaceMergeSrc=None):
    return splitFeature(filename,'','clickTime','weekDay',endIndex=2,postprocessFunction=lambda x: x%7,inplaceMergeSrc=inplaceMergeSrc)

def splitHour(filename,inplaceMergeSrc=None):
    return splitFeature(filename,'','clickTime','Hour',startIndex=2,endIndex=4,inplaceMergeSrc=inplaceMergeSrc)

def discreteAge(filename):
    ageThreshold=[7,18,41,66,80]
    return discreteFeature(filename,'userID','age','ageCategory',threshold=ageThreshold,zeroRepresentUnknown=True)

def discreteClickTime(filename,inplaceMergeSrc=None):
    timeThreshold=[7,12,19]
    return discreteFeature(filename,'','clickTime','clickTimeCategory',startIndex=2,endIndex=4,threshold=timeThreshold,inplaceMergeSrc=inplaceMergeSrc)

def IsHometownAndResidenceProvinceSame(pdDataframe):
    def isSame(x,y):
        if x==0 or y==0:
            return 0
        elif x==y:
            return 1
        else:
            return 2
    pdDataframe['isHometownAndResidenceProvinceSame'] = pdDataframe.apply(lambda row: isSame(row['hometownProvince'],row['residenceProvince']), axis=1)

#count is stored using a json string
def processInstalledApp(mode):
    result = None
    with open(path + '/user_installedapps.csv', 'r') as installedFile:
        with open(path + '/app_categories.csv', 'r') as categoryFile:
            installedPd = pd.read_csv(installedFile)
            categoryPd = pd.read_csv(categoryFile)
            ids = pd.Series.unique(installedPd['userID'])
            categories = pd.Series.unique(categoryPd['appCategory'])
            app_category_Mapping = {}
            for _, appCategory in categoryPd.iterrows():
                app_category_Mapping[int(appCategory['appID'])] = appCategory['appCategory']
            if mode == "ID":
                userApp = {key:"" for key in ids}
                for id in ids:
                    userApp[id] = ""
                for _, row in installedPd.iterrows():
                    userApp[int(row['userID'])] += str(row['appID'])
                result = pd.DataFrame({'userID': userApp.keys(), 'userAppID': userApp.values()})
            if mode == "Category":
                print "Category"
                userAppCategory = {key: {x:0 for x in categories} for key in ids}
                for _, row in installedPd.iterrows():
                    UserID = int(row["userID"])
                    AppID = int(row["appID"])
                    userAppCategory[UserID][app_category_Mapping[AppID]] += 1
                print "finish count"
                result = pd.DataFrame({'userID': userAppCategory.keys(), 'CategoryCount': userAppCategory.values()})
                result.to_csv('categoryCount.csv', sep=',')
            if mode == "appCount":
                print "appCount"
                userAppCount = {int(key): 0 for key in ids}
                for _, row in installedPd.iterrows():
                    userAppCount[int(row['userID'])] += 1
                print "finish Count"
                result = pd.DataFrame({'userID': userAppCount.keys(), 'appCount': userAppCount.values()})
                result.to_csv('appCount.csv', sep=',')
    return result




def main():
    content = {}
    for f in os.listdir(path):
        tempFile = pd.read_csv(os.path.join(path, f))
        content[f.replace('.csv', '')] = tempFile
    result = splitWeekday(os.path.join(path, '{0}.csv'.format(args.mode)), inplaceMergeSrc=content[args.mode])
    result = splitHour(os.path.join(path,'{0}.csv'.format(args.mode)), inplaceMergeSrc=result)
    result = discreteClickTime(os.path.join(path,'{0}.csv'.format(args.mode)), inplaceMergeSrc=result)
    result = pd.merge(result, discreteAge(os.path.join(path, 'user.csv')), on='userID')
    result = pd.merge(result, content['ad'], on='creativeID')
    result = pd.merge(result, content['user'], on='userID')
    result = pd.merge(result, content['position'], on='positionID')
    result = pd.merge(result, content['app_categories'], on='appID')
    result = pd.merge(result, appadIDCount(), on='appID')
    result = pd.merge(result, appCampaignIDCount(), on='appID')
    result = pd.merge(result, splitCategory(os.path.join(path, 'app_categories.csv')), on='appID')
    result = pd.merge(result, splitHometown(os.path.join(path, 'user.csv')), on='userID')
    result = pd.merge(result, splitResidence(os.path.join(path, 'user.csv')), on='userID')
    IsHometownAndResidenceProvinceSame(result)
    result = result.rename(columns={'appID': 'Ad_appID'})
    if args.mode == 'train':
        result = result.drop('conversionTime', 1)
        result.to_csv(os.path.join('.', 'joined.csv'), index=False)
    else:
        result.to_csv(os.path.join('.', 'joined_test.csv'), index=False)

if __name__ == '__main__':
    #main()
    start = time.time()
    print processInstalledApp('appCount')
    print "time cost: " + str(time.time() - start)