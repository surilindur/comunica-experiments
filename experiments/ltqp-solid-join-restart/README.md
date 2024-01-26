# Solid Join Restart

This is an experimental experiment for measuring the impact of using predicate counts to estimate triple pattern cardinalities while performing Link Traversal Query Processing (LTQP) over Solid pods using [jbr](https://github.com/rubensworks/jbr.js) and [SolidBench.js](https://github.com/SolidBench/SolidBench.js). The engine implementation is taken from a set of [work-in-progress Comunica components](https://github.com/surilindur/comunica-components).

The following dependencies need to be met to execute the experiments:

* NodeJS 18+ with corepack enabled
* Docker

The experiments can be reproduced after cloning the repository by installing the dependencies:

```bash
yarn install --immutable
```

The SolidBench test data can then be generated (this might fail at validation generation step, in that case simply re-run the command):

```bash
yarn run jbr generate-combinations
```

The experiments prepared:

```bash
yarn run jbr prepare
```

The dataset descriptions can be generated with the following Bash script:

```bash
docker_tag=catalogue:dev
docker_file=./input/dockerfiles/catalogue.dockerfile

docker build --network host --tag "$docker_tag" --file "$docker_file" .
docker run --volume ./generated:/generated "$docker_tag"
```

The complex queries can be removed to avoid running them:

```bash
rm generated/out-queries/interactive-complex-*.sparql
```

Finally, the experiments can be executed:

```bash
yarn run jbr run
```

The provided [script](./experiment.sh) has all of these commands included in it. The results will go into the `output/` folder in this directory.
