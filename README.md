<p align="center">
  <img alt="Comunica" src=".github/assets/logo.svg" width="64">
</p>

<p align="center">
  <strong>Comunica Experiments</strong>
</p>

<p align="center">
  <a href="https://github.com/surilindur/comunica-experiments/actions/workflows/ci.yml"><img alt="Workflow: CI" src=https://github.com/surilindur/comunica-experiments/actions/workflows/ci.yml/badge.svg?branch=main"></a>
  <a href="https://creativecommons.org/licenses/by/4.0/"><img alt="Licence: CC-BY-4.0" src="https://img.shields.io/badge/License-CC_BY_4.0-white.svg"></a>
</p>

This monorepository contains various experiments
with the [Comunica](https://github.com/comunica/comunica) query engine
using a combination of [SolidBench](https://github.com/SolidBench/SolidBench.js),
[Docker Compose](https://docs.docker.com/compose/)
and [sparql-benchmark-runner](https://github.com/comunica/sparql-benchmark-runner.js).
The experiments are stored here for future reference, transparency and reproducibility.
The following experiments reside here:

* [**Link Traversal over Solid**](experiments/ltqp-solid-default/), as a baseline reference experiment for link traversal over Solid pods.
* [**Link Traversal over Solid with Bloom Filters**](experiments/ltqp-solid-bloom-filters/), to explore the use of Bloom filters to remove unnecessary links during link traversal over Solid pods.
* [**Link Traversal over Solid with Join Plan Restarts**](experiments/ltqp-solid-join-restart/), to evaluate the impact of restarting most of the query plan upon cardinality estimate updates.

## Running

After cloning the repository, install dependencies with [Yarn](https://github.com/yarnpkg/berry).

```bash
yarn install --immutable
```

Each experiment can then be executed using `jbr` in the experiment directory:

```bash
yarn jbr --help
```

## Issues

Please feel free to report any issues on the GitHub issue tracker.

## License

The experiments here are copyrighted and released under the [CC-BY-4.0 license](https://creativecommons.org/licenses/by/4.0/).
