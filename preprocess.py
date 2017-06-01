import os
import pandas as pd
import numpy as np
import csv

path = '/media/ace/Data/Ace/datasets/tecent/pre'

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

def splitFeature(filename,IDFieldName,FieidtoSpilt,NewFieldName,startIndex=None,endIndex=None,postprocessFunction=None):
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
                tmp = postprocessFunction(tmp)

            tmps.append(int(tmp))
            IDs.append(int(row[IDFieldName]))
    result = pd.DataFrame({IDFieldName:IDs,NewFieldName:tmps})
    print(result)
    return result

def splitCategory(filename):
    return splitFeature(filename,'appID','appCategory','appFirstLevelCategory',endIndex=1)    

def splitHometown(filename):
    return splitFeature(filename,'userID','hometown','hometownProvince',endIndex=-2)

def splitResidence(filename):
    return splitFeature(filename,'userID','residence','residenceProvince',endIndex=-2)    

def splitWeekday(filename):
    return splitFeature(filename,'')

def main():
    content = {}
    for f in os.listdir(path):
        tempFile = pd.read_csv(os.path.join(path, f))
        content[f.replace('.csv', '')] = tempFile
    result = pd.merge(content['test'], content['ad'], on='creativeID')
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
    #main()
    result1 = splitHometown('pre/user.csv')
    result2 = splitResidence('pre/user.csv')
    userData = pd.read_csv('pre/user.csv')
    tmp = pd.merge(result1,result2,on='userID')
    print(pd.merge(userData,tmp,on='userID'))
    '''
    result = splitCategory('pre/app_categories.csv')
    adData = pd.read_csv('pre/app_categories.csv')
    print(adData)
    print(pd.merge(adData,result, on='appID'))
    '''