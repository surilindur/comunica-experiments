#!/bin/bash

yarn install --immutable

yarn run jbr generate-combinations
yarn run jbr prepare

docker_tag=solidlab/catalogue:dev
docker_file=./input/dockerfiles/catalogue.dockerfile

docker build --network host --tag "$docker_tag" --file "$docker_file" --build-arg CONFIG_CATALOGUE=./input/config-catalogue.json .
docker run --volume ./generated:/generated "$docker_tag"

# this is a workaround for issue where jbr.js produces a directory
rmdir combinations/combination_0/input/context-client.json/

context='{
  "sources": [],
  "lenient": true
}'

echo "$context" > combinations/combination_0/input/context-client.json
echo "$context" > combinations/combination_1/input/context-client.json

yarn run jbr run
