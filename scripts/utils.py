from json import loads
from typing import Tuple
from typing import Sequence
from typing import Iterable

from natsort import natsorted

from numpy import trapezoid
from numpy import array
from numpy.typing import NDArray


def sort_labels(values: Iterable[str]) -> Sequence[str]:
    """Sorts labels in a way that makes sense."""

    values_sorted = natsorted(values)

    if "baseline" in values_sorted and "overhead" in values_sorted:
        values_sorted.remove("baseline")
        values_sorted.remove("overhead")
        values_sorted.insert(0, "overhead")
        values_sorted.insert(0, "baseline")

    return values_sorted


def parse_timestamps(
    timestamps_all: str,
) -> Tuple[NDArray, NDArray, NDArray, NDArray]:
    """Parses the all timestamps field from CSV and calculates the minimum and maximum."""

    timestamps_min: Sequence[float] = []
    timestamps_max: Sequence[float] = []
    timestamps_sum: Sequence[float] = []
    diefficiencies: Sequence[float] = []

    if timestamps_all:
        replications: Sequence[Sequence[float]] = loads(timestamps_all)

        for replication in replications:
            for i in range(0, len(replication)):
                if len(timestamps_sum) > i:
                    timestamps_sum[i] += replication[i]
                    timestamps_min[i] = min(timestamps_min[i], replication[i])
                    timestamps_max[i] = max(timestamps_max[i], replication[i])
                else:
                    timestamps_sum.append(replication[i])
                    timestamps_min.append(replication[i])
                    timestamps_max.append(replication[i])
            y = list(range(0, len(replication) + 1))
            x = [0, *replication]
            diefficiencies.append(trapezoid(y=y, x=x))

        # Ensure the timestamps are sorted
        timestamps_min.sort()
        timestamps_max.sort()
        timestamps_avg = list(sorted(t / len(replications) for t in timestamps_sum))
    else:
        timestamps_avg = []

    return (
        array(timestamps_min),
        array(timestamps_avg),
        array(timestamps_max),
        array(diefficiencies),
    )
