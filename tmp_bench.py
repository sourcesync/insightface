from fvs_helpers import *
from apubench import leda, host

import sys
import argparse
import os
import json, datetime
import numpy as np
import platform
import pandas as pd
import traceback

# constants and globals

# search phase length (seconds)
SEARCH_TOTAL = 100

# global verbosity level
VERBOSE = False

def vprint(*msg):
    '''print message behind a VERBOSE check guard'''
    global VERBOSE
    if VERBOSE: print("%s:" % sys.argv[0], *msg)
    
datadir = "/home/public/fvs_benchmark_datasets"

#
# parse arguments
#
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-d", "--dataset", default="deep-1M")
parser.add_argument("-q", "--query-path", default="deep-queries-")
parser.add_argument("-n", "--nbits", type=int, default=768)
parser.add_argument("-s", "--search-type", default="clusters")
parser.add_argument("-c", "--centroids-hamming-k", type=int)
parser.add_argument("-h", "--hamming-k", type=int)
parser.add_argument("-r", "--centroids-rerank", type=int)
parser.add_argument("-b", "--num-of-boards", type=int)
parser.add_argument("-k", "--topk", type=int, default=10)
parser.add_argument("-v", "--verbose", default=False, action="store_true")
parser.add_argument("-e", "--output", required=False)
parser.add_argument("-a", "--batch-size", required=False)
parser.add_argument("-z", "--dont_cleanup_data", required=False, action="store_true")
args = parser.parse_args()

#
# process arguments
#
VERBOSE = args.verbose

#
# validate dataset
#
data_path = f"{datadir}/{args.dataset}.npy"
print("%s: Validating dataset file..." % sys.argv[0])
if not os.path.exists(data_path): raise Exception("%s: ERROR: Could not validate dataset file %s" % (sys.argv[0],data_path))

#
# validate query/batch files
#
print("%s: Validating query file path(s)..." % sys.argv[0])
if args.batch_size.find(":")>0:
    # batch size is first, and then dataset is second
    parts = args.batch_size.split(":")
    batch_size = int(parts[0])
    q_modulo = int(parts[1])
    # validate all the modulo files exist
    for i in range(q_modulo):
        q_path = os.path.join( datadir, args.query_path + "%d-%d.npy" % (q_modulo, i+1) )
        if not os.path.exists(q_path): raise Exception("Cannot find query path for modulo search, %s" % q_path)
else:
    # batch size inferred from the query path
    batch_size = int(args.batch_size)
    query_path = os.path.join( datadir, args.query_path + "%d.npy" % batch_size )
    if not os.path.exists(query_path): raise Exception("Cannot find %s" % query_path) 
    q_modulo = -1
print("%s: Validated batch size=%d and file prefix=%s w/modulo=%d" % (sys.argv[0], batch_size, args.query_path, q_modulo))
 
#
# form config name
#
config_name = f"gsi-{args.dataset}-{args.nbits}-{args.search_type}-batch-{batch_size}"
if args.centroids_hamming_k:
    config_name += "-centroidsHammingK-" + str(args.centroids_hamming_k)
    config_name += "-hammingK-" + str(args.hamming_k)
    config_name += "-centroidsRerank-" + str(args.centroids_rerank)

#
# create allocation
#
if args.num_of_boards:
    print("%s: Creating allocation..." % sys.argv[0])
    ret = create_allocation(args.num_of_boards, "fvs-automation")
    if not ret:
        raise Exception("%s: Could not create allocation" % sys.argv[0])

#
# validate fvs connection and get fvs version
#
fvs_version = get_fvs_version()
print("%s: Validated connection to fvs server, version=" % sys.argv[0], fvs_version)


#
# get leda info
#
print("%s: Getting leda info from boards..." % sys.argv[0])
leda_info = leda.get_leda_info( verbose=VERBOSE, raise_exc=False )
if not leda_info: raise Exception("%s: ERROR: Could not get Leda info." % sys.argv[0])

#
# get system information (via query path arg)
#
print("%s: Getting system information..." % sys.argv[0])
# get sys info on query file path (presumably all the local files used live there but its a TODO for later)
query_file_info = host.get_file_info( os.path.dirname(args.query_path), verbose=VERBOSE, require_local_path=True)
if not query_file_info: raise Exception("%s: ERROR: Could not get host/sys info for query file" % sys.argv[0], query_path)

#
# prepare to collect data
#
results = [] # collects the reponse indices per search
timings = [] # collects the walltime per search
responses = [] # collects raw search query results

