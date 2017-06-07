import pandas as pd
import numpy as np
import csv, os
import argparse
import json
import time

parser = argparse.ArgumentParser()
parser.add_argument("mode", help="train or test")
args = parser.parse_args()

path = 'pre'

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

def CountUserPerApp():
    result = None
    installed = pd.read_csv(open(path+ '/user_installedapps.csv','r'))
    result = installed.groupby("appID")["appID"].count().reset_index(name="appUserCount")
    return result

def numberOfAppPerCategory():
    result = None
    count =pd.read_csv(open(path+'/app_categories.csv', 'r'))
    result = count.groupby('appCategory')['appCategory'].count().reset_index(name="NumberOfAppPerCategory")
    return result

def clickAppCategoryCount():
    return pd.read_csv(open('userAppCategoryCount.csv', 'r'))

def uniqueUserPerPosition(train):
    '''positionIDs = train['positionID']
    ids = pd.Series.unique(positionIDs)
    adFile = open(os.path.join(path, 'train.csv'), 'r')
    adDict = csv.DictReader(adFile)
    idCount = {}
    for id in ids:
        idCount[id] = set()
    for row in adDict:
        idCount[int(row['positionID'])].add(row['userID'])
    count = []
    for id in ids:
        count.append(len(idCount[id]))
    adFile.close()
    result = pd.DataFrame({'positionID': ids, 'userCountPerPosition': count})
    result.to_csv('uniqueUserPerPosition.csv')
    return result'''
    result = train.groupby('positionID')['userID'].unique().reset_index(name='userCount')
    result['userCountPerPosition'] = result['userCount'].map(len)
    result = result.drop('userCount', 1)
    return result

def uniqueUserPerPositionHelper(train):
    positionIDs = train['positionID']
    ids = pd.Series.unique(positionIDs)
    adFile = open(os.path.join(path, 'train.csv'), 'r')
    adDict = csv.DictReader(adFile)
    idCount = {}
    for id in ids:
        idCount[id] = set()
    for row in adDict:
        idCount[int(row['positionID'])].add(row['userID'])
    adFile.close()
    return idCount



def uniqueUserPerSite(train, position):
    '''
    adFile = open(os.path.join(path, 'position.csv'), 'r')
    adDict = csv.DictReader(adFile)
    ids = pd.Series.unique(position['sitesetID'])
    idCount = {}
    for id in ids:
        idCount[id] = set()
    for row in adDict:
        idCount[int(row['sitesetID'])].add(row['positionID'])
    positionUser = uniqueUserPerPositionHelper(train)
    for item in idCount: 
        idCount[item] = sum([len(positionUser[pos]) for pos in idCount[item] if pos in positionUser])
    count = []
    for id in ids:
        count.append(idCount[id])
    adFile.close()
    result = pd.DataFrame({'sitesetID': ids, 'userCountPerSiteset': count})
    result.to_csv('uniqueUserPerSite.csv')
    return result'''
    result = train.groupby('sitesetID')['userID'].unique().reset_index(name='userCount')
    result['userCountPerSite'] = result['userCount'].map(len)
    result = result.drop('userCount', 1)
    return result

def creativeIDUserCount(joined_data):
    return joined_data.groupby('creativeID')['userID'].count().reset_index(name='creativeIDUserCount')
def conversionRateAndClickCount(joined_data):
    avgRate = 93262 / 2855841.0
    Rate = (joined_data.groupby('creativeID')['label'].sum()/ joined_data.groupby('creativeID')['label'].count() * 100).reset_index(name="conversionRate")
    clickCount = joined_data.groupby('creativeID')['label'].count().reset_index(name = "clickCount")
    result = pd.merge(Rate, clickCount, on="creativeID")
    result.loc[result.clickCount < 3, 'conversionRate'] = avgRate
    return result
def uniquePositionPerSite(train, position):
    '''
    adFile = open(os.path.join(path, 'position.csv'), 'r')
    adDict = csv.DictReader(adFile)
    ids = pd.Series.unique(position['sitesetID'])
    idCount = {}
    for id in ids:
        idCount[id] = set()
    for row in adDict:
        idCount[int(row['sitesetID'])].add(row['positionID'])
    positionUser = uniqueUserPerPositionHelper(train)
    for item in idCount: 
        idCount[item] = sum([len(positionUser[pos]) for pos in idCount[item] if pos in positionUser])
    count = []
    for id in ids:
        count.append(idCount[id])
    adFile.close()
    result = pd.DataFrame({'sitesetID': ids, 'userCountPerSiteset': count})
    result.to_csv('uniqueUserPerSite.csv')
    return result'''
    result = train.groupby('sitesetID')['positionID'].unique().reset_index(name='posCount')
    result['positionCountPerSite'] = result['posCount'].map(len)
    result = result.drop('posCount', 1)
    return result

