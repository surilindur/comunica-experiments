#!/bin/bash

yarn install --immutable

yarn run generate

execution_uuid=$(uuidgen)

catalogue_tag="comunica-experiments/catalogue:$execution_uuid"
catalogue_file=./input/dockerfiles/catalogue.dockerfile
catalogue_name=catalogue

client_tag="comunica-experiments/client:$execution_uuid"
client_file=./input/dockerfiles/client.dockerfile
client_name=client

server_tag=solid/community-server:7.0.1
server_name=server

docker build --network host --tag "$catalogue_tag" --file "$catalogue_file" .
docker build --network host --tag "$client_tag" --file "$client_file" .

docker run \
    --volume ./generated:/generated \
    --name "$catalogue_name" \
    "$catalogue_tag"

docker run \
    --volume ./generated/out-fragments/http/localhost_3000/pods:/data \
    --volume ./input/config-server/config-default.json:/tmp/config.json \
    --env CSS_LOGGING_LEVEL=error \
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

docker run \
    --volume ./generated/out-queries:/queries \
    --volume ./input/config-client:/config \
    --volume ./experiment.json:/tmp/experiment.json \
    --volume ./output:/results \
    --name "$client_name" \
    "$client_tag" \
    --experiment /tmp/experiment.json

docker stop "$server_name"

client_logs=$(docker inspect --format='{{.LogPath}}' "$client_name")
cp "$client_logs" ./output/client.log

server_logs=$(docker inspect --format='{{.LogPath}}' "$server_name")
cp "$server_logs" ./output/server.log

catalogue_logs=$(docker inspect --format='{{.LogPath}}' "$catalogue_name")
cp "$catalogue_logs" ./output/catalogue.log
