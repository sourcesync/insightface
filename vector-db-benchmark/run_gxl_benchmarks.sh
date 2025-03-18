#!/bin/bash

#
# hnswlib
#

python run.py --engines hnswlib-gxl-m-32-ef-128 --datasets deep-image-96-angular
python run.py --engines hnswlib-gxl-m-32-ef-256 --datasets deep-image-96-angular
python run.py --engines hnswlib-gxl-m-64-ef-256 --datasets deep-image-96-angular
python run.py --engines hnswlib-gxl-m-64-ef-512 --datasets deep-image-96-angular # NOTE efc=512 did not work in the GXL version we used