def numerical2Categorical(column):
    #describe = column.describe()
    #return pd.cut(column, [0, describe['25%'], describe['50%'], describe['75%'], describe['max']], labels = ['a', 'b', 'c', 'd'])
    describe = column.describe()
    Bin = sorted(list(set([0.0, describe['25%'], describe['50%'], describe['75%'], describe['max']])))
    labels = [str(i) for i in range(len(Bin) - 1)]
    return pd.cut(column, Bin, labels = labels)

def main():
    content = {}
    for f in os.listdir(path):
        tempFile = pd.read_csv(os.path.join(path, f))
        content[f.replace('.csv', '')] = tempFile
    appCount = pd.read_csv(open('appCount.csv', 'r'))
    appCategoryCount = pd.read_csv(open('appCategoryCount.csv', 'r'))
    CountUserPerAppData = CountUserPerApp()
    clickAppCategoryCountData = clickAppCategoryCount()
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
    #print len(result)
    result = pd.merge(result, numberOfAppPerCategory(), on="appCategory")
    print len(result)
    result = pd.merge(result, uniqueUserPerPosition(result), on="positionID")
    print len(result)
    result = pd.merge(result, uniqueUserPerSite(result, content['position']), on="sitesetID")
    result = pd.merge(result, uniquePositionPerSite(result, content['position']), on="sitesetID")
    print len(result)
    result = pd.merge(result, creativeIDUserCount(result), on='creativeID')
    #result.drop('age', 1)
    result.drop('clickTime', 1)
    result = pd.merge(result, conversionRateAndClickCount(result), on='creativeID')
    IsHometownAndResidenceProvinceSame(result)
    #for feature in ["appAdIdCount", "appCampaignIdCount", "userCountPerPosition", "userCountPerSite"]:
    #for feature in ["userCountPerPosition", "userCountPerSite"]:
    #    print(feature)
    #    result[feature] = numerical2Categorical(result[feature])
    resultWithNewField = pd.merge(result, appCount, on='userID')
    #resultWithNewField = pd.merge(resultWithNewField, appCategoryCount, on='userID')
    resultWithNewField = pd.merge(resultWithNewField, CountUserPerAppData, on='appID')
    resultWithNewField = pd.merge(resultWithNewField, clickAppCategoryCountData, on=['userID', 'appCategory'])
    if args.mode == 'train':
        #result = result[(result['clickTime'] < 310000) | (pd.notnull(result['conversionTime']))]
        result = result[(result['clickTime'] < 300000)]
        result = result.drop('conversionTime', 1)
        result = result.drop('clickTime', 1)
        resultWithNewField = resultWithNewField.drop('conversionTime', 1)
        result = result.rename(columns={'appID': 'Ad_appID'})
        resultWithNewField = resultWithNewField.rename(columns={'appID': 'Ad_appID'})
        result.to_csv(os.path.join('.', 'joined.csv'), index=False)
        resultWithNewField.to_csv(os.path.join('.', 'joined_withNewFeature.csv'), index=False)
    else:
        result.to_csv('joined_test.csv', index=False)
        leftJoined = pd.merge(result, appCount, on='userID', how='left')
        #leftJoined = pd.merge(leftJoined, appCategoryCount, on='userID', how='left')
        leftJoined = pd.merge(leftJoined, CountUserPerAppData, on='appID', how='left')
        leftJoined = pd.merge(leftJoined, clickAppCategoryCountData, on=['userID', 'appCategory'], how='left')
        leftJoined = leftJoined.rename(columns={'appID': 'Ad_appID'})
        resultWithOutNewField = leftJoined[(pd.isnull(leftJoined['appCount'])) | (pd.isnull(leftJoined['appUserCount'])) |(pd.isnull(leftJoined['UserAppCateCount']))]

        resultWithOutNewField = resultWithOutNewField.rename(columns={'appID': 'Ad_appID'})
        resultWithNewField = resultWithNewField.rename(columns={'appID': 'Ad_appID'})
        resultWithNewField.to_csv(os.path.join('.', 'joined_test_new_field.csv'), index=False)
        resultWithOutNewField = resultWithOutNewField.drop('appCount', 1)
        resultWithOutNewField = resultWithOutNewField.drop('appUserCount', 1)
        resultWithOutNewField = resultWithOutNewField.drop('UserAppCateCount', 1)
        resultWithOutNewField.to_csv(os.path.join('.', 'joined_test_without_new_field.csv'), index=False)

if __name__ == '__main__':
    start = time.time()
    main()
    print "time cost: " + str(time.time() - start)
