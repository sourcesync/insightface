#!/bin/bash

#
# qdrant
#

# Note that in practice, we ran each benchmark separately due to an issue in shutdown in run.py
python3 run.py --engines qdrant-m-16-ef-128 --datasets deep-image-96-angular
python3 run.py --engines qdrant-m-32-ef-128 --datasets deep-image-96-angular
python3 run.py --engines qdrant-m-32-ef-256 --datasets deep-image-96-angular
python3 run.py --engines qdrant-m-32-ef-512 --datasets deep-image-96-angular
python3 run.py --engines qdrant-m-64-ef-256 --datasets deep-image-96-angular
python3 run.py --engines qdrant-m-64-ef-512 --datasets deep-image-96-angular
python3 run.py --engines qdrant-m-128-ef-512 --datasets deep-image-96-angular

