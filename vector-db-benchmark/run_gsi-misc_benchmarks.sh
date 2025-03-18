#!/bin/bash

#
# gsi misc configs
#

python run.py --engines gsi-64-clusters-default --datasets deep-image-96-angular
python run.py --engines gsi-128-clusters-default --datasets deep-image-96-angular
python run.py --engines gsi-256-clusters-default --datasets deep-image-96-angular
python run.py --engines gsi-512-clusters-default --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-default --datasets deep-image-96-angular
python run.py --engines gsi-128-clusters-noam1 --datasets deep-image-96-angular
python run.py --engines gsi-256-clusters-noam1 --datasets deep-image-96-angular
python run.py --engines gsi-512-clusters-noam1 --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-noam1 --datasets deep-image-96-angular
python run.py --engines gsi-128-clusters-noam2 --datasets deep-image-96-angular
python run.py --engines gsi-256-clusters-noam2 --datasets deep-image-96-angular
python run.py --engines gsi-512-clusters-noam2 --datasets deep-image-96-angular
python run.py --engines gsi-768-clusters-noam2 --datasets deep-image-96-angular