#
# FVS UPLOAD
#
print("%s: Starting FVS Upload..." % sys.argv[0])
api_config = configure() #leaving empty for default params
cleanup(api_config)
vprint(f"starting upload, {config_name}")
ts = datetime.datetime.now()
dataset_id = upload(
    api_config, data_path, config_name,
    nbits=args.nbits, searchType=args.search_type, top=args.topk,
    centroids_hamming_k=args.centroids_hamming_k, hamming_k=args.hamming_k, centroids_rerank=args.centroids_rerank,
    num_of_boards=args.num_of_boards, verbose=VERBOSE
)
del api_config

#
# FVS SEARCH
#

# do consec searches until timeout
print("%s: Starting FVS Search..." % sys.argv[0], datetime.datetime.now())
vprint("starting search")
t_start, iters  = datetime.datetime.now(), 0
api_config = configure() #leaving empty for default paramss
# pre-compute the query path (this might get overridden in 'modulo' mode in the loop below)
search_query_path = os.path.join( datadir, args.query_path + "%d.npy" % batch_size ) 
if q_modulo<0:  vprint("using search query path=", search_query_path)
while ((datetime.datetime.now() - t_start).total_seconds() < SEARCH_TOTAL):
    # lets keep the compute and file I/O to a minimum within this loop
    if q_modulo>=0:
        # the final query path final may depend on a modulo operation decided during parse args
        m = (iters % q_modulo) + 1
        search_query_path = os.path.join( datadir, args.query_path + "%d-%d.npy" % (q_modulo, m) )
        vprint("using search query path=", search_query_path)
    s_start =  datetime.datetime.now()
    response = search(api_config, search_query_path, dataset_id, args.topk, verbose=VERBOSE)
    s_end  = datetime.datetime.now()
    results.append(response)
    timings.append( (s_end-s_start).total_seconds() ) 
    iters += 1
t_end = datetime.datetime.now()
vprint("iterations completed:", iters)
vprint("done searching")
counter = 0

vprint("----------done with benchmark----------")

if not args.output: # compute accuracy now
    gt_path = f"{data_path[:-4]}-gt-{batch_size}.npy"
    if not os.path.exists(gt_path): raise Exception("Could not file path %s" % gt_path)
    gt = np.load(gt_path)
    accuracy = []
    for inds in results:
        for i in range(len(inds)):
            accuracy.append(len(np.intersect1d(inds.indices[i], gt[i][:args.topk])) / args.topk)
    vprint(f"\nACCURACY: {sum(accuracy) / len(accuracy)}\n")

if not args.output:# export the search results now
    file_data["experiment_date"] = exp_date = str(datetime.datetime.now())
    file_data["accuracy"] = sum(accuracy) / len(accuracy)
    file_data["topk"] = args.topk
    outfile.seek(0)
    json.dump(file_data, outfile)
    outfile.close()
else:
    exp_date = datetime.datetime.now()
# finalize search phase
del api_config

#
# singular JSON and CSV export
#
if args.output: # saving a unified export at the end
    result = { 
        "experiment_date": exp_date,
        "num_searches": iters,
        "search_results": results,
        "timings": timings,
        "search_start": t_start,
        "search_end": t_end, 
        "parms": {  "topk": args.topk, 
                    "nbits": args.nbits, 
                    "searchType": args.search_type,
                    "centroids_hamming_k":args.centroids_hamming_k, 
                    "hamming_k":args.hamming_k, 
                    "centroids_rerank":args.centroids_rerank,
                    "num_of_boards":args.num_of_boards
                },
        "leda": leda_info,
        "dataset": data_path,
        "query": args.query_path,
        "batch_size": batch_size,
        "q_modulo": q_modulo,
        "query_file_info": query_file_info,
        "fvs_version": fvs_version,
        "allocation_num_boards": args.num_of_boards
    }
    # form a base file name for export
    machine_name = platform.node()
    ts = str( datetime.datetime.now() ).replace(":","_").replace(" ","_")
    fpath = os.path.join( args.output, "results__%s__%s" % ( machine_name, ts ) )

    # save as JSON
    try:
        with open(fpath+".json", "w") as outfile: 
            json.dump(result, outfile)
        print("%s: Wrote results JSON to" % sys.argv[0], fpath+".json")
    except:
        print("%s: WARNING: Serialization issue export to JSON file" % sys.argv[0])

    # save as CSV
    df = pd.DataFrame([result])
    df.to_csv(fpath+".csv")
    print("%s: Wrote results CSV to" % sys.argv[0], fpath+".csv")
     
# 
# cleanup/finalize
#
api_config=configure()
if args.dont_cleanup_data:
    print("%s: WARNING: Skipping final FVS data cleanup." % sys.argv[0])
else:
    vprint("cleanup datasets")
    cleanup(api_config)
try: del api_config
except NameError as e: print("ERROR: FVS config stopped")
