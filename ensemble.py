import pandas as pd
import numpy as np
import os
with open('ffm.txt') as f:
    content = f.readlines()

for i in xrange(10):
    sample = np.random.choice(content, int(0.2*len(content)))
    with open('samples/sample{}.txt'.format(i), 'w+') as f:
        for item in sample:
            f.write(item)
    os.system('../libffm/ffm-train -l 0.000002 -t 12 -k 4 -s 1 --auto-stop -p ffm_validate.txt samples/sample{}.txt models/model{}'.format(i,i))    
