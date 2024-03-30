import os
import numpy as np

path = "./weiboData_10000/1900232583/data"
data = os.listdir(path)
print(len(data))

# data = np.load("./weiboData_10000/1900232583/ba")