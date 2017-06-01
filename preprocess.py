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
    result = result.rename(columns={'appID': 'Ad_appID'})
    #result = pd.merge(result, content['user_app_actions'], on='userID')
    #result = result.rename(columns={'appID': 'Action_appID'})
    #result = result.drop('conversionTime', 1)
    #result.query('clickTime < 300000')
    #print result
    result.to_csv(os.path.join(path, 'joined_test.csv'), index=False)

if __name__ == '__main__':
    #main()
    appCampaignIDCount()
