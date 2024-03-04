<p align="center">
  <a href="https://comunica.dev/">
    <img alt="Comunica" src="https://comunica.dev/img/comunica_red.svg" width="200">
  </a>
</p>

<p align="center">
  <strong>Work-in-Progress Experiments for Comunica</strong>
</p>

<p align="center">
  <a href="https://github.com/surilindur/comunica-experiments/actions/workflows/ci.yml">
    <img alt="CI" src=https://github.com/surilindur/comunica-experiments/actions/workflows/ci.yml/badge.svg?branch=main">
  </a>
</p>

This is a monorepository that contains various work-in-progress experiments for [Comunica](https://github.com/comunica/comunica) using [jbr.js](https://github.com/rubensworks/jbr.js). The experiments here are meant for benchmarking different ideas in a reproducible way. The following experiments reside here:

* [**Restarting of joins during link traversal over Solid pods**](experiments/ltqp-solid-join-restart/).
* [**Pruning of links during link traversal over Solid pods**](experiments/ltqp-solid-bloom-filters/).

## Running

The project can be cloned, after which the dependencies can be installed using Yarn with:

```bash
yarn install --immutable
```

The experiments each have their own readme files that clarify how to run them.

## Issues

Please feel free to report any issues on the GitHub issue tracker, but do note that there are only experiments are therefore not of actual use.

## License

The experiments here are copyrighted by [Ghent University – imec](http://idlab.ugent.be/) and released under the [CC-BY-4.0 license](https://creativecommons.org/licenses/by/4.0/).
