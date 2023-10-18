#!/bin/bash

yarn install --immutable

yarn run jbr generate-combinations
yarn run jbr prepare

docker_tag=solidlab/catalogue:dev
docker_file=./input/dockerfiles/catalogue.dockerfile

docker build --network host --tag "$docker_tag" --file "$docker_file" .
docker run --volume ./generated:/generated "$docker_tag"

# this is a workaround for issue where jbr.js produces a directory
# rmdir combinations/combination_0/input/context-client.json/

# context='{
#  "sources": [],
#  "lenient": true
# }'

# echo "$context" > combinations/combination_0/input/context-client.json
# echo "$context" > combinations/combination_1/input/context-client.json

# this is to delete all queries that should not be run
rm generated/out-queries/interactive-complex-*.sparql
#rm generated/out-queries/interactive-short-*.sparql
#rm generated/out-queries/interactive-discover-1.sparql
#rm generated/out-queries/interactive-discover-3.sparql
#rm generated/out-queries/interactive-discover-4.sparql
#rm generated/out-queries/interactive-discover-5.sparql
#rm generated/out-queries/interactive-discover-7.sparql
#rm generated/out-queries/interactive-discover-8.sparql

yarn run jbr run
