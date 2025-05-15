"""Representation of benchmark results."""

from io import TextIOWrapper
from csv import DictReader
from typing import Set
from typing import Dict
from typing import List
from typing import Iterable
from logging import info
from logging import warning
from pathlib import Path
from os.path import splitext
from tarfile import open as open_tarfile

from numpy import mean

from utils import parse_timestamps

RESULT_DELIMITER = ";"  # The CSV file delimiter used by sparql-benchmark-runner.js
TIMESTAMP_DELIMITER = " "  # The CSV file timestamp delimiter
QUERY_TIMES_FILE = "query-times.csv"
STATS_ZIP_FILE = "stats.tar.xz"
GB_BYTES = 1024**3

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


class CombinationContainerStats:
    """Collection of stats for a given combination."""

    def __init__(
        self,
        container: str,
        cpu_percent: Iterable[float],
        mem_gb: Iterable[float],
        net_rx_gb: Iterable[float],
        net_tx_gb: Iterable[float],
    ) -> None:
        self.container = container
        self.cpu_percent = cpu_percent
        self.cpu_seconds_percent = sum(cpu_percent)
        self.mem_gb = mem_gb
        self.gigabyte_seconds = sum(mem_gb)
        self.net_rx_gb = net_rx_gb
        self.gigabytes_inbound = sum(net_rx_gb)
        self.net_tx_gb = net_tx_gb
        self.gigabytes_outbound = sum(net_tx_gb)


def load_combination_stats(path: Path) -> Dict[str, CombinationContainerStats]:
    """Parses the resource consumption statistics for the specificed combination."""

    stats: Dict[str, List[CombinationContainerStats]] = {}

    for combination_path in (p for p in path.iterdir() if p.is_dir()):
        stats_path = combination_path.joinpath(STATS_ZIP_FILE)
        info(f"Parsing resource stats from {stats_path}")
        stats[combination_path.name] = []
        with open_tarfile(stats_path, "r:xz") as tar_file:
            for file in tar_file:
                name, ext = splitext(file.name)
                if ext == ".csv":
                    with tar_file.extractfile(member=file) as tar_buffer:
                        tar_text = TextIOWrapper(tar_buffer)
                        reader = DictReader(f=tar_text, delimiter=",")
                        cpu_usage_percent = []
                        bytes_mem = []
                        bytes_rx = []
                        bytes_tx = []
                        for row in reader:
                            cpu_usage_percent.append(float(row["cpu_percentage"]))
                            bytes_mem.append(int(row["memory"]))
                            bytes_in = int(row["received"])
                            bytes_out = int(row["transmitted"])
                            if bytes_rx:
                                bytes_rx.append(bytes_in - bytes_rx[-1])
                                bytes_tx.append(bytes_out - bytes_tx[-1])
                            else:
                                bytes_rx.append(bytes_in)
                                bytes_tx.append(bytes_out)
                        stats[combination_path.name].append(
                            CombinationContainerStats(
                                container=name.removeprefix("stats-"),
                                cpu_percent=cpu_usage_percent,
                                mem_gb=list(b / GB_BYTES for b in bytes_mem),
                                net_rx_gb=list(b / GB_BYTES for b in bytes_rx),
                                net_tx_gb=list(b / GB_BYTES for b in bytes_tx),
                            )
                        )

    return stats


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
