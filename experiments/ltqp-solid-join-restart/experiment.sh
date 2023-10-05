#!/bin/bash

yarn install --immutable

yarn jbr generate-combinations
yarn jbr prepare

docker_tag=solidlab/catalogue:dev
docker_file=./input/dockerfiles/catalogue.dockerfile

docker build --network host --tag "$docker_tag" --file "$docker_file" --build-arg CONFIG_CATALOGUE=./input/config-catalogue.json .
docker run --volume ./generated:/generated "$docker_tag"

yarn jbr run
