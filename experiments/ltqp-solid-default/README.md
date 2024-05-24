# Solid Bloom Filters

This is an experimental experiment for measuring the impact of using Bloom filters to prune links during link traversal over Solid pods. The experiment uses the following components to function:

* [jbr](https://github.com/rubensworks/jbr.js) as the benchmark runner
* [SolidBench.js](https://github.com/SolidBench/SolidBench.js) as the benchmark itself
* [Comunica components](https://github.com/surilindur/comunica-components) to implement the parsing and use of Bloom filters

The provided [script](./experiment.sh) contains the commands used to execute the experiment, together with their explanations.
The results will be produced in the `output` folder.
