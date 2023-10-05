# Solid Join Restart

This is an experimental experiment for measuring the impact of using predicate counts to estimate triple pattern cardinalities while performing Link Traversal Query Processing (LTQP) over Solid pods using [jbr](https://github.com/rubensworks/jbr.js) and [SolidBench.js](https://github.com/SolidBench/SolidBench.js). The engine implementation is taken from a set of [work-in-progress Comunica components](https://github.com/surilindur/comunica-components).

The necessary dependencies can be installed with Yarn:

```bash
yarn install --immutable
```

Generate the combinations:

```bash
yarn jbr generate-combinations
```

Generate the dataset and queries:

```bash
yarn jbr prepare
```

Generate the VoID descriptions for all the Solid pods:

```bash
docker build --network host --tag solidlab/catalogue:dev --file ./input/dockerfiles/catalogue.dockerfile
docker run --volume ./generated:/generated solidlab/catalogue:dev
```

Run the experiment locally:

```bash
yarn jbr run
```

The `output/` directory should contain all experiment results.

## Issues

Please feel free to report any issues on the GitHub issue tracker. Thank you!
