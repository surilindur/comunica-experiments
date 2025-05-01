from json import loads
from typing import Tuple
from typing import Sequence


def parse_timestamps(
    timestamps_all: str,
) -> Tuple[Sequence[float], Sequence[float], Sequence[float]]:
    """Parses the all timestamps field from CSV and calculates the minimum and maximum."""
    timestamps_min: Sequence[float] = []
    timestamps_max: Sequence[float] = []
    timestamps_sum: Sequence[float] = []
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

    # Ensure the timestamps are sorted
    timestamps_min.sort()
    timestamps_max.sort()
    timestamps_avg = list(sorted(t / len(replications) for t in timestamps_sum))

    return (timestamps_min, timestamps_avg, timestamps_max)
