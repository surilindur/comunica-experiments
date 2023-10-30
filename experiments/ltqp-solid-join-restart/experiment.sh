#!/bin/bash

yarn install --immutable

yarn run jbr generate-combinations
yarn run jbr prepare

docker_tag=solidlab/catalogue:dev
docker_file=./input/dockerfiles/catalogue.dockerfile

docker build --network host --tag "$docker_tag" --file "$docker_file" .
docker run --volume ./generated:/generated "$docker_tag"

rm generated/out-queries/interactive-complex-*.sparql

yarn run jbr run
