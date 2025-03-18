#!/bin/bash

#
# weaviate
#

# Note that in practice, we ran each benchmark separately due to an issue in shutdown and timeout issue (see below)
python3 run.py --engines weaviate-m-16-ef-128 --datasets deep-image-96-angular
python3 run.py --engines weaviate-m-32-ef-128 --datasets deep-image-96-angular
python3 run.py --engines weaviate-m-32-ef-256 --datasets deep-image-96-angular
python3 run.py --engines weaviate-m-32-ef-512 --datasets deep-image-96-angular
python3 run.py --engines weaviate-m-64-ef-256 --datasets deep-image-96-angular
# We rebooted and changed weaviate docker singel-node server config related to memory limits
python3 run.py --engines weaviate-m-64-ef-512 --datasets deep-image-96-angular --timeout 172800

