#!/bin/bash

if [ ! -e ../../node_modules ]; then
    echo "Installing dependencies"
    yarn install --immutable
fi

if [ ! -e combinations ]; then
    echo "Generating combinations"
    yarn run jbr generate-combinations
    yarn run jbr prepare
    yarn run jbr prepare
fi

if [ ! -e ./generated/out-fragments/http/solidbench-server_3000/pods/00000000000000000933/.meta ]; then
    echo "Running catalogue to generate VoID descriptions"
    docker_tag=solidlab/catalogue:dev
    docker_file=./input/dockerfiles/catalogue.dockerfile
    docker build --network host --tag "$docker_tag" --file "$docker_file" .
    docker run --volume ./generated:/generated "$docker_tag"
fi

if [ ! -e generated/out-queries/interactive-complex-1.sparql ]; then
    echo "Removing complex queries"
    rm generated/out-queries/interactive-complex-*.sparql
fi

echo "Running benchmark"
yarn run jbr run
