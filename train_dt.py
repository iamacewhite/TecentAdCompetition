from __future__ import print_function
import numpy as np
import pandas as pd
import os
import pickle
import scipy as sp
from sklearn.metrics import *
from sklearn.model_selection import *
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("mode", help="train or test")
args = parser.parse_args()

def logloss(y_pred, y_true):
    loss = log_loss(list(y_pred), list(y_true.get_label()))
    return ('validation', loss)

new_features = ['userCountPerPosition', 'userCountPerSite','appCount', 'appUserCount',' UserAppCateCount']
feature_dict = {}
new_feature_dict = {}

mode = args.mode
path = '.'
new_test_data = pd.read_csv(os.path.join(path, 'joined_test_new_field.csv'))
test_data = pd.read_csv(os.path.join(path, 'joined_test.csv'))

instances = test_data['instanceID']

new_test_data = new_test_data.drop('instanceID', 1)
new_test_data = new_test_data.drop('label', 1)
#new_test_data = new_test_data.drop('clickTime', 1)

test_data = test_data.drop('instanceID', 1)
test_data = test_data.drop('label', 1)
#test_data = test_data.drop('clickTime', 1)

new_data = pd.read_csv(os.path.join(path, 'joined_withNewFeature.csv')) 
data = pd.read_csv(os.path.join(path, 'joined.csv'))
new_target = new_data['label']
target = data['label']

data = data.drop('label', 1)
#data = data.drop('clickTime', 1)
new_data = new_data.drop('label', 1)
#new_data = new_data.drop('clickTime', 1)

new_X_train, new_X_test, new_y_train, new_y_test = train_test_split(new_data, new_target, test_size=0.2)
X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.2)

for feature in new_features:
    if feature in data:
        feature_dict[feature] = (X_train[feature], X_test[feature])
        X_train.drop(feature, 1)
        X_test.drop(feature, 1)

for feature in new_features:
    if feature in new_data:
        new_feature_dict[feature] = (new_X_train[feature], new_X_test[feature])
        new_X_train.drop(feature, 1)
        new_X_test.drop(feature, 1)



eval_set = [(X_test, y_test)]
new_eval_set = [(new_X_test, new_y_test)]

if mode == 'rf':
    #new_model = RandomForestClassifier(max_depth=100, n_estimators=3000, n_jobs = 25, verbose=2)
    #new_model.fit(new_X_train, new_y_train)
    models = []
    results = []
    es = [100, 1000, 2500, 5000]
    criterions = ["entropy"]
    max_features = ["auto", "sqrt"]
    max_depths = [10, 100, 500]
    oob_scores = [False]
    for e in es:
        for criterion in criterions:
            for max_feature in max_features:
                for max_depth in max_depths:
                    for oob_score in oob_scores:
                        print("{} {} {} {} {}".format(e, criterion, max_feature, max_depth, oob_score))
                        model = RandomForestClassifier(max_depth=max_depth, n_estimators=e, criterion=criterion, max_features=max_feature, oob_score=oob_score, n_jobs = 25, verbose=0)
                        model.fit(X_train, y_train)
                        predictions = model.predict_proba(X_test)
                        results.append(log_loss(y_test, predictions))
                        models.append(model)
                        print("loss: %f" % log_loss(y_test, predictions))
    models = models.sort(key=dict(zip(models, results)).get)
    for i, model in enumerate(models[:5]):
        pickle.dump(model, open('model_rf_{}'.format(i), 'wb'))

    
elif mode == 'ada':
    model = AdaBoostClassifier(n_estimators=1000, learning_rate=0.9)
    model.fit(X_train, y_train)
else:
    #for feature in new_feature_dict:
    #    print("training complete file with {}:".format(feature))
    #    new_X_train[feature] = new_feature_dict[feature][0] 
    #    new_X_test[feature] = new_feature_dict[feature][1] 
    #    new_model = XGBClassifier(max_depth=6, n_estimators=2000, nthread=16) 
    #    new_model.fit(new_X_train, new_y_train, eval_metric='logloss', eval_set=new_eval_set, early_stopping_rounds=2, verbose=True)
    #    new_limit = new_model.best_iteration
    #    new_X_train.drop(feature, 1)
    #    new_X_test.drop(feature, 1)

    #for feature in feature_dict:
    #    print("training incomplete file with {}:".format(feature))
    #    X_train[feature] = feature_dict[feature][0] 
    #    X_test[feature] = feature_dict[feature][1] 
    #    model = XGBClassifier(max_depth=6, n_estimators=2000, nthread=16) 
    #    model.fit(X_train, y_train, eval_metric='logloss', eval_set=eval_set, early_stopping_rounds=2, verbose=True)
    #    limit = model.best_iteration
    #    X_train.drop(feature, 1)
    #    X_test.drop(feature, 1)
    #new_model = XGBClassifier(max_depth=6, n_estimators=2000, nthread=16) 
    #new_model.fit(new_X_train, new_y_train, eval_metric='logloss', eval_set=new_eval_set, early_stopping_rounds=2, verbose=True)
    print(len(X_train))
    models = []
    results = []
    deps = [6,7,8,9,10]
    ns = [100, 500, 1000, 2000, 3000, 5000]
    eta = [0.1, 0.15, 0.2]
    reg_lambdas = [0.5, 0.75, 1]
    for dep in deps:
        for n in ns:
            for e in eta:
                for reg in reg_lambdas:
                    print("{} {} {} {}".format(dep, n, e, reg))
                    model = XGBClassifier(max_depth=dep, n_estimators=n, learning_rate=e, reg_lambda=reg, nthread=16) 
                    model.fit(X_train, y_train, eval_metric='logloss', eval_set=eval_set, early_stopping_rounds=2, verbose=False)
                    limit = model.best_iteration
                    if mode == 'xgb':
                        predictions = model.predict_proba(X_test, ntree_limit=limit+1)
                    else:
                        predictions = model.predict_proba(X_test)
                    results.append(log_loss(y_test, predictions))
                    models.append(model)
                    print("loss: %f" % log_loss(y_test, predictions))
    models = models.sort(key=dict(zip(models, results)).get)
    for i, model in enumerate(models[:5]):
        pickle.dump(model, open('model_{}'.format(i), 'wb'))
#if mode == 'xgb':
#    new_result = new_model.predict_proba(new_test_data, ntree_limit=new_limit+1)
    #result = model.predict_proba(test_data, ntree_limit=limit+1)
#else:
#    new_result = new_model.predict_proba(new_test_data, ntree_limit=new_limit+1)
#    result = model.predict_proba(test_data)

#with open('submission{}'.format(mode), 'w+') as f:
#    for row in new_result:
#        f.write(str(row[1])+'\n')

    #for row in result:
    #    f.write(str(row[1])+'\n')
