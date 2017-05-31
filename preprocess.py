import os
import pandas as pd
import numpy as np

path = '/media/ace/Data/Ace/datasets/tecent/pre'

def main():
    content = {}
    for f in os.listdir(path):
        tempFile = pd.read_csv(os.path.join(path, f))
        content[f.replace('.csv', '')] = tempFile
    result = pd.merge(content['test'], content['ad'], on='creativeID')
    result = pd.merge(result, content['user'], on='userID')
    result = pd.merge(result, content['position'], on='positionID')
    result = pd.merge(result, content['app_categories'], on='appID')
    result = result.rename(columns={'appID': 'Ad_appID'})
    #result = pd.merge(result, content['user_app_actions'], on='userID')
    #result = result.rename(columns={'appID': 'Action_appID'})
    #result = result.drop('conversionTime', 1)
    #result.query('clickTime < 300000')
    #print result
    result.to_csv(os.path.join(path, 'joined_test.csv'), index=False)




if __name__ == '__main__':
    main()
