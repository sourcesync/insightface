#!/bin/bash

DATASET_ID="abf7fc1a-2ffb-4328-8b83-045b72984a1a"

python tmp_bench.py --dataset_id $DATASET_ID --batch-size 10 --search_elapsed -1 --verbose
