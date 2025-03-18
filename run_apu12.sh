#!/bin/bash


#
# configuration
#

# uncomment next line for extra debugging
#set -x

# list of datasets to test, space separated list
DATASETS="deep-1M"

# space separated list of batch sizes to test - an entry with ':' has special meaning
#BATCH_SIZES="1:10 10 100 1000"
BATCH_SIZES="1"

# prefix name of query files
QUERY_PATH="deep-queries-"

# centroids-hamming-k
CENTROIDS_HAMMING_K=200 #FVS-LL

# hamming-k
HAMMING_K=250 #FVS-LL

# centroids-rerank
CENTROIDS_RERANK=100 #FVS-LL

# where to write data (CSV at least)
OUTPUT="./results"

# subset of boards to use
NUM_BOARDS="1"

# if set, export float32 and training manager data (set to empty string otherwise)
EXPORT_DATA_PATH="/mnt/nas2/benchmarks/fvs/0.9.5.4/exports"

# verbosity level for debugging
VERBOSE=1

#
# I don't recommend using the config vars below unless you know what you are doing.
# They are useful for troubleshooting the python script...
#

# dry run mode
SHORTCUT=0

# bypass rebooting of boards
BYPASS_REBOOT_BOARDS=1

# bypass restarting of docker (assumes you will do so manually)
BYPASS_RESTART_DOCKER=0

#
# check arguments
#
if [ ! -z "$1" ]; then
    echo "$0: ERROR: Not expecting any command line arguments"
    exit 1
fi


#
# source common bash functions 
#
if [ -f "./functions.bash" ]; then
    source "./functions.bash"
fi

#
# useful functions 
#

