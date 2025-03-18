#!/bin/bash

set -e
set -x

USER=gwilliams
SOURCEDIR="/mnt/nas2/jacob/vdbenchmark_results/"
SOURCE="$USER@192.168.99.40:$SOURCEDIR"
mkdir -p ./results
rsync -azvd0 "$SOURCE" ./results/

SOURCEDIR="/mnt/nas2/jacob/weaviate_results/"
SOURCE="$USER@192.168.99.40:$SOURCEDIR"
rsync -azvd0 "$SOURCE" ./results/

SOURCEDIR="/mnt/nas1/fvs_benchmark_datasets/deep-"
SOURCE="$USER@192.168.99.40:$SOURCEDIR"
declare -a sizes=("10M" "50M" "100M")
mkdir -p ./data
for size in "${sizes[@]}"
do
    rsync -azvd0 "$SOURCE""$size"-gt-1000.npy ./data/
done
