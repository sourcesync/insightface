#!/bin/bash
psql postgresql://fvs_post_user:gsi4ever@localhost:14032/caching_db -c "delete from flat_trains";
psql postgresql://fvs_post_user:gsi4ever@localhost:14032/caching_db -c "delete from clusters_trains";