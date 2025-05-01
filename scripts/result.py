"""Representation of benchmark results."""

from csv import DictReader
from typing import Dict
from typing import Iterable
from typing import Sequence
from pathlib import Path

from numpy import trapezoid
from numpy import array

from utils import parse_timestamps

RESULT_DELIMITER = ";"  # The CSV file delimiter used by sparql-benchmark-runner.js
TIMESTAMP_DELIMITER = " "  # The CSV file timestamp delimiter

ERROR_EXPLANATION_MAP: Dict[str, str | None] = {
    "Result hash inconsistency": "inconsistent results",
    'Unexpected "!" at position 0 in state STOP': "timeout",
}


class BenchmarkResult:
    """Representation of a sparql-benchmark-runner.js row for a template instance."""

    template: str
    instance: str
    combination: str

    replication: int
    error: str | None

    durations: Sequence[float]

    http_avg: float
    http_min: float
    http_max: float

    timestamps: Sequence[float]
    timestamps_min: Sequence[float]
    timestamps_max: Sequence[float]

    def __init__(self, combination: str, row: Dict[str, str]) -> None:
        self.combination = combination
        self.template = row["name"]
        self.instance = row["id"]
        t_min, t_avg, t_max = (
            parse_timestamps(row["timestampsAll"])
            if row["timestampsAll"]
            else ([], [], [])
        )
        self.timestamps = list(t / 1000 for t in t_avg)
        self.timestamps_min = list(t / 1000 for t in t_min)
        self.timestamps_max = list(t / 1000 for t in t_max)
        self.error = (
            ERROR_EXPLANATION_MAP.get(row["errorDescription"], "unknown")
            if row["error"] == "true"
            else None
        )
        self.replication = int(row["replication"])
        self.http_min = float(row["httpRequestsMin"] or "0")
        self.http_max = float(row["httpRequestsMax"] or "0")
        self.http_avg = float(row["httpRequests"] or "0")
        self.durations = list(
            float(d) / 1000 if d.isdigit() else 0
            for d in row["times"].split(TIMESTAMP_DELIMITER)
        )

    @property
    def results(self) -> int:
        return len(self.timestamps)

    @property
    def failed(self) -> bool:
        return self.error is not None

    @property
    def name(self) -> str:
        return f"{" ".join(self.template.split("-"))}.{self.instance}"

    @property
    def diefficiency(self) -> float:
        """Calculate the diefficiency metric as trapezoidal integral."""
        x = array([0, *self.timestamps])
        y = array(range(0, x.size))
        return trapezoid(y=y, x=x)

    @property
    def diefficiency_min(self) -> float:
        """Calculate the minimum diefficiency metric as trapezoidal integral."""
        x = array([0, *self.timestamps_min])
        y = array(range(0, x.size))
        return trapezoid(y=y, x=x)

    @property
    def diefficiency_max(self) -> float:
        """Calculate the maximum diefficiency metric as trapezoidal integral."""
        x = array([0, *self.timestamps_max])
        y = array(range(0, x.size))
        return trapezoid(y=y, x=x)

    @property
    def duration(self) -> float:
        return sum(self.durations) / len(self.durations)

    @property
    def duration_min(self) -> float:
        return min(self.durations)

    @property
    def duration_max(self) -> float:
        return max(self.durations)


def load_results_file(path: Path) -> Iterable[BenchmarkResult]:
    """Process a query-results.csv file dumped by the runner."""

    results: Sequence[BenchmarkResult] = []

    with open(path, "r") as csv_file:
        reader = DictReader(csv_file, delimiter=RESULT_DELIMITER)
        for row in reader:
            results.append(BenchmarkResult(path.parent.name, row))

    return results
