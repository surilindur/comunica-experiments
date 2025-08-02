# Wikidata Graph Split

The purpose of this experiment is to evaluate the feasibility of executing the sample set of Wikidata queries
over the [split SPARQL endpoints](https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/WDQS_graph_split).
The experiment consist of set of 14 queries,
with `SERVICE` clause-based source assignment and without it.

* The query engine configuration is found in [input/comunica](input/comunica/).
* The queries with `SERVICE` clauses are in [input/queries-service](input/queries-service/).
* The queries without `SERVICE` clauses are in [input/queries-automatic](input/queries-automatic/).

The experiment results will be placed under [output](output/) after execution.
The current results are found under the results directory at the monorepo level.

## Running

The experiment makes use of [jbr.js](https://github.com/rubensworks/jbr.js),
and after installing the dependencies at the monorepo level,
can be prepared with:

```bash
yarn run prepare
```

The experiment can be executed with:
```bash
yarn run execute
```

The query plans can be generated with:

```bash
yarn run explain
```

## Issues

Please feel free to report any issues at the GitHub issue tracker.
