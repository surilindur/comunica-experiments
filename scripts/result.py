"""Representation of benchmark results."""

from csv import DictReader
from typing import Set
from typing import Dict
from typing import List
from typing import Iterable
from logging import info
from logging import warning
from pathlib import Path

from numpy import mean

from utils import parse_timestamps

RESULT_DELIMITER = ";"  # The CSV file delimiter used by sparql-benchmark-runner.js
TIMESTAMP_DELIMITER = " "  # The CSV file timestamp delimiter
QUERY_TIMES_FILE = "query-times.csv"

ERROR_EXPLANATION_MAP: Dict[str, str | None] = {
    "Result hash inconsistency": "inconsistent results",
    'Unexpected "!" at position 0 in state STOP': "timeout",
}


class BenchmarkResult:
    """Representation of a sparql-benchmark-runner.js row for a template instance."""

    def __init__(self, combination: str, row: Dict[str, str]) -> None:
        self.combination = combination
        self.template = row["name"]
        self.instance = row["id"]
        t_min, t_avg, t_max, dieff_raw = (
            parse_timestamps(row["timestampsAll"])
            if row["timestampsAll"]
            else ([], [], [], [0])
        )
        self.timestamps_avg = list(t / 1000 for t in t_avg)
        self.timestamps_min = list(t / 1000 for t in t_min)
        self.timestamps_max = list(t / 1000 for t in t_max)
        self.diefficiency_avg = mean(dieff_raw)
        self.diefficiency_max = max(dieff_raw)
        self.diefficiency_min = min(dieff_raw)
        self.error = (
            ERROR_EXPLANATION_MAP.get(row["errorDescription"], "unknown")
            if row["error"] == "true"
            else None
        )
        self.replication = int(row["replication"])
        self.http_requests_min = float(row["httpRequestsMin"] or "0")
        self.http_requests_max = float(row["httpRequestsMax"] or "0")
        self.http_requests_avg = float(row["httpRequests"] or "0")
        self.durations = list(
            float(d) / 1000 if d.isdigit() else 0
            for d in row["times"].split(TIMESTAMP_DELIMITER)
        )

    @property
    def name(self) -> str:
        return f"{" ".join(self.template.split("-"))}.{self.instance}"

    @property
    def result_count(self) -> int:
        return len(self.timestamps_avg)

    @property
    def duration_avg(self) -> float:
        return sum(self.durations) / len(self.durations)

    @property
    def duration_min(self) -> float:
        return min(self.durations)

    @property
    def duration_max(self) -> float:
        return max(self.durations)


class AggregateResult:
    """Representation of results for a single combination in an experiment."""

    def __init__(self, name: str, results: Iterable[BenchmarkResult]) -> None:
        self.name = name
        self.queries_total = len(results)
        self.queries_succeeded = sum(0 if r.error else 1 for r in results)
        self.diefficiency_avg = sum(r.diefficiency_avg for r in results)
        self.diefficiency_max = sum(r.diefficiency_max for r in results)
        self.diefficiency_min = sum(r.diefficiency_min for r in results)
        self.http_requests_avg = sum(r.http_requests_avg for r in results)
        self.http_requests_max = sum(r.http_requests_max for r in results)
        self.http_requests_min = sum(r.http_requests_min for r in results)
        self.duration_avg = sum(r.duration_avg for r in results)
        self.duration_max = sum(r.duration_max for r in results)
        self.duration_min = sum(r.duration_min for r in results)


def load_combination_results(path: Path) -> Dict[str, Iterable[BenchmarkResult]]:
    """Parses raw query results for all combinations in the specified path."""

    info(f"Loading combinations from {path}")

    results: Dict[str, Iterable[BenchmarkResult]] = {}
    failed_queries: Set[str] = set()

    for combination_path in (p for p in path.iterdir() if p.is_dir()):
        csv_path = combination_path.joinpath(QUERY_TIMES_FILE)
        if csv_path.exists() and csv_path.is_file():
            info(f"Loading {csv_path}")
            combination_results: List[BenchmarkResult] = []
            with open(csv_path, "r") as csv_file:
                reader = DictReader(csv_file, delimiter=RESULT_DELIMITER)
                for row in reader:
                    result = BenchmarkResult(
                        combination=combination_path.name,
                        row=row,
                    )
                    if result.error or result.result_count < 1:
                        failed_queries.add(result.name)
                    combination_results.append(result)
            results[combination_path.name] = combination_results

    warning(f"Found {len(failed_queries)} failed queries")

    for combination_name in results.keys():
        filtered_results = list(
            r for r in results[combination_name] if r.name not in failed_queries
        )
        removed_count = len(results[combination_name]) - len(filtered_results)
        if removed_count > 0:
            warning(f"Ignoring {removed_count} failed queries from {combination_name}")
            results[combination_name] = filtered_results

    info(f"Loaded results for {len(results)} combinations")

    return results


def load_combination_summaries(path: Path) -> Iterable[AggregateResult]:
    """Parses query results and provides a per-combination summary."""

    info(f"Loading per-combination results from {path}")

    results: List[AggregateResult] = []

    for combination_name, combination_results in load_combination_results(path).items():
        results.append(
            AggregateResult(
                name=combination_name,
                results=combination_results,
            )
        )

    info(f"Resolved to {len(results)} combination summaries")

    return results
