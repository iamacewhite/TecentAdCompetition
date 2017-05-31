from __future__ import print_function
import numpy as np
import pandas as pd
import os

import pywFM
import pickle
import scipy as sp

def logloss(act, pred):
  epsilon = 1e-2
  pred = sp.maximum(epsilon, pred)
  pred = sp.minimum(1-epsilon, pred)
  ll = sum(act*sp.log10(pred) + sp.subtract(1,act)*sp.log10(sp.subtract(1,pred)))
  ll = ll * -1.0/len(act)
  return ll

path = '.'
#test_data = pd.read_csv(os.path.join(path, 'joined_test.csv'))
#instances = test_data['instanceID']
#test_data = test_data.drop('instanceID', 1)
#test_data = test_data.drop('label', 1)
#test_data = test_data.drop('clickTime', 1)
data = pd.read_csv(os.path.join(path, 'joined.csv'))
fm = pywFM.FM(task='classification', num_iter=30, k2=2, verbose=True)
target = data['label']
data = data.drop('label', 1)
data = data.drop('clickTime', 1)
# split features and target for train/test
# first 5 are train, last 2 are test
model = fm.run(data[:3000000], target[:3000000], data[3000000:], target[3000000:])
#print(model.predictions)
# you can also get the model weights
#print(model.weights)
print("loss: %f" % logloss(target[3000000:],model.predictions))
pickle.dump(model.predictions, open( "predictions.p", "wb" ))

#pickle.dump(instances, open( "instances.p", "wb" ))


