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
from fvs_helpers import *

#
# config
#
# embeddings pkl file
PKL = "/home/public/face-gen/embeddings_sabrina.pkl"
# embeddings npy file
NPY="/home/public/face-gen/embeddings_sabrina.npy"
# FVS index configs
FVS_CONFIGS = \
{
  "flat": {
    "nbits": 768,
    "search_type": "flat",
    "topk": 10
  }
}
#{ "low_latency": {
#    "nbits": 768,
#    "search_type": "clusters", 
#    "topk": 10,
#    "centroids_hamming_k": 200,
#    "hamming_k": 250,
#    "centroids_rerank": 100
#}

if __name__ == "__main__":

    # Unpickle embedding pkl  
    print("%s: Loading" % sys.argv[0], PKL)
    f = open(PKL,"rb")
    obj = pickle.load(f)
    f.close()
    print("%s: Object is of type" % sys.argv[0], type(obj))
    if type(obj) != type(pd.DataFrame()):
        raise Exception("Unexpected unpickled object")
    #print(obj)

    # load embeddings npy
    arr = np.load(NPY)
    arr = arr.astype( np.float32 )
    print("%s: Embeddings npy" % sys.argv[0], arr.shape, arr.dtype, arr[0])

    # initialize FVS api object        
    api_config = configure() #leaving empty for default params

    # get datasets list
    dsets = dataset_list(api_config, verbose=True)
    print("%s: Datasets=" % sys.argv[0], len(dsets), dsets)

    # create all indexes
    for cfg in FVS_CONFIGS.keys():
        config = FVS_CONFIGS[cfg]
        print("%s: Building FVS index with config=" % sys.argv[0], cfg, cfg, config)
        print("%s: Starting upload" % sys.argv[0])
        dataset_id = upload(
            api_config, 
            NPY, cfg,
            nbits=config["nbits"], searchType=config["search_type"], top=config["topk"],
            num_of_boards=1, verbose=True
        )
#        dataset_id = upload(
#            api_config, 
#            NPY, cfg,
#            nbits=config["nbits"], searchType=config["search_type"], top=config["topk"],
#            centroids_hamming_k=config["centroids_hamming_k"], hamming_k=config["hamming_k"], 
#            centroids_rerank=config["centroids_rerank"],
#            num_of_boards=1, verbose=True
#        )
        print("%s: Got Dataset_id=" % sys.argv[0], dataset_id)

        # do a sanity check search
        search_query_path = os.path.join( os.path.dirname( NPY ), "query_embedding.npy" )
        arr = np.load(NPY)
        print("%s: Saving array to file" % sys.argv[0], arr[0].shape, arr[0].dtype, search_query_path)
        np.save( search_query_path, arr[0].reshape(1,512) )
        response = search(api_config, search_query_path, dataset_id, config["topk"], verbose=VERBOSE)
        print(response)

    
    # get datasets list
    dsets = dataset_list(api_config, verbose=True)
    print("%s: Datasets=" % sys.argv[0], len(dsets), dsets)

    del api_config

