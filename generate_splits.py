from sklearn.model_selection import *
import numpy as np
with open("ffm.txt") as f:
    content = f.readlines()

X_train, X_validate, y_train, y_validate = train_test_split(content, np.zeros(len(content)), test_size=0.2)

with open('ffm_train.txt', 'w') as f1:
    for line in X_train:
        f1.write(line)

with open('ffm_validate.txt', 'w') as f2:
    for line in X_validate:
        f2.write(line)


