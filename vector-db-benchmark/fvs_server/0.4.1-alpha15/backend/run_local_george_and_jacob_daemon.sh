#!/bin/bash
run_dir=.
#source ${run_dir}/get_ip.sh
source ${run_dir}/common-env.sh
export DOCKER_VERSION=${product_version}
export BROKER_HOST=broker
source ${run_dir}/prepare.sh
source ${run_dir}/prepare-prod.sh
docker_compose_file=${run_dir}/docker-compose.yml
docker_compose_prod_file=${run_dir}/docker-compose-prod.yml
docker_compose_kafka_file=${run_dir}/kafka-docker-compose.yml
docker_compose_fvs_file=${run_dir}/docker-compose-fvs.yml
docker_compose_cluster=${run_dir}/docker-compose-cluster.yml
docker_compose_single_cluster=${run_dir}/docker-compose-single-cluster.yml
create_path(){
    if [ ! -d $1 ]; then
        echo "not exists, create $1"
        sudo mkdir -p $1
        sudo chmod 777 -R $1
    fi
}
export LOCAL_TRAIN=True
FLOAT32_KAFKA_HOSTNAME=minsk
FLOAT32_KAFKA_PORT=29094
ROOT_SHARED=/home/public/elastic-similarity

#use this for plugin upload 
#export FS_UPLOAD_DIR=/efs/data/upload_store/${HOSTNAME}
#create_path $FS_UPLOAD_DIR

export SERVER_TYPE=CLOUD
export FVS_TRAIN_POSTGRES_USER=fvs_post_user
export FVS_TRAIN_POSTGRES_PASSWORD=fvs_post_passwd
export FVS_TRAIN_POSTGRES_PORT=14032
export FLOAT_TCP_HOST=$(hostname -I | awk '{print $1}')
export USER_DIR=$HOME

if [ $LOCAL_TRAIN = True ] || [ $LOCAL_TRAIN = true ]; then
  echo "use local train"
  export COMPOSE_PROFILES=backend,localtrain,cassandra_single_cluster
  export FLOAT32_KAFKA_HOSTNAME=${HOSTNAME}
else
  echo "use train from $FLOAT32_KAFKA_HOSTNAME"
  export COMPOSE_PROFILES=backend,cassandra_single_cluster
  export FLOAT32_KAFKA_HOSTNAME=$FLOAT32_KAFKA_HOSTNAME
  export FLOAT32_KAFKA_PORT=$FLOAT32_KAFKA_PORT
  export ROOT_SHARED=$ROOT_SHARED
  export DATA_MANAGER_PATH=$ROOT_SHARED/data/${HOSTNAME}
  create_path $ROOT_SHARED
  create_path $DATA_MANAGER_PATH
fi

#gw docker-compose \
#gw  -f ${docker_compose_file} \
#gw  -f ${docker_compose_prod_file} \
#gw  -f ${docker_compose_kafka_file} \
#gw  -f ${docker_compose_fvs_file} \
#gw  -f ${docker_compose_single_cluster} \
#gw  -p elastic-similarity \
#gw  up 

docker-compose \
  -f ${docker_compose_fvs_file} \
  -p elastic-similarity \
  up -d
