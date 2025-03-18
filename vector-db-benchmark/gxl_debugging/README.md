
GXL Index Search Issue

# Introduction

We found an issue with a GXL built index, and not sure what exactly the problem is.

Basically, we built a GXL index with the GXL2 utilities.  It appears to build successfully, but when we use HNSWLib on the index, it fails with an error we've never seen before.

Below are instructions to reproduce and also what we see when we run it on "apu11" in the SV datacenter.

The script also runs on a GXL index we built several weeks ago, and it seems to work correctly.

Hopefully its something obvious.  Thanks for you help.

# How To Reproduce

Usage: `python3 gxl_debugging.py --dataset <DATASET_PATH_HERE> --gxl <GXL_BIN_PATH_HERE>`

Example: `python3 gxl_debugging.py --dataset ../datasets/deep-image-96-angular/deep-image-96-angular.hdf5 --gxl /home/public/GXL_2.0/bin`

# Example Output

```
$ conda create -n gxl-debugging python=3.10

$ conda activate gxl-debugging

$ python -m pip install -r ../requirements

$ python3 gxl_debugging.py --dataset ../datasets/deep-image-96-angular/deep-image-96-angular.hdf5 --gxl /home/public/GXL_2.0/bin
running gxl cen gen

There are 4 H/W contexts
H/W context 0: num_apucs=4, memory_size=14979955712, hw_general_info=600_MHZ-INDIRECT_R-INDIRECT_W, status=0
H/W context 1: num_apucs=4, memory_size=14979955712, hw_general_info=600_MHZ-INDIRECT_R-INDIRECT_W, status=0
H/W context 2: num_apucs=4, memory_size=14979955712, hw_general_info=600_MHZ-INDIRECT_R-INDIRECT_W, status=0
H/W context 3: num_apucs=4, memory_size=14979955712, hw_general_info=600_MHZ-INDIRECT_R-INDIRECT_W, status=0

Number of APUC in use is 16
Number of CPU cores is 104

QUANTIZED DB CREATION TIME IS 903ms.

Refining centroids...
Splitting big cluster whose size is 78177, Target size = 50000
Splitting big cluster whose size is 82585, Target size = 50000
Splitting big cluster whose size is 88242, Target size = 50000
Splitting big cluster whose size is 88776, Target size = 50000
Splitting big cluster whose size is 90481, Target size = 50000
Splitting big cluster whose size is 78054, Target size = 50000
Splitting big cluster whose size is 84445, Target size = 50000
Splitting big cluster whose size is 94671, Target size = 50000
Splitting big cluster whose size is 92883, Target size = 50000
Splitting big cluster whose size is 75411, Target size = 50000
Splitting big cluster whose size is 81116, Target size = 50000
Splitting big cluster whose size is 103610, Target size = 50000
Splitting big cluster whose size is 87773, Target size = 50000
Splitting big cluster whose size is 161496, Target size = 50000
Splitting big cluster whose size is 88034, Target size = 50000
Splitting big cluster whose size is 118150, Target size = 50000
Splitting big cluster whose size is 82850, Target size = 50000
Splitting big cluster whose size is 80216, Target size = 50000
Splitting big cluster whose size is 79998, Target size = 50000
Splitting big cluster whose size is 89021, Target size = 50000
Splitting big cluster whose size is 75114, Target size = 50000
Splitting big cluster whose size is 94296, Target size = 50000
Splitting big cluster whose size is 96150, Target size = 50000
Splitting big cluster whose size is 89367, Target size = 50000
Splitting big cluster whose size is 80610, Target size = 50000
Splitting big cluster whose size is 118603, Target size = 50000
CENTROIDS GENERATION TIME IS 48s.

CENTROIDS GENERATION TIME IS 0mn.

running gxl

There are 4 H/W contexts
H/W context 0: num_apucs=4, memory_size=14979955712, hw_general_info=600_MHZ-INDIRECT_R-INDIRECT_W, status=0
H/W context 1: num_apucs=4, memory_size=14979955712, hw_general_info=600_MHZ-INDIRECT_R-INDIRECT_W, status=0
H/W context 2: num_apucs=4, memory_size=14979955712, hw_general_info=600_MHZ-INDIRECT_R-INDIRECT_W, status=0
H/W context 3: num_apucs=4, memory_size=14979955712, hw_general_info=600_MHZ-INDIRECT_R-INDIRECT_W, status=0

Number of APUC in use is 16
Number of CPU cores is 104

QUANTIZED DB CREATION TIME IS 960ms.

APUC workers search time is 6214ms.
Mergers supplementary time is 18ms.
Search on centroids average speed is: 9.92274us
CLSTRS AND QUERIES GENERATOR TIME IS 6233ms.

KNN Graph allocation time is 1017ms.
APUC workers search time is 71599ms.
Mergers supplementary time is 1267ms.
Search on clusters average speed is: 13.3431us
KNN Graph writing time is 626ms.
KNN Graph distances writing time is 307ms.
KNN GRAPH GENERATOR TIME IS 74845ms.
===============
TOTAL TIME IS 82932ms.
make symmetric
	Number of records = 9990000
	K = 32
	Number of CPU cores: 104
	MEMORY ALLOCATIONS AND READ FROM FILE TIME IS: 1s
	REVERSE EDGES MATRIX BUILD TIME IS: 3s
	MERGING AND PRINTING TO FILE TIME IS: 0s
	PRINTING SUPPLEMENTARY TIME IS: 0s
Total time is:6s.
idx gen
Building index:
Initializing and allocating memory...
Building upper layers:
Sampling the database...
Elapsed time is: 0s.
Adding points...
Elapsed time is: 3s.
Finished building upper layers.
BUILD UPPER LEVELS TIME IS: 5s.
Finished building index file.
Build index time is 6s.
searching using ef: 64
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.903
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.7225
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.7393
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.9105
searching using ef: 128
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.903
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.7225
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.7393
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.9105
searching using ef: 256
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.903
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.7225
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.7393
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.9105
searching using ef: 512
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.903
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.7225
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.7393
Cannot return the results in a contiguous 2D array. Probably ef or M is too small
error on query no.9105
Checking against existing GXL index...
(gxl-debugging) gwilliams@sv7-apu11:~/Projects/Qdrant_benchmarking/jacob-fork/vector-db-benchmark/gxl_debugging$ 
```
