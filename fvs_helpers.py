import swagger_client
from swagger_client.models import *
from datetime import datetime
import time
import sys
import traceback

# constants and globals

# swagger version flag
VERSION = "v1.0"

# verbosity level
VERBOSE = False

def vprint(*msg):
    '''Only print the messsage if VERBOSE global is true.'''
    global VERBOSE
    if VERBOSE: print("%s:" % sys.argv[0], *msg)

def create_allocation(num_boards, name, verbose=False):
    allocation_id = None
    try:
        print("%s: Creating allocation" % sys.argv[0], num_boards, name)
        api_config = configure()
        gsi_boards_apis = swagger_client.BoardsApi(api_config)
        api_config.default_headers["allocationToken"] = "fvs-automation"
        ret = gsi_boards_apis.controllers_boards_controller_create_context(
            ContextRequest(boards_list=list(range(num_boards)), allocation_id=name))
        print("%s: Ret=" % sys.argv[0], ret)
        #api_config.default_headers["allocationToken"] = "fvs-automation"
        got_allocation_id = api_config.default_headers["allocationToken"]
        print("%s: Got allocation_id" % sys.argv[0], got_allocation_id)
        allocation_id = got_allocation_id
        return allocation_id
    except Exception as e:
        print(traceback.print_exc())
        raise Exception("Cannot create proper allocation")
#        msg = str(e)
#        if msg.find("already exist")>=0:
#            print("%s: No need to allocate since id already exists" % sys.argv[0])
#            allocation_id="fvs-automation"
#            return allocation_id
#        else:
#            return False

def get_fvs_version(host="localhost", port=7760, alloc="fvs-automation"):
    '''Get FVS api version from server'''

    #o = swagger_client.GetAllocationsListResponse()
    #print(o, dir(o), o.allocations_list)
    utils = swagger_client.UtilitiesApi()
    ret = utils.controllers_utilities_controller_alive()
    return ret.version

def configure(host="localhost", port=7760, alloc="fvs-automation"):
    config = swagger_client.Configuration()
    config.verify_ssl = False
    config.host = f"http://{host}:{port}/{VERSION}"
    api_config = swagger_client.ApiClient(config)
    api_config.default_headers["allocationToken"] = alloc

    return api_config

def dataset_list(api_config, verbose=False):
    datasets_apis = swagger_client.DatasetsApi(api_config)
    utilities_apis = swagger_client.UtilitiesApi(api_config)
    alloc = api_config.default_headers["allocationToken"]
    vprint("getting dataset list with alloc:", alloc)
    dataset_list = datasets_apis.controllers_dataset_controller_get_datasets_list(api_config.default_headers["allocationToken"])
    vprint('total count:', len(dataset_list.datasets_list))
    vprint("dataset list:", dataset_list.datasets_list)
    return dataset_list.datasets_list

def cleanup(api_config, verbose=False):
    datasets_apis = swagger_client.DatasetsApi(api_config)
    utilities_apis = swagger_client.UtilitiesApi(api_config)
    alloc = api_config.default_headers["allocationToken"]
    vprint("getting dataset list with alloc:", alloc)
    dataset_list = datasets_apis.controllers_dataset_controller_get_datasets_list(api_config.default_headers["allocationToken"])
    vprint('Cleaning up FVS, total count:', len(dataset_list.datasets_list))
    for dataset_id in dataset_list.datasets_list:
        status = datasets_apis.controllers_dataset_controller_get_dataset_status(
            dataset_id=dataset_id['id'], allocation_token=api_config.default_headers["allocationToken"]
        ).dataset_status
        if status == "loaded":
            datasets_apis.controllers_dataset_controller_unload_dataset(
                UnloadDatasetRequest(allocation_id=api_config.default_headers["allocationToken"], dataset_id=dataset_id['id']),
                api_config.default_headers["allocationToken"]
            )
        datasets_apis.controllers_dataset_controller_remove_dataset(
            dataset_id=dataset_id['id'], allocation_token=api_config.default_headers["allocationToken"]
        )
        vprint('removed dataset:', dataset_id['id'])
    vprint("clearing cache...")
    utilities_apis.controllers_utilities_controller_clear_cache(alloc)
    vprint('Done cleaning')

def upload(api_config, path, dataset_name, nbits=768, searchType="clusters", top=10,
           centroids_hamming_k=None, hamming_k=None, centroids_rerank=None,
           num_of_boards=None, num_of_clusters=None, verbose=False, update_verbose=10):
    
    datasets_apis = swagger_client.DatasetsApi(api_config)
    alloc = api_config.default_headers["allocationToken"]

    # import dataset
    vprint("sending import data request")
    import_request = ImportDatasetRequest(records=path, search_type=searchType, train_ind=True,
                             nbits=nbits, dataset_name=dataset_name,
                             num_of_boards=num_of_boards, num_of_clusters=num_of_clusters)
    vprint(import_request)
    response = datasets_apis.controllers_dataset_controller_import_dataset(import_request,alloc)
    # TODO: look for error in response
 
    # get the dataset id generated by FVS 
    dataset_id = response.dataset_id
    vprint(f"got dataset_id: {dataset_id}")
    
    # train status
    train_status = datasets_apis.controllers_dataset_controller_get_dataset_status(
        dataset_id=dataset_id, allocation_token=alloc
    ).dataset_status

    # loop until training is done # TODO: implement a max retries or timeout
    vprint("training, status currently:", train_status)
    counter=0
    while train_status != "completed":
        train_status = datasets_apis.controllers_dataset_controller_get_dataset_status(
            dataset_id=dataset_id, allocation_token=alloc
        ).dataset_status
        if train_status == "error":
            raise SystemError("fvs training failed")
        time.sleep(1) # it means we have 1 second resolution for wall-time benchmarks surrounding the training
        if update_verbose and (counter % update_verbose == 0):
            print("%s: %s: Checking for training conpleted status.  Please wait..." % ( sys.argv[0], str(datetime.now())) )
        counter += 1

    # load the dataset
    vprint('done training, loading dataset...')
    load_status = datasets_apis.controllers_dataset_controller_load_dataset(
        LoadDatasetRequest(allocation_id=alloc, dataset_id=dataset_id, topk=top,
                           centroids_hamming_k=centroids_hamming_k, centroids_rerank=centroids_rerank,
                           hamming_k=hamming_k), alloc).status
    # TODO: check any error status
    vprint('load status:', load_status)

    # focus dataset
    vprint("focusing dataset...")
    datasets_apis.controllers_dataset_controller_focus_dataset(
        FocusDatasetRequest(alloc, dataset_id), alloc
    )
    # TODO: check any focus err status

    vprint("done with upload")
    return dataset_id
    
def search(api_config, qpath, dataset_id, top, verbose=False):
    search_apis = swagger_client.SearchApi(api_config)
    alloc = api_config.default_headers["allocationToken"]

    vprint("starting search")
    response = search_apis.controllers_search_controller_search(
        SearchRequest(allocation_id=alloc, dataset_id=dataset_id, queries_file_path=qpath, topk=top),
        alloc)
    vprint("done searching")

    return response


if __name__ == "__main__":

    print("%s: unit tests..." % sys.argv[0])
    print()
    print("%s: testing 'create_allocation' with 4 boards" % sys.argv[0])
    create_allocation(4, "fvs-4" )
    print() 
    print("%s: testing 'create_allocation' with 4 boards" % sys.argv[0])
    create_allocation(3, "fvs-3" )

    print("%s: Done." % sys.argv[0])

