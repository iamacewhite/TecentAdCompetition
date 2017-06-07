import pandas as pd
import numpy as np
import os
from sklearn.model_selection import *
with open('ffm_incomplete_train.txt') as f:
    content = f.readlines()

for i in xrange(3):
    sample, validate, y_train, y_validate = train_test_split(content, np.zeros(len(content)), test_size=0.2)
    #sample = np.random.choice(content, int(0.8*len(content)))
    #validate = np.random.choice(content, int(0.2*len(content)))

    with open('samples/sample{}.txt'.format(i), 'w+') as f:
        for item in sample:
            f.write(item)
    with open('samples/sample_validate{}.txt'.format(i), 'w+') as f:
        for item in validate:
            f.write(item)

os.system('../libffm/ffm-train -t 10 -k 4 -s 7 -r 0.2 --auto-stop -p samples/sample_validate{}.txt samples/sample{}.txt models/model{}'.format(0,0,0))    
os.system('../libffm/ffm-train -t 14 -k 4 -s 7 -r 0.1 --auto-stop -p samples/sample_validate{}.txt samples/sample{}.txt models/model{}'.format(1,1,1))    
os.system('../libffm/ffm-train -t 19 -k 4 -s 7 -r 0.05 --auto-stop -p samples/sample_validate{}.txt samples/sample{}.txt models/model{}'.format(2,2,2))    
