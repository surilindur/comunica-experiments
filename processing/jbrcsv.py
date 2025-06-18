"""Helper classes and functions for parsing jbr.js results into processable entities."""

from io import TextIOWrapper
from csv import DictReader
from json import loads
from typing import Set
from typing import Dict
from typing import Sequence
from typing import Iterable
from logging import debug
from logging import warning
from pathlib import Path
from os.path import splitext
from tarfile import open as open_tarfile

RESULT_FILENAME = "query-times.csv"
RESULT_DELIMITER = ";"  # The CSV file delimiter used by sparql-benchmark-runner.js
TIMESTAMP_DELIMITER = " "  # The CSV file timestamp delimiter
STATS_FILENAME = "stats.tar.xz"
STATS_EXTENSION = ".csv"
GB_BYTES = 1024**3


class JbrQuery:
    """Representation of a single result row from sparql-benchmark-runner.js results."""

    def __init__(self, combination: str, row: Dict[str, str]) -> None:
        self.combination = combination
        self.template = row["name"]
        self.instance = row["id"]
        self.replication = int(row["replication"])
        self.timestamps: Sequence[Sequence[float]] = loads(row["timestampsAll"])
        self.durations: Sequence[float] = list(
            float(d) / 1000
            for d in row["times"].split(TIMESTAMP_DELIMITER)
            if d.isdigit()
        )
        self.duration_avg = float(row["time"])
        self.duration_min = float(row["timeMin"])
        self.duration_max = float(row["timeMax"])
        self.results_avg = float(row["results"])
        self.results_min = float(row["resultsMin"])
        self.results_max = float(row["resultsMax"])
        self.http_requests_avg = float(row["httpRequests"] or "0")
        self.http_requests_min = float(row["httpRequestsMin"] or "0")
        self.http_requests_max = float(row["httpRequestsMax"] or "0")
        self.failed = row["error"] == "true" and "hash" not in row["errorDescription"]
        self.error = row["errorDescription"]

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


class JbrStats:
    """
    The aggregate statistics collected by jbr.js, that cannot be split by query,
    because they are not recorded by query.
    """

    def __init__(
        self,
        container: str,
        cpu_percent: Iterable[float],
        mem_bytes: Iterable[float],
        net_rx_bytes: Iterable[float],
        net_tx_bytes: Iterable[float],
    ) -> None:
        self.container = container
        self.cpu_percent = cpu_percent
        self.cpu_seconds_percent = sum(cpu_percent)
        self.mem_bytes = mem_bytes
        self.gigabyte_seconds = sum(mem_bytes) / GB_BYTES
        self.net_rx_bytes = net_rx_bytes
        self.gigabytes_inbound = sum(net_rx_bytes) / GB_BYTES
        self.net_tx_bytes = net_tx_bytes
        self.gigabytes_outbound = sum(net_tx_bytes) / GB_BYTES


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


def parse_jbr_stats(path: Path) -> Set[JbrStats]:
    """Parses the resource consumption statistics for the specificed combination."""

    stats: Set[JbrStats] = set()

    for combination_path in (p for p in path.iterdir() if p.is_dir()):
        stats_path = combination_path.joinpath(STATS_FILENAME)
        debug(f"Parsing container resource statistics from {stats_path}")
        with open_tarfile(stats_path, "r:xz") as tar_file:
            for file_info in tar_file:
                name, ext = splitext(file_info.name)
                if ext != STATS_EXTENSION:
                    debug(f"Skipping {file_info.name}")
                    continue
                stats_file = tar_file.extractfile(member=file_info)
                assert stats_file, f"Failed to extract {file_info.name}"
                stats_text = TextIOWrapper(stats_file)
                reader = DictReader(f=stats_text, delimiter=",")
                cpu_usage_percent = []
                bytes_mem = []
                bytes_rx = []
                bytes_tx = []
                bytes_in_prev = -1
                bytes_out_prev = -1
                for row in reader:
                    cpu_usage_percent.append(float(row["cpu_percentage"]))
                    bytes_mem.append(int(row["memory"]))
                    bytes_in = int(row["received"])
                    bytes_out = int(row["transmitted"])
                    if bytes_in_prev < 0:
                        bytes_rx.append(bytes_in - bytes_in_prev)
                        bytes_tx.append(bytes_out - bytes_out_prev)
                    else:
                        bytes_rx.append(bytes_in)
                        bytes_tx.append(bytes_out)
                    bytes_in_prev = bytes_in
                    bytes_out_prev = bytes_out
                stats.add(
                    JbrStats(
                        container=name.removeprefix("stats-"),
                        cpu_percent=cpu_usage_percent,
                        mem_bytes=bytes_mem,
                        net_rx_bytes=bytes_rx,
                        net_tx_bytes=bytes_tx,
                    )
                )

    return stats
