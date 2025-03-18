#!/bin/bash
root_path=/home/public/elastic-similarity
kafka_path=$root_path/fvs-kafka
zookeeper_path=$root_path/fvs-zookeeper
python_training_path=$root_path/python-training-manager-api
python_postgresql_path=$root_path/fvs-postgresql

create_path(){
    if [ ! -d $1 ]; then
        echo "not exists, create $1"
        sudo mkdir -p $1
        sudo chmod 777 -R $1
    fi
}

create_path $root_path
create_path $kafka_path
create_path $zookeeper_path
create_path $python_training_path
create_path $python_postgresql_path

export SERVER_TYPE=CLOUD
export FVS_TRAIN_POSTGRES_USER=fvs_post_user
export FVS_TRAIN_POSTGRES_PASSWORD=fvs_post_passwd
export FVS_TRAIN_POSTGRES_PORT=14032


export COMPOSE_PROFILES=backend,localtrain
export TRAIN_KAFKA_HOST=192.168.42.60
#export TRAIN_KAFKA_HOST=192.168.42.32
export TRAIN_KAFKA_PORT=29094
export HOSTNAME=192.168.42.60
#export HOSTNAME=192.168.42.32


export ROOT_SHARED=/efs/data/elastic_shared/elastic-data
#export TM_WORKSPACE=$ROOT_SHARED/python-training-manager-api/
export TM_WORKSPACE=/home/public/elastic-similarity/python-training-manager-api/
export TM_WORKSPACE_OUTPUT=$ROOT_SHARED/python-training-manager-api/cache/
create_path $ROOT_SHARED
create_path $TM_WORKSPACE


docker-compose -f \
    docker-compose-fvs.yml \
    -p elastic-similarity \
    up -d #--remove-orphans

