"""Helper utilities for managing jbr.js stats information."""

from io import TextIOWrapper
from csv import DictReader
from typing import Set
from typing import Iterable
from pathlib import Path
from logging import debug
from os.path import splitext
from tarfile import open as open_tarfile

from numpy import array
from numpy import float64
from numpy.typing import NDArray

STATS_FILENAME = "stats.tar.xz"
STATS_EXTENSION = ".csv"

# Helpers for calculations
MB_BYTES = 1024
GB_BYTES = MB_BYTES**3

class JbrStats:
    """
    The aggregate statistics collected by jbr.js, that cannot be split by query,
    because they are not recorded by query.
    """

    def __init__(
        self,
        combination: str,
        container: str,
        cpu_percent: Iterable[float],
        mem_bytes: Iterable[float],
        net_rx_bytes: Iterable[float],
        net_tx_bytes: Iterable[float],
    ) -> None:
        self.combination = combination
        self.container = container
        self.cpu_percent: NDArray[float64] = array(cpu_percent)
        self.cpu_seconds_percent = sum(cpu_percent)
        self.mem_bytes: NDArray[float64] = array(mem_bytes)
        self.gigabyte_seconds = sum(mem_bytes) / GB_BYTES
        self.net_rx_bytes: NDArray[float64] = array(net_rx_bytes)
        self.gigabytes_inbound = sum(net_rx_bytes) / GB_BYTES
        self.net_tx_bytes: NDArray[float64] = array(net_tx_bytes)
        self.gigabytes_outbound = sum(net_tx_bytes) / GB_BYTES


def parse_jbr_stats(path: Path) -> Iterable[JbrStats]:
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
                        bytes_rx.append(bytes_in)
                        bytes_tx.append(bytes_out)
                    else:
                        bytes_rx.append(bytes_in - bytes_in_prev)
                        bytes_tx.append(bytes_out - bytes_out_prev)
                    bytes_in_prev = bytes_in
                    bytes_out_prev = bytes_out
                stats.add(
                    JbrStats(
                        combination=combination_path.name,
                        container=name.removeprefix("stats-"),
                        cpu_percent=cpu_usage_percent,
                        mem_bytes=bytes_mem,
                        net_rx_bytes=bytes_rx,
                        net_tx_bytes=bytes_tx,
                    )
                )

    return stats
