#!/usr/bin/env bash

explain_mode=logical
query_timeout=120

for config in "ask" "count" "void"; do
    echo "Building Docker image for $config"

    docker build \
        --build-arg CONFIG_CLIENT="config-$config.json" \
        --build-arg QUERY_TIMEOUT="$query_timeout" \
        --build-arg MAX_MEMORY=16384 \
        --build-arg LOG_LEVEL=info \
        --network host \
        --tag "comunica:$config" \
        ./input/comunica

    for query_set in "automatic" "service"; do
        output_dir="./explained-$query_set-$config"
        context_string=$(cat "./input/comunica/context-$query_set.json")

        echo "Writing explained $explain_mode plans into $output_dir"

        rm -rf "$output_dir" && mkdir "$output_dir"

        for query_path in ./input/"queries-$query_set"/*.rq; do
            query_name=$(basename --suffix=".rq" "$query_path")
            output_path="$output_dir/$query_name.json"

            echo "Explaining $query_name"
            # echo "Output $output_path"

            query_string=$(cat "$query_path")

            # echo "Query: $query_string"
            # echo "Context: $context_string"

            docker run \
                --rm \
                --entrypoint node \
                "comunica:$config" \
                ./bin/query.js \
                --timeout "$query_timeout" \
                --explain "$explain_mode" \
                --query "$query_string" \
                --context "$context_string" \
            >& "$output_path"
        done
    done
done
