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

def logloss(y_pred, y_true):
    loss = log_loss(list(y_pred), list(y_true.get_label()))
    return ('validation', loss)

mode = 'xgb'
path = '.'
test_data = pd.read_csv(os.path.join(path, 'joined_test.csv'))
instances = test_data['instanceID']
test_data = test_data.drop('instanceID', 1)
test_data = test_data.drop('label', 1)

test_data = test_data.drop('clickTime', 1)

data = pd.read_csv(os.path.join(path, 'joined.csv'))
target = data['label']
data = data.drop('label', 1)
data = data.drop('clickTime', 1)


X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.2)
X_train.dropna()
X_test.dropna()
eval_set = [(X_test, y_test)]

if mode == 'rf':
    model = RandomForestClassifier(n_estimators = 2000, n_jobs = -1, verbose=True)
    model.fit(X_train, y_train)
elif mode == 'ada':
    model = AdaBoostClassifier(n_estimators=1000, learning_rate=0.9)
    model.fit(X_train, y_train)
else:
    model = XGBClassifier(max_depth=6, n_estimators=2000, nthread=8)
    model.fit(X_train, y_train, eval_metric='logloss', eval_set=eval_set, early_stopping_rounds=2, verbose=True)
    limit = model.best_iteration
if mode == 'xgb':
    predictions = model.predict_proba(X_test, ntree_limit=limit+1)
else:
    predictions = model.predict_proba(X_test)

print("loss: %f" % log_loss(y_test, predictions))


if mode == 'xgb':
    result = model.predict_proba(test_data, ntree_limit=limit+1)
else:
    result = model.predict_proba(test_data)

with open('submission', 'w+') as f:
    for row in result:
        f.write(str(row))
pickle.dump(open('model_{}'.format(mode), 'wb'))
