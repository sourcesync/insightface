#!/bin/bash

#
# hnswlib
#

python run.py --engines hnswlib-default --datasets deep-image-96-angular
python run.py --engines hnswlib-m-16-ef-128 --datasets deep-image-96-angular
python run.py --engines hnswlib-m-32-ef-128 --datasets deep-image-96-angular
python run.py --engines hnswlib-m-32-ef-256 --datasets deep-image-96-angular
python run.py --engines hnswlib-m-32-ef-512 --datasets deep-image-96-angular
python run.py --engines hnswlib-m-64-ef-256 --datasets deep-image-96-angular
python run.py --engines hnswlib-m-64-ef-512 --datasets deep-image-96-angular
