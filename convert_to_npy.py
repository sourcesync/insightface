# imports
import numpy as np

# config



#
# get array info from a valid npy file
#
arr = np.load("/home/public/fvs_benchmark_datasets/deep-1M.npy")
print(type(arr), arr.dtype, arr.shape)
