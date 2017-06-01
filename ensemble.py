import pandas as pd

with open('ffm.txt') as f:
    content = f.readlines()

samples = []
for i in xrange(20):
    sample = data.sample(frac=0.5, replace=True)
    sample.to_csv()
