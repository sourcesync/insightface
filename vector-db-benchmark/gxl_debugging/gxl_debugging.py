import hnswlib
import h5py
import os
from GXL_helpers import convert_np_to_fbin
from subprocess import run
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dataset') #path to the hdf5 dataset file
parser.add_argument('-g', '--gxl') #supply a path to GXL/bin
args = parser.parse_args()

f = h5py.File(args.dataset, "r")
test = f['test'][:]
out = f"/tmp/tmpDB.bin"
if not os.path.exists(out):
    convert_np_to_fbin(f["train"][:], out)
f.close()

# run index generation script
run(f"./gxl_debugging.sh {args.gxl}", shell=True)

# read index
index = hnswlib.Index(space="cosine", dim=96)
index.load_index(f"/tmp/deep1B_9m_ef_128_M_32_gxl.bin")

ef_list = [64, 128, 256, 512]
for ef in ef_list:
    print(f"searching using ef: {ef}")
    index.set_ef(ef)
    for i in range(len(test)):
        try:
            _, _ = index.knn_query(test[i], k=100)
        except Exception as e:
            print(e)
            print(f'error on query no.{i}')

print("Checking against existing GXL index...")
tmp = hnswlib.Index(space="cosine", dim=96)
tmp.load_index("/mnt/nas1/GXL/deep1B/v2.0_with250Mfix/deep1B_1m_ef_64_M_32_gxl.bin")
tmp.set_ef(64)
for i in range(len(test)):
    try:
        _, _ = tmp.knn_query(test[i], k=100)
    except Exception as e:
        print(e)
        print(f'error on query no.{i}')