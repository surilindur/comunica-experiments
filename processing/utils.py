from json import loads
from typing import Sequence
from collections import namedtuple

from natsort import natsorted

from numpy import ndarray
from numpy import minimum
from numpy import maximum
from numpy import interp
from numpy import arange

AggregateTimestamps = namedtuple("AggregateTimestamps", ["min", "max", "avg"])


def sort_labels(values: Sequence[str]) -> Sequence[str]:
    """Sorts labels in a way that makes sense."""

    values_sorted = natsorted(values)

    if "baseline" in values_sorted and "overhead" in values_sorted:
        values_sorted.remove("baseline")
        values_sorted.remove("overhead")
        values_sorted.insert(0, "overhead")
        values_sorted.insert(0, "baseline")

    return values_sorted


def parse_jbr_timestamps_all_column(value: str) -> Sequence[Sequence[float]]:
    """Parses the jbr.js timestampsAll column into numeric values."""

    return loads(value)


def aggregate_result_arrivals(
    timestamps: Sequence[Sequence[float]],
) -> AggregateTimestamps:
    """
    Resamples result arrival timestamps to [0, 99] and aggregates them.
    This enables the aggregation of results with different time axis.
    """

    t_min = ndarray((0, 0))
    t_max = ndarray((0, 0))
    t_sum = ndarray((0, 0))

    y = arange(100)

    for t in timestamps:
        t_y = interp(y, arange(len(t)) + 1, t)
        if t_min.size == 0:
            t_min = minimum(t_min, t_y)
            t_max = maximum(t_max, t_y)
            t_sum += t_y
        else:
            t_min = t_y
            t_max = t_y
            t_sum = t_y

    return AggregateTimestamps(min=t_min, max=t_max, avg=t_sum / len(timestamps))
