"""Functions for analysing the data and creating aggregations."""

from typing import Sequence

from numpy import ndarray
from numpy import minimum
from numpy import maximum
from numpy import interp
from numpy import arange


class AggregateTimestamps:

    def __init__(
        self,
        t_min: ndarray,
        t_max: ndarray,
        t_avg: ndarray,
        t_count: int,
    ) -> None:
        self.t_min = t_min
        self.t_max = t_max
        self.t_avg = t_avg
        self.t_count = t_count


def calculate_aggregate_completeness_curve(
    timestamps: Sequence[Sequence[float]],
) -> AggregateTimestamps:
    """
    Resamples result arrival timestamps to [0, 99] and aggregates them.
    This enables the aggregation of results with different time axis.
    """

    t_count = 100
    t_min = ndarray((0, 0))
    t_max = ndarray((0, 0))
    t_sum = ndarray((0, 0))

    y = arange(t_count)

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

    return AggregateTimestamps(
        t_min=t_min,
        t_max=t_max,
        t_avg=t_sum / len(timestamps),
        t_count=t_count,
    )
