from __future__ import print_function
import pandas as pd
import numpy as np
import pickle
import os
import scipy as sp
from sklearn.metrics import *

pickle = False
def logloss(act, pred):
  epsilon = 1e-2
  pred = sp.maximum(epsilon, pred)
  pred = sp.minimum(1-epsilon, pred)
  ll = sum(act*sp.log10(pred) + sp.subtract(1,act)*sp.log10(sp.subtract(1,pred)))
  ll = ll * -1.0/len(act)
  return ll

path = '.'
if pickle:
    predictions = pickle.load(open('predictions.p', 'rb'))
else:
    with open('output') as f:
        predictions = map(float, [item.strip() for item in f.readlines()])
#data = pd.read_csv(os.path.join(path, 'joined.csv'))
with open('ffm_validate.txt') as f:
    data = [item.split()[0] for item in f.readlines()]
    target = map(int, data)
#target = data['label'][3000000:]

predictions = np.asarray(predictions)
target = np.asarray(target)
#target = target.as_matrix()
print(log_loss(target, predictions))
print(logloss(target,predictions))
print(np.average(np.logical_or((target>=0.5)==(predictions>=0.5),(target<0.5)==(predictions<0.5))))
#print(type(target))
#print(type(predictions))

#instances = pickle.load(open('instances.p', 'rb'))
#
#result = pd.DataFrame(dict(instanceID = instances, prob = predictions))
#result = result.sort_values(by=['instanceID'])
#result.to_csv('submission.csv', index=False)
