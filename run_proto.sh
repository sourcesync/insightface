#!/bin/bash

python -u proto.py 2>&1 | tee "data/proto.log"
