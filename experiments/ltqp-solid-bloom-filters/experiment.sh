#!/bin/bash

if [ ! -e ../../node_modules ]; then
    echo "Installing dependencies"
    yarn install --immutable
fi

# Ensure the appropriate version of rdf-dataset-fragmenter is used by the SolidBench
# of this specific experiment here. Otherwise it will use the NPM version.

ln -sf ../../node_modules/rdf-dataset-fragmenter ../../node_modules/solidbench/node_modules/rdf-dataset-fragmenter

if [ ! -e combinations ]; then
    echo "Generating combinations"
    yarn run jbr generate-combinations
    # The validation step will fail, so it can be skipped by creating the directories
    mkdir generated/out-validate
    mkdir generated/out-validate-params
    yarn run jbr prepare
fi

if [ -e generated/out-queries/interactive-complex-1.sparql ]; then
    echo "Removing complex queries"
    rm generated/out-queries/interactive-complex-*.sparql
fi

echo "Running benchmark"
yarn run jbr run
