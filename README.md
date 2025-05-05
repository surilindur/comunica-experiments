<p align="center">
  <img alt="Comunica" src=".github/assets/logo.svg" width="128">
</p>

<p align="center">
  <strong>Comunica Experiments</strong>
</p>

<p align="center">
  <a href="https://github.com/surilindur/comunica-experiments/actions/workflows/ci.yml"><img alt="Workflow: CI" src=https://github.com/surilindur/comunica-experiments/actions/workflows/ci.yml/badge.svg?branch=main"></a>
  <a href="https://creativecommons.org/licenses/by/4.0/"><img alt="Licence: CC-BY-4.0" src="https://img.shields.io/badge/License-CC_BY_4.0-white.svg"></a>
</p>

This repository contains verious experiments with the [Comunica](https://github.com/comunica/comunica) query engine,
stored here for future reference, transparency and reproducibility.
The following experiments reside here:

* [**Link Traversal over Solid**](experiments/ltqp-solid-default/), as a baseline reference experiment for link traversal over Solid pods. The purpose of this experiment is to exist as a template of sorts, as well as a reference point when needed for sanity checks. The experiment has all resources stored in documents based on their URIs, and the default Comunica link traversal engine setup is used.
* [**Link Traversal over Solid with Bloom Filters**](experiments/ltqp-solid-bloom-filters/), to explore the use of Bloom filters to remove unnecessary links during link traversal over Solid pods. The purpose of this experiment is to establish an understanding of whether Bloom filters could be beneficial in pruning links during traversal, specifically within the context of Solid pods.
* [**Link Traversal over Solid with Join Plan Restarts**](experiments/ltqp-solid-join-restart/), to evaluate the impact of restarting most of the query plan upon cardinality estimate updates. The purpose of this experiment is to underline the importance of client-side adaptive techniques in improving query execution, even within link traversal scenarios.

## Results

The results for the experiments are provided in the results directory,
and the scripts used to generate figures and summaries in the scripts directory.
The diefficiency metrics used in the result analysis is calculated as trapezoidal integral,
using the result arrival times as x-axis and result counts as y-axis.

To collect the combination output from a specific experiment after running it:

```bash
python scripts/cli.py collect experiments/example-experiment
```

To generate the analysis for a specific experiment:

```bash
python scripts/cli.py analyse results/example-experiment
```

The plots will need further fine-tuning, and exist mostly for reference at the moment.

## Results

The results for the experiments are provided in the results directory,
and the scripts used to generate figures and summaries in the scripts directory.
The diefficiency metrics used in the result analysis is calculated as trapezoidal integral,
using the result arrival times as x-axis and result counts as y-axis.

To generate the analysis for a specific experiment:

```bash
python scripts/tool.py --results results/ltqp-solid-join-restart
```

The plots will need further fine-tuning, and exist mostly for reference at the moment.

## Running

After cloning the repository, install dependencies with [Yarn](https://github.com/yarnpkg/berry):

```bash
yarn install --immutable
```

Each experiment can then be prepared and executed using `jbr` in the experiment directory:

```bash
yarn run prepare
yarn run validate
yarn run execute
```

## Issues

Please feel free to report any issues on the GitHub issue tracker.

## License

The experiments here are copyrighted and released under the [CC-BY-4.0 license](https://creativecommons.org/licenses/by/4.0/).
