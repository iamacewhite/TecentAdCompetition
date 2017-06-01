import os
import pandas as pd
import numpy as np
import csv

path = './pre'

def appadIDCount():
    adFile = open('pre/ad.csv', 'r')
    adData = pd.read_csv(adFile)
    ids = pd.Series.unique(adData['appID'])
    adFile.close()
    adFile = open('pre/ad.csv', 'r')
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
    adFile = open('pre/ad.csv', 'r')
    adData = pd.read_csv(adFile)
    ids = pd.Series.unique(adData['appID'])
    adFile.close()
    adFile = open('pre/ad.csv', 'r')
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
            if not startIndex:
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

def main():
    content = {}
    for f in os.listdir(path):
        tempFile = pd.read_csv(os.path.join(path, f))
        content[f.replace('.csv', '')] = tempFile
    mode = 'test'
    result = splitWeekday('pre/{0}.csv'.format(mode),inplaceMergeSrc=content[mode])
    result = splitHour('pre/{0}.csv'.format(mode),inplaceMergeSrc=result)
    result = pd.merge(result, content['ad'], on='creativeID')
    result = pd.merge(result, content['user'], on='userID')
    result = pd.merge(result, content['position'], on='positionID')
    result = pd.merge(result, content['app_categories'], on='appID')
    result = pd.merge(result, appadIDCount(), on='appID')
    result = pd.merge(result, appCampaignIDCount(), on='appID')
    result = pd.merge(result, splitCategory('pre/app_categories.csv'), on='appID')
    result = pd.merge(result, splitHometown('pre/user.csv'), on='userID')
    result = pd.merge(result, splitResidence('pre/user.csv'), on='userID')
    result = result.rename(columns={'appID': 'Ad_appID'})
    #result = pd.merge(result, content['user_app_actions'], on='userID')
    #result = result.rename(columns={'appID': 'Action_appID'})
    #result = result.drop('conversionTime', 1)
    #result.query('clickTime < 300000')
    #print result
    result.to_csv(os.path.join(path, 'joined_test.csv'), index=False)

if __name__ == '__main__':
    main()
    #csvdata = pd.read_csv('pre/test.csv')
    #print(splitHour('pre/test.csv',inplaceMergeSrc=csvdata))
