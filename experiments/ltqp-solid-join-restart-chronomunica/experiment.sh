#!/bin/bash

execution_uuid=$(uuidgen)

run_generate=0
run_catalogue=0
run_server=1
run_client=1
run_prune=1

catalogue_tag="comunica-experiments/catalogue:$execution_uuid"
catalogue_file=./dockerfiles/catalogue.dockerfile
catalogue_name=catalogue

client_tag="comunica-experiments/client:$execution_uuid"
client_file=./dockerfiles/client.dockerfile
client_name=client

server_tag=solidproject/community-server:7.0.1
server_name=server

if [ $run_generate = 1 ]; then
    yarn install --immutable
    yarn run generate
fi

if [ $run_catalogue = 1 ]; then
    echo "Building catalogue as \"$catalogue_tag\" using $catalogue_file"
    docker rm --force "$catalogue_name"
    docker build --network host --tag "$catalogue_tag" --file "$catalogue_file" .
    echo "Running catalogue as \"$catalogue_name\" using $catalogue_tag"
    docker run \
        --volume ./out-fragments/http/localhost_3000/pods:/pods \
        --name "$catalogue_name" \
        "$catalogue_tag"
fi

if [ $run_server = 1 ]; then
    echo "Starting server as \"$server_name\" using $server_tag"
    docker rm --force "$server_name"
    docker run \
        --network host \
        --volume ./out-fragments/http/localhost_3000:/data \
        --volume ./config-server/config-default.json:/tmp/config.json \
        --env CSS_LOGGING_LEVEL=info \
        --env CSS_ROOT_FILE_PATH=/data \
        --env CSS_BASE_URL=http://localhost:3001 \
        --env CSS_PORT=3001 \
        --env CSS_CONFIG=/tmp/config.json \
        --env NODE_ENV=production \
        --env NODE_OPTIONS=--max-old-space-size=8192 \
        --name "$server_name" \
        --detach \
        "$server_tag"
    sleep 10
fi

if [ $run_client = 1 ]; then
    echo "Building client as \"$client_tag\" using $client_file"
    docker rm --force "$client_name"
    docker build --network host --tag "$client_tag" --file "$client_file" .
    echo "Running client as \"$client_name\" using $client_tag"
    docker run \
        --network host \
        --volume ./out-queries/:/queries/ \
        --volume ./config-client/:/configs/ \
        --volume ./experiment.json:/tmp/experiment.json \
        --volume ./results/:/results/ \
        --name "$client_name" \
        "$client_tag" \
        --experiment /tmp/experiment.json
fi

if [ $run_server = 1 ]; then
    echo "Stopping server with name \"$server_name\""
    docker stop "$server_name"
fi

if [ $run_prune = 1 ]; then
    echo "Running docker system prune"
    docker system prune --force
fi
