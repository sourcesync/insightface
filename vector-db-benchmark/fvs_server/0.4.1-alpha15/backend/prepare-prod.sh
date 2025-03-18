#!/bin/bash

set -e
root_path=${elastic_similarity_public_dir:-/home/public/elastic-similarity}

create_path(){
    local path=$1
    if [ ! -d $path ]; then
        echo -n "directory is not exists, create path: $path. "
        sudo mkdir -p $path
        echo -n "set permissions.."
        sudo chmod 777 -R $path
        echo -ne "fine \n\r"
    fi
}


create_folder(){
    #echo "num of arguments $#"
    #echo "create folder: $1"
    create_path $root_path
    create_path $root_path/$1

}


create_folder fvs-kafka
create_folder fvs-redis-data
create_folder python-training-manager-api
create_folder float32_neural
create_folder fvs-zookeeper

echo "all folders are checked."

