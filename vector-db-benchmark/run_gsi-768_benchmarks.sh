#!/bin/bash

#
# gsi 768 bits
#

python run.py --engines gsi-768-clusters-250-nprobe-150-nprobe_rerank-300-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-300-nprobe-200-nprobe_rerank-350-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-350-nprobe-250-nprobe_rerank-400-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-400-nprobe-300-nprobe_rerank-450-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-450-nprobe-350-nprobe_rerank-500-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-500-nprobe-400-nprobe_rerank-550-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-550-nprobe-450-nprobe_rerank-600-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-600-nprobe-500-nprobe_rerank-650-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-650-nprobe-550-nprobe_rerank-700-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-700-nprobe-600-nprobe_rerank-750-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-750-nprobe-650-nprobe_rerank-800-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-800-nprobe-700-nprobe_rerank-850-hammingk --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-850-nprobe-750-nprobe_rerank-900-hammingk --datasets deep-image-96-angular

