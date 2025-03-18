#!/bin/bash
set -e
elastic_similarity_public_dir=${elastic_similarity_public_dir:-/home/public/elastic-similarity}
if [ ! -d "${elastic_similarity_public_dir}" ]; then
   echo "create elastic-similarity public directory (${elastic_similarity_public_dir})"
   sudo mkdir -p ${elastic_similarity_public_dir}
   sudo chmod -R 777 ${elastic_similarity_public_dir}
fi
create_volume_dir(){
   dir=${elastic_similarity_public_dir}/$1
   if [ ! -d $dir ]; then
      echo "create volume directory: $dir"
      sudo mkdir $dir
      sudo chmod -R 777 $dir
   fi
}
create_volume_dir kafka
create_volume_dir zookeeper
create_volume_dir postgresql
create_volume_dir pgadmin4
create_volume_dir redis
create_volume_dir data
create_volume_dir cassandra
create_volume_dir upload_store
create_volume_dir float32_neural
create_volume_dir float32_neural/config
create_volume_dir fvs-postgresql
