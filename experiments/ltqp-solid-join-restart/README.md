# Solid Join Restart

This is an experimental experiment for measuring the impact of using predicate counts to estimate triple pattern cardinalities
while performing Link Traversal Query Processing (LTQP) over Solid pods.
The experiments use [jbr](https://github.com/rubensworks/jbr.js) as the benchmark runner
and [SolidBench](https://github.com/SolidBench/SolidBench.js) as the dataset.
The engine implementation is taken from a set of [work-in-progress Comunica components](https://github.com/surilindur/comunica-components).

## Dependencies

* NodeJS 21+ with corepack enabled
* Docker 26+

## Running

After cloning the repository, install the dependencies.

```bash
yarn install --immutable
```

Afterwards, the different test cases need to be prepared.
This will generate the various combinations of configuration files needed for those cases.

```bash
yarn run jbr generate-combinations
```

The experiments can then be prepared.
The preparation step generates the SolidBench dataset and builds the Docker images for the query engine.
This step will fail when executed the first time, because the SolidBench validation generator is non-functioning.
Thus, this command needs to be run twice.

```bash
yarn run jbr prepare
yarn run jbr prepare
```

The VoID descriptions for the datasets can be generated with the following Bash script:

```bash
docker_tag=catalogue:dev
docker_file=./input/dockerfiles/catalogue.dockerfile

docker build --network host --tag "$docker_tag" --file "$docker_file" .
docker run --volume ./generated:/generated "$docker_tag"
```

The complex queries can be removed to avoid running them.
They will fail anyway, so removing them saves some time in the experiments.

```bash
rm generated/out-queries/interactive-complex-*.sparql
```

Finally, the experiments can be executed:

```bash
yarn run jbr run
```

## Results

The results will go into the `output/` folder in this directory,
where each test case will have its own combination folder.
These results can then be processed using [SPARQL Benchmark Recap](https://github.com/surilindur/sparql-benchmark-recap).
