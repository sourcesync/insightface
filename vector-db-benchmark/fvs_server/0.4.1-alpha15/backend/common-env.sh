#docker_registry=minsk:5005
source ${run_dir}/version.properties
docker_registry=186285203186.dkr.ecr.us-west-1.amazonaws.com
export DOCKER_REGISTRY=${docker_registry}/
export HOSTNAME=${HOSTNAME}
export REDIS_VERSION=5.0.9
export CONFLUENT_KAFKA_VERSION=7.4.0
export BITNAMI_KAFKA_VERSION=3.3.2
export ES_FTP_DIR=/home/ftpuser
