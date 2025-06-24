"""Functions for analysing the data and creating aggregations."""

from typing import Tuple
from typing import List
from typing import Sequence

from statistics import NormalDist

from numpy import array
from numpy import minimum
from numpy import maximum
from numpy import interp
from numpy import arange
from numpy import trapezoid
from numpy import float64
from numpy.typing import NDArray


def resample_timestamps(
    timestamps: NDArray[float64],
    start=0,
    stop=100,
    step=1,
) -> NDArray[float64]:
    """Resamples all timestamps to the range [0, 99] to represent relative times."""

    y = arange(start=start, stop=stop, step=step)
    output = array(
        [interp(x=y, xp=arange(start=0, stop=len(t)), fp=t) for t in timestamps]
    )

    assert (
        output.shape[0] == timestamps.shape[0] and output.shape[1] == stop - start
    ), "Resampling produced mismatched lengths"

    return output


def calculate_confidence_interval(
    data: NDArray[float64],
    confidence=0.95,
) -> Tuple[NDArray[float64], NDArray[float64]]:
    """Calculates the confidence interval."""

    confidence_min: List[float] = []
    confidence_max: List[float] = []

    assert all(
        len(data[i]) == len(data[i - 1]) for i in range(1, len(data))
    ), "Attempting to calculate confidence for mismatched arrays"

    for i in range(0, len(data[0])):
        samples = [data[n][i] for n in range(0, len(data))]
        dist = NormalDist.from_samples(data=samples)
        z = NormalDist().inv_cdf((1 + confidence) / 2.0)
        h = dist.stdev * z / ((len(data) - 1) ** 0.5)
        confidence_min.append(dist.mean - h)
        confidence_max.append(dist.mean + h)

    assert (
        len(confidence_min) == len(confidence_max) == len(data[0])
    ), "Mismatched confidence lengths"

    return array(confidence_min), array(confidence_max)


def calculate_diefficiency_at_full_results(timestamps: NDArray[float64]) -> float:
    """
    Calculates the *dieff@k* metric when k is set to the total number of results.
    This is done using a trapezoidal integral, so that queries producing only one
    result can also have a different metric value from each other.
    """

    assert len(timestamps.shape) == 1 and timestamps.shape[0] > 0

    x = array([0, *timestamps])
    y = arange(start=0, stop=timestamps.shape[0] + 1)

    return trapezoid(y=y, x=x)


def calculate_aggregate_completeness_curve(
    timestamps: NDArray[float64],
) -> Tuple[NDArray[float64], NDArray[float64], NDArray[float64]]:
    """
    Resamples result arrival timestamps to [0, 99] and aggregates them.
    This enables the aggregation of results with different time axis.
    The return value is a Tuple[t_min, t_avg, t_max, t_count].
    """

    t_min = array([])
    t_max = array([])
    t_sum = array([])

    for t_resampled in resample_timestamps(timestamps=timestamps):
        if t_min.size > 0:
            t_min = minimum(t_min, t_resampled)
            t_max = maximum(t_max, t_resampled)
            t_sum += t_resampled
        else:
            t_min = t_resampled
            t_max = t_resampled
            t_sum = t_resampled

    return (t_min, t_sum / len(timestamps), t_max)
