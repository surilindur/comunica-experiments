#!/bin/bash

repo=$(realpath "$(pwd)/../..")

if [ ! -e "$repo/node_modules" ]; then
    echo "Installing dependencies"
    yarn install --immutable
fi

# Ensure the appropriate version of rdf-dataset-fragmenter is used by the SolidBench
# of this specific experiment here. Otherwise it will use the NPM version.

source="$repo/node_modules/rdf-dataset-fragmenter"
target="$repo/node_modules/solidbench/node_modules/rdf-dataset-fragmenter"

echo "Linking:"
echo "	from $source"
echo "	to $target"

rm -r "$target"
ln -sf "$source" "$target"

if [ ! -e combinations ]; then
    echo "Generating combinations"
    yarn run jbr generate-combinations
    # The validation step will fail, so it can be skipped by creating the directories
    for dir in combinations/*/; do mkdir -- "$dir"/generated/{out-validate,out-validate-params}; done
    yarn run jbr prepare
fi

if [ -e generated/out-queries/interactive-complex-1.sparql ]; then
    echo "Removing complex queries"
    rm generated/out-queries/interactive-complex-*.sparql
fi

echo "Running benchmark"
yarn run jbr run
