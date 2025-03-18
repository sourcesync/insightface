#
# imports
#
# system imports
import os
import sys
import pickle
# installed packages
import numpy as np
import pandas as pd

#
# config
#
# embeddings pkl file
INPUT="/home/public/face-gen/embeddings_sabrina.pkl"
# resulting npy file
OUTPUT="/home/public/face-gen/embeddings_sabrina.npy"


if __name__ == "__main__":

    if os.path.exists(OUTPUT):
        print("WARNING: Found file", OUTPUT)
        arr = np.load(OUTPUT)
        print("WARNING: Is numpy array", arr.shape, arr.dtype, arr.size)
        raise Exception("ERROR: This path already exists", OUTPUT)


    if not os.path.exists(INPUT):
        raise Exception("ERROR: This path does not exists", INPUT)

    # Unpickle    
    print("Loading", INPUT)
    f = open(INPUT,"rb")
    obj = pickle.load(f)
    f.close()
    print("Object is of type", type(obj))
    if type(obj) != type(pd.DataFrame()):
        raise Exception("Unexpected unpickled object")

    new_shape = (obj.shape[0], 512) 
    arr = np.empty( (0, 512) )
    for i in range(obj.shape[0]):
        row = obj.iloc[i]
        arr = np.append( arr, row['embedding'])
        print(i, "shape", arr.shape)

    arr = arr.reshape( (obj.shape[0], 512 ) )
    arr = arr.astype( np.float32 )
    print("final", arr.shape, arr.dtype, "export file to", OUTPUT)
    np.save(OUTPUT, arr)
    print("saved", OUTPUT)
    