cleanup_local_fvs() {
    if [ "$VERBOSE" -ne "0" ]; then
        echo "$0: Removing all trained clusters"
    fi
    sudo rm -rf /home/public/elastic-similarity/python-training-manager-api/cache/* >/dev/null
    sudo rm -fr /home/public/elastic-similarity/float32_neural/fvs-automation >/dev/null
    return 0
}

reboot_boards() {
    for ((i=($1-1); i>=0; i--)); 
    do
        echo "$0: Rebooting card $i"
        ledag-ssh -o localhost -s $i reboot >/dev/null
        sleep 5
    done

    echo "$0: Waiting for cards, please wait..."
    sleep 30
    ledag-ssh -o localhost quit
#    while : ; do # TODO: implement max_retries
#        ledag-ssh -o localhost quit
#    done
    return 0
}

restart_docker_fvs() {
    if [ "$VERBOSE" -ne "0" ]; then
        echo "$0: Restarting docker fvs"
    fi

    pushd . >/dev/null # remember the current director for 'pop' later
    cd ./vector-db-benchmark/fvs_server/0.4.1-alpha15/backend/ >/dev/null && docker compose down >/dev/null 2>&1
    docker stop $(docker ps -a -q) >/dev/null 2>&1
    docker rm $(docker ps -a -q) >/dev/null 2>&1
    sudo service docker restart >/dev/null 2>&1
    if [ "$?" -ne "0" ]; then
        echo "$0: ERROR: Cannot restart the docker service."
        exit 1
    fi

    # cleanup redis key state
    sudo rm -f /home/public/elastic-similarity/fvs-redis-data/dump.rdb >/dev/null 2>&1

    # cleanup any trained clusters
    sudo rm -rf /home/public/elastic-similarity/python-training-manager-api/cache/* >/dev/null 2>&1

    # cleanup any datasets attached to fvs-automation
    sudo rm -fr /home/public/elastic-similarity/float32_neural/fvs-automation >/dev/null 2>&1

    pwd
    echo "$0: Running fvs docker compose script..." && ./run_local_george_and_jacob_daemon.sh >/dev/null
    if [ "$?" -ne "0" ]; then
        echo "$0: ERROR: Cannot restart fvs containers."
        exit 1
    fi
    popd >/dev/null # go back to directory that we 'push'ed further up
   
    # wait until float32 container is properly running... 
    echo "$0: Checking float32 container logs for proper startup.  Please wait..."
    docker logs python-float32-neural |grep "Press CTRL+C to quit" >/dev/null 2>&1
    while [ "$?" -ne "0" ]; do #TODO: implement max retries
        echo "$0: Checking float32 container logs for proper startup.  Please wait..."
        sleep 5
        docker logs python-float32-neural |grep "Press CTRL+C to quit" >/dev/null 2>&1
    done

    # wait until training manager has started properly...
    docker logs python-training-manager |grep "Press CTRL+C to quit" >/dev/null
    while [ "$?" -ne "0" ]; do
        echo "$0: Training manager not yet started.  Please wait..."
        sleep 2
        docker logs python-training-manager |grep "Press CTRL+C to quit" >/dev/null
    done

    # inject init code into training manager container...
    echo "$0: Resetting the state for the training-manager container"
    docker cp ./clear_fvs.sh python-training-manager-postgres:/clear_fvs.sh >/dev/null
    if [ "$?" -ne "0" ]; then
        echo "$0: ERROR: Cannot inject init code into training manager container"
        exit 1
    fi
    # run it
    docker exec -it python-training-manager-postgres /clear_fvs.sh >/dev/null
    if [ "$?" -ne "0" ]; then
        echo "$0: ERROR: Cannot run injected script in training manager container"
        exit 1
    fi
    return 0
}

# capture specific fvs docker logs
capture_docker_logs() {
    output_dir=$1
    if [ ! -d "$output_dir" ]; then
        echo "$0: ERROR: No output dir found $1"
        exit 1
    fi
    dset=$2
    if [ -z "$dset" ]; then
        echo "$0: ERROR: Invalid dataset passed as argument $2"
        exit 1
    fi
    nb=$3
    if [ -z "$nb" ]; then
        echo "$0: ERROR: Invalid num_boards passed as argument $3"
        exit 1
    fi
    bs=$4
    if [ -z "$bs" ]; then
        echo "$0: ERROR: Invalid batch size for argument $4"
        exit 1
    fi

    ts=$(date +%s)
    FL32_NAME="$output_dir/float32_logs__${dset}___nb_${nb}__bs_${bs}__${ts}.log"
    docker logs python-float32-neural >"$FL32_NAME"
    if [ "$?" -ne "0" ]; then
        echo "$0: WARNING: There was a problem retrieving the float32 logs"
    fi
    
    TM_NAME="$output_dir/training_manager_logs__${dset}___nb_${nb}__bs_${bs}__${ts}.log"
    docker logs python-training-manager >"$TM_NAME"
    if [ "$?" -ne "0" ]; then
        echo "$0: WARNING: There was a problem retrieving the training manager logs"
    fi

    return 0
}

# export float32, python-training-manager, and postgresql data
export_data() {
    output_dir="$1"
    echo "$0: Creating/using export data directory: $output_dir"
    mkdir -p $output_dir

    if [ ! -d "$output_dir" ]; then
        echo "$0: ERROR: No output dir found $1"
        return 1
    fi
    dset=$2 
    if [ -z "$dset" ]; then
        echo "$0: ERROR: Invalid dataset passed as argument $2"
        return 1
    fi
    nb=$3
    if [ -z "$nb" ]; then
        echo "$0: ERROR: Invalid num_boards passed as argument $3"
        return 1
    fi
    bs=$4
    if [ -z "$bs" ]; then
        echo "$0: ERROR: Invalid batch size for argument $4"
        return 1
    fi

    ts=$(date +%s)

    # check float32 src
    src="/home/public/elastic-similarity/float32_neural/fvs-automation" # TODO: should this be hard-coded?
    if [ ! -d "$src" ]; then
        echo "$0: WARNING: Export not possible because directory $src does not exist."
        return 1
    fi
    
    # create dest for float32 data
    dest="$output_dir/data__${dset}__nb_${nb}__bs_${bs}__${ts}/float32_neural"
    mkdir -p $dest >/dev/null

    # copy float32 data
    cp -r "$src" "$dest/" >/dev/null
    if [ "$?" -ne "0" ]; then
        echo "$0: WARNING: Export not possible because cp failed from $src to $dest."
        return 1
    fi
    
    # check python-training-manager src
    src="/home/public/elastic-similarity/python-training-manager-api/cache" # TODO: should this be hard-coded?
    if [ ! -d "$src" ]; then
        echo "$0: WARNING: Export not possible because directory $src does not exist."
        return 1
    fi
    
    # create dest for python-training-manager data
    dest="$output_dir/data__${dset}__nb_${nb}__bs_${bs}__${ts}/python_training_manager"
    mkdir -p $dest >/dev/null
 
    # copy python-training-manager data
    cp -r "$src" "$dest/" >/dev/null
    if [ "$?" -ne "0" ]; then
        echo "$0: WARNING: Export not possible because cp failed from $src to $dest."
        return 1
    fi
   
    # inject psql export code into postgresql container 
    echo "$0: Export psql data..."
    docker cp ./export_clusters_trains.sh python-training-manager-postgres:/export_clusters_trains.sh >/dev/null
    if [ "$?" -ne "0" ]; then
        echo "$0: WARNING: Cannot inject init code into postgres container."
        return 1
    fi
    # run it
    docker exec -it python-training-manager-postgres /export_clusters_trains.sh >/dev/null
    if [ "$?" -ne "0" ]; then
        echo "$0: WARNING: Cannot run psql export script."
        return 1
    fi
    # copy resulting csv
    dest="$output_dir/data__${dset}__nb_${nb}__bs_${bs}__${ts}"
    docker cp python-training-manager-postgres:/tmp/clusters_trains.csv "$dest/" >/dev/null
    if [ "$?" -ne "0" ]; then
        echo "$0: WARNING: Cannot copy export CSV from postgres container."
        return 1
    fi
 
    return 0
} 

# activate the right conda env manually because of sudo requirement (TODO)
export PATH=/home/gwilliams/anaconda3/envs/fvs-benchmarking-2/bin:/home/gwilliams/anaconda3/condabin:$PATH
source /home/gwilliams/anaconda3/etc/profile.d/conda.sh
conda activate fvs-benchmarking-2

#
# ensure python environment is correct by checking availability of (some) packages
#
check_python_env pandas

#
# Run the benchmarks
#

# form the --verbose flag as needed
VFLAG=""
if [ "$VERBOSE" -ne "0" ]; then 
    VFLAG="--verbose"
fi

# form the --shortcut flag as needed
SCFLAG=""
if [ "$SHORTCUT" -eq "1" ]; then 
    SCFLAG="--shortcut"
fi

# form the --output flag as needed
OFLAG=""
if [ ! -z "$OUTPUT" ]; then 
    OFLAG="--output $OUTPUT"
fi

# form the --dont_cleanup_data flag as needed
DCDFLAG=""
if [ ! -z "$EXPORT_DATA_PATH" ]; then 
    DCDFLAG="--dont_cleanup_data"
fi

# form the --centroids-hamming-k flag as needed
CHK_FLAG=""
if [ ! -z "$CENTROIDS_HAMMING_K" ]; then
    CHK_FLAG="--centroids-hamming-k $CENTROIDS_HAMMING_K"
fi

# form the --hamming-k flag as needed
HK_FLAG=""
if [ ! -z "$HAMMING_K" ]; then
    HK_FLAG="--hamming-k $HAMMING_K"
fi

# form the --centroids-rerank flag as needed
CR_FLAG=""
if [ ! -z "$CENTROIDS_RERANK" ]; then
    CR_FLAG="--centroids-rerank $CENTROIDS_RERANK"
fi

# iterate over datasets and query batch_sizes
for DATASET in ${DATASETS}
    do
        for BATCH_SIZE in ${BATCH_SIZES}
            do

                # reboot attached boards (unless bypass flag set)
                if [ "$BYPASS_REBOOT_BOARDS" -ne "1" ]; then
                    vecho $0 "Rebooting $NUM_BOARDS APU boards.."
                    reboot_boards 4 #TODO: we should probably just reset all boards in the system
                fi

                # reset docker fvs (if not bypassed)
                if [ "$BYPASS_RESTART_DOCKER" -ne "1" ]; then
                    vecho $0 "Resetting docker fvs..."
                    restart_docker_fvs
                fi

                # create output dir as needed
                if [ ! -z "$OUTPUT" ]; then
                    mkdir -p "$OUTPUT"
                fi
        
                # run the python script
                echo $0 "Running benchmark on dataset: $DATASET w/queries prefix=$QUERY_PATH and batch_size=$BATCH_SIZE and num_boards $NUM_BOARDS..."
                PYTHONPATH=../common python3 -u ./tmp_bench.py \
                        --dataset $DATASET \
                        --query-path $QUERY_PATH \
                        --batch-size $BATCH_SIZE \
                        --num-of-boards $NUM_BOARDS \
                        $VFLAG $SCFLAG $OFLAG $DCDFLAG $CHK_FLAG $HK_FLAG $CR_FLAG
                if [ "$?" -ne "0" ]; then
                    echo "$0: WARNING: python script failed."
                else
                    # export float32 and python-training_manager data if requested
                    if [ ! -z "$EXPORT_DATA_PATH" ]; then
                        vecho $0 "Exporting fvs container data to $EXPORT_DATA_PATH..."
                        export_data $EXPORT_DATA_PATH $DATASET $NUM_BOARDS $BATCH_SIZE
                    fi
                fi

                # do some docker container cleanup - TODO: this may not be needed if docker restart is performed above
                vecho $0 "Python benchmark script is done, cleaning up.  Please wait ..."
                docker exec -it python-training-manager-postgres /clear_fvs.sh
             
                # capture specific docker logs
                vecho $0 "Capturing specific docker container logs..."
                capture_docker_logs $OUTPUT $DATASET $NUM_BOARDS $BATCH_SIZE

            done
    done

#
# Finalize
#

echo "$0: Done."
