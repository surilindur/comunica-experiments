# Solid Join Restart with Chronomunica

This is an experiment for measuring the impact of using predicate counts to estimate triple pattern cardinalities while performing Link Traversal Query Processing (LTQP) over Solid pods using [Chronomunica](https://github.com/surilindur/chronomunica) and [SolidBench.js](https://github.com/SolidBench/SolidBench.js). The engine implementation is taken from a set of [work-in-progress Comunica components](https://github.com/surilindur/comunica-components).

The provided [script](./experiment.sh) can be used to execute the experiment, provided that the dependencies are met. The results will go into the `output/` folder.
