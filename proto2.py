# 
# imports
#
# system imports
import os
import glob
import pandas as pd
import sys
import pickle
# installed packages
import insightface
from insightface.app import FaceAnalysis
import kagglehub
import cv2
import numpy
import numpy as np
import tqdm
from numpy.linalg import norm

pd.set_option('display.max_columns', None)

f = open("data/match_stats.pkl","rb")
obj = pickle.load(f)
f.flush()
f.close()

print(obj)
