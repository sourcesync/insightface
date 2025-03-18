#!/bin/bash

set -e
set -x


#
# m=32 efc=128
#
M=32
EFC=128
# copy data files
cd /home/jacob/GXL/tmp/ && rm -f * && cp /home/jacob/GXL/deep-angular.fbin . && cp /home/jacob/GXL/labels.lbl . && ls /home/jacob/GXL/tmp/
# run-gxl-cen-gen
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-gxl-cen-gen /home/jacob/GXL/tmp/deep-angular.fbin
# run-gxl 
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-gxl --db /home/jacob/GXL/tmp/deep-angular.fbin --cent /home/jacob/GXL/tmp/generated_q_centroids.bin
# run-make-symmetri
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-make-symmetric /home/jacob/GXL/tmp/knn_graph.bin /home/jacob/GXL/tmp/distances.bin
# gxl-hnsw-idx-gen
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/gxl-hnsw-idx-gen /home/jacob/GXL/tmp/deep-angular.fbin /home/jacob/GXL/tmp/labels.lbl /home/jacob/GXL/tmp/s_knn_graph.bin $M $EFC
echo

#
# m=32 efc=256
#
M=32
EFC=256
# copy data files
cd /home/jacob/GXL/tmp/ && rm -f * && cp /home/jacob/GXL/deep-angular.fbin . && cp /home/jacob/GXL/labels.lbl . && ls /home/jacob/GXL/tmp/
# run-gxl-cen-gen
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-gxl-cen-gen /home/jacob/GXL/tmp/deep-angular.fbin
# run-gxl 
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-gxl --db /home/jacob/GXL/tmp/deep-angular.fbin --cent /home/jacob/GXL/tmp/generated_q_centroids.bin
# run-make-symmetri
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-make-symmetric /home/jacob/GXL/tmp/knn_graph.bin /home/jacob/GXL/tmp/distances.bin
# gxl-hnsw-idx-gen
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/gxl-hnsw-idx-gen /home/jacob/GXL/tmp/deep-angular.fbin /home/jacob/GXL/tmp/labels.lbl /home/jacob/GXL/tmp/s_knn_graph.bin $M $EFC
echo

#
# m=64 efc=256
#
M=64
EFC=256
# copy data files
cd /home/jacob/GXL/tmp/ && rm -f * && cp /home/jacob/GXL/deep-angular.fbin . && cp /home/jacob/GXL/labels.lbl . && ls /home/jacob/GXL/tmp/
# run-gxl-cen-gen
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-gxl-cen-gen /home/jacob/GXL/tmp/deep-angular.fbin
# run-gxl 
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-gxl --db /home/jacob/GXL/tmp/deep-angular.fbin --cent /home/jacob/GXL/tmp/generated_q_centroids.bin
# run-make-symmetri
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-make-symmetric /home/jacob/GXL/tmp/knn_graph.bin /home/jacob/GXL/tmp/distances.bin
# gxl-hnsw-idx-gen
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/gxl-hnsw-idx-gen /home/jacob/GXL/tmp/deep-angular.fbin /home/jacob/GXL/tmp/labels.lbl /home/jacob/GXL/tmp/s_knn_graph.bin $M $EFC
echo

#
# m=64 efc=512
#
M=64
EFC=512
# copy data files
cd /home/jacob/GXL/tmp/ && rm -f * && cp /home/jacob/GXL/deep-angular.fbin . && cp /home/jacob/GXL/labels.lbl . && ls /home/jacob/GXL/tmp/
# run-gxl-cen-gen
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-gxl-cen-gen /home/jacob/GXL/tmp/deep-angular.fbin
# run-gxl 
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-gxl --db /home/jacob/GXL/tmp/deep-angular.fbin --cent /home/jacob/GXL/tmp/generated_q_centroids.bin
# run-make-symmetri
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/run-make-symmetric /home/jacob/GXL/tmp/knn_graph.bin /home/jacob/GXL/tmp/distances.bin
# gxl-hnsw-idx-gen
cd /home/jacob/GXL/tmp/ && /home/jacob/GXL/bin/gxl-hnsw-idx-gen /home/jacob/GXL/tmp/deep-angular.fbin /home/jacob/GXL/tmp/labels.lbl /home/jacob/GXL/tmp/s_knn_graph.bin $M $EFC
echo

echo "Done."
