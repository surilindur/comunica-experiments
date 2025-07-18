"""Helper classes and functions for parsing jbr.js results into processable entities."""

from csv import DictReader
from json import loads
from typing import Set
from typing import Dict
from logging import debug
from logging import warning
from pathlib import Path

from numpy import array
from numpy import float64
from numpy.typing import NDArray

RESULT_FILENAME = "query-times.csv"
RESULT_DELIMITER = ";"  # The CSV file delimiter used by sparql-benchmark-runner.js
TIMESTAMP_DELIMITER = " "  # The CSV file timestamp delimiter


class JbrQuery:
    """Representation of a single result row from sparql-benchmark-runner.js results."""

    def __init__(self, combination: str, row: Dict[str, str]) -> None:
        self.combination = combination
        self.template = row["name"]
        self.instance = row["id"]
        self.failed = True  # assumes failed, unless proven otherwise
        self.timestamps: NDArray[float64] = array([])
        self.replication = int(row.get("replication", "") or "1")
        if row.get("timestampsAll"):
            # parse the new query runner format file
            try:
                self.timestamps = array(
                    [[t / 1000 for t in t_r] for t_r in loads(row["timestampsAll"])]
                )
            except ValueError as ex:
                assert "inhomogeneous shape after 1" in str(ex)
        elif row.get("timestamps"):
            # parse old query runner timestamps format
            csv_timestamps = list(
                float(t) / 1000 for t in row["timestamps"].split(TIMESTAMP_DELIMITER)
            )
            csv_timestamps.sort()
            self.timestamps = array([csv_timestamps])
        self.failed = len(self.timestamps.shape) < 2 or self.timestamps.shape[1] < 1
        self.duration_avg = float(row.get("time") or "0") / 1000
        row_time_min = row.get("timeMin")
        self.duration_min = (
            float(row_time_min) / 1000 if row_time_min else self.duration_avg
        )
        row_time_max = row.get("timeMax")
        self.duration_max = (
            float(row_time_max) / 1000 if row_time_max else self.duration_avg
        )
        self.results_avg = float(row.get("results") or "0")
        row_results_min = row.get("resultsMin")
        self.results_min = (
            float(row_results_min) if row_results_min else self.results_avg
        )
        row_results_max = row.get("resultsMax")
        self.results_max = (
            float(row_results_max) if row_results_max else self.results_avg
        )
        self.http_requests_avg = float(row["httpRequests"] or "0")
        self.http_requests_min = (
            float(row["httpRequestsMin"] or "0")
            if "httpRequestsMin" in row
            else self.http_requests_avg
        )
        self.http_requests_max = (
            float(row["httpRequestsMax"] or "0")
            if "httpRequestsMax" in row
            else self.http_requests_avg
        )
        if not self.failed and row["error"] == "true":
            warning(
                f"Accepting failed query {self.name} with error {row.get("errorDescription")}"
            )

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, JbrQuery)
            and value.combination == self.combination
            and value.name == self.name
        )

    @property
    def name(self) -> str:
        return f"{self.template}-{self.instance}"


def parse_jbr_csv(path: Path) -> Set[JbrQuery]:
    """Parses the given query-times.csv into a set of result abstractions."""

    queries: Set[JbrQuery] = set()

    with open(path, "r") as results_file:
        reader = DictReader(results_file, delimiter=RESULT_DELIMITER)
        for row in reader:
            query = JbrQuery(combination=path.parent.name, row=row)
            queries.add(query)

    return queries


def parse_jbr_queries(path: Path, ignore_failed=True) -> Set[JbrQuery]:
    """Parses all combinations under the specified path."""

    queries: Set[JbrQuery] = set()
    failed_names: Set[str] = set()

    for combination_path in (p for p in path.iterdir() if p.is_dir()):
        csv_path = combination_path.joinpath(RESULT_FILENAME)
        if csv_path.exists() and csv_path.is_file():
            debug(f"Loading queries from {csv_path}")
            for query in parse_jbr_csv(path=csv_path):
                if query.failed:
                    failed_names.add(query.name)
                queries.add(query)

    if failed_names and ignore_failed:
        warning(f"Excluding {len(failed_names)} failed query instantiations")
        return set(q for q in queries if q.name not in failed_names)

    return queries
