#!/bin/bash

export BIN_dir=$1
export TMP=/tmp
export DB=${TMP}/tmpDB.bin
export LABELS=${TMP}/labels.lbl
export CEN=${TMP}/generated_q_centroids.bin
export KNN=${TMP}/knn_graph.bin
export DISTS=${TMP}/distances.bin
export S_KNN=${TMP}/s_knn_graph.bin

export M=32
export efc=128

if false; then
    rm -rf ${TMP}
    mkdir ${TMP}
fi
# cen gen

cd ${TMP}
echo running gxl cen gen
${BIN_dir}/run-gxl-cen-gen ${DB}
# run gxl
echo running gxl
${BIN_dir}/run-gxl --db ${DB} --cent ${CEN}
# make symmetric
echo make symmetric
${BIN_dir}/run-make-symmetric ${KNN} ${DISTS}
# idx gen
echo idx gen
${BIN_dir}/gxl-hnsw-idx-gen ${DB} ${LABELS} ${S_KNN} ${M} ${efc}