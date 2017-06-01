import pandas as pd
import numpy as np
import pickle

instances = pickle.load(open('instances.p', 'rb'))
with open('submission') as f:
    predictions = [item.strip() for item in f.readlines()]
result = pd.DataFrame(dict(instanceID = instances, prob = predictions))
result = result.sort_values(by=['instanceID'])
result.to_csv('submission.csv', index=False)
