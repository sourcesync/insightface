#!/bin/bash

set -e
set -x

USER=gwilliams
SOURCEDIR="/home/gwilliams/Projects/Qdrant_benchmarking/jacob-fork/vector-db-benchmark/results/"
SOURCE="$USER@192.168.99.40:$SOURCEDIR"
mkdir -p ./results
rsync -azvd0 "$SOURCE" ./results/

#gw SOURCEDIR="/mnt/nas2/jacob/weaviate_results/"
#gw SOURCE="$USER@192.168.99.40:$SOURCEDIR"
#gw rsync -azvd0 "$SOURCE" ./results/

#gw SOURCEDIR="/mnt/nas1/fvs_benchmark_datasets/deep-"
#gw SOURCE="$USER@192.168.99.40:$SOURCEDIR"
#gw declare -a sizes=("10M" "50M" "100M")
#gw mkdir -p ./data
#gw for size in "${sizes[@]}"
#gw do
#gw    rsync -azvd0 "$SOURCE""$size"-gt-1000.npy ./data/
#gw done
