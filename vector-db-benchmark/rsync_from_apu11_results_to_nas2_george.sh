#!/bin/bash

set -e
set -x

USER=gwilliams
TARGETDIR="/mnt/nas2/george/vdbenchmark_results/"
TARGET="$USER@192.168.99.40:$TARGETDIR"
rsync -azvd0  ./results/ "$TARGET"


