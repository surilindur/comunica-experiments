from io import BytesIO
from typing import Dict
from typing import Iterable
from logging import info

from matplotlib import rcParams
from matplotlib.pyplot import style
from matplotlib.pyplot import figure
from matplotlib.pyplot import close
from matplotlib.pyplot import subplots
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import ScalarFormatter

from result import BenchmarkResult
from result import CombinationContainerStats
from utils import sort_labels

IMAGE_DPI = 600
IMAGE_EXT = "svg"

rcParams["font.family"] = "Noto Serif"


def plot_network_metrics(
    combination_results: Dict[str, Iterable[BenchmarkResult]],
    combination_stats: Dict[str, Iterable[CombinationContainerStats]],
) -> BytesIO:
    """Create an illustration of the HTTP request count and GB per combination."""

    info(f"Plotting network metrics for {len(combination_results)} combinations")

    fig = figure(
        figsize=(12, 3 * (len(combination_results) / 10)),
        layout="constrained",
    )

    axes_requests = fig.add_subplot(121)
    axes_traffic = fig.add_subplot(122, sharey=axes_requests)

    stats_requests = []
    values_gb_downloaded = []
    values_gb_uploaded = []

    for combination_name in sort_labels(combination_results.keys())[::-1]:
        results = combination_results[combination_name]
        http_sum_avg = sum(r.http_requests_avg for r in results)
        http_sum_min = sum(r.http_requests_min for r in results)
        http_sum_max = sum(r.http_requests_max for r in results)
        stats_requests.append(
            dict(
                med=http_sum_avg,
                q1=http_sum_avg,
                q3=http_sum_avg,
                whislo=http_sum_min,
                whishi=http_sum_max,
                fliers=[],
                label=combination_name,
            )
        )

        stats = (
            s for s in combination_stats[combination_name] if s.container == "server"
        )
        values_gb_uploaded.append(sum(s.gigabytes_outbound for s in stats))
        values_gb_downloaded.append(sum(s.gigabytes_inbound for s in stats))

    axes_requests.bxp(
        stats_requests,
        widths=0.5,
        vert=False,
        patch_artist=True,
        showbox=False,
        showmeans=False,
        capprops=dict(color="lightgrey"),
        whiskerprops=dict(color="lightgrey"),
    )

    y = list(range(1, len(combination_results) + 1))
    # axes_traffic.plot(values_gb_downloaded, y, ".")
    axes_traffic.plot(values_gb_uploaded, y, ".")

    style.use("seaborn-v0_8-colorblind")

    for ax in (axes_requests, axes_traffic):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.set_xlim(left=0)

    formatter_thousands = FuncFormatter(lambda x, p: format(int(x), ","))

    axes_requests.set_xlabel("Total HTTP requests", labelpad=10, style="italic")
    axes_requests.xaxis.set_inverted(True)
    axes_requests.xaxis.set_major_formatter(formatter=formatter_thousands)
    axes_requests.yaxis.set_tick_params(
        length=0,
        labelright=True,
        labelleft=False,
        pad=60,
    )

    for tick in axes_requests.yaxis.get_ticklabels():
        tick.set_horizontalalignment("center")
        tick.set_fontweight("medium")

    axes_traffic.set_xlabel("Total data transfer (GB)", labelpad=10, style="italic")
    axes_traffic.yaxis.set_visible(False)

    info(f"Saving image as {IMAGE_EXT} to in-memory buffer")
    bytes_io = BytesIO()
    fig.savefig(fname=bytes_io, format=IMAGE_EXT, dpi=IMAGE_DPI)
    close(fig)
    bytes_io.seek(0)

    return bytes_io


def plot_dieff_metrics(
    combination_results: Dict[str, Iterable[BenchmarkResult]],
) -> BytesIO:
    """Create an illustration of the diefficiency metric per combination."""

    info(f"Plotting diefficiency for {len(combination_results)} combinations")

    fig = figure(
        figsize=(12, 3 * (len(combination_results) / 10)),
        layout="constrained",
    )

    axes_diefficiency = fig.add_subplot(121)
    axes_duration = fig.add_subplot(122, sharey=axes_diefficiency)

    stats_diefficiency = []
    stats_duration = []

    for combination_name in sort_labels(combination_results.keys())[::-1]:
        results = combination_results[combination_name]
        # Diefficiency
        diefficiency_sum_avg = sum(r.diefficiency_avg for r in results)
        diefficiency_sum_max = sum(r.diefficiency_max for r in results)
        diefficiency_sum_min = sum(r.diefficiency_min for r in results)
        stats_diefficiency.append(
            dict(
                med=diefficiency_sum_avg,
                q1=diefficiency_sum_avg - 0.5,
                q3=diefficiency_sum_avg + 0.5,
                whislo=diefficiency_sum_min,
                whishi=diefficiency_sum_max,
                fliers=[],
                label=combination_name,
            )
        )
        # Execution time
        duration_sum_avg = sum(r.duration_avg for r in results)
        duration_sum_max = sum(r.duration_max for r in results)
        duration_sum_min = sum(r.duration_min for r in results)
        stats_duration.append(
            dict(
                med=duration_sum_avg,
                q1=duration_sum_avg,
                q3=duration_sum_avg,
                whislo=duration_sum_min,
                whishi=duration_sum_max,
                fliers=[],
                label=combination_name,
            )
        )

    axes_diefficiency.bxp(
        stats_diefficiency,
        widths=0.5,
        vert=False,
        patch_artist=True,
        showbox=False,
        showmeans=False,
        capprops=dict(color="lightgrey"),
        whiskerprops=dict(color="lightgrey"),
    )

    axes_duration.bxp(
        stats_duration,
        widths=0.5,
        vert=False,
        patch_artist=True,
        showbox=False,
        showmeans=False,
        capprops=dict(color="lightgrey"),
        whiskerprops=dict(color="lightgrey"),
    )

    style.use("seaborn-v0_8-colorblind")

    for ax in (axes_diefficiency, axes_duration):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.set_xlim(left=0)

    formatter_scientific = ScalarFormatter()
    formatter_scientific.set_scientific(True)
    formatter_scientific.set_powerlimits((0, 0))

    axes_diefficiency.set_xlabel("Total dieff@full", labelpad=10, style="italic")
    axes_diefficiency.xaxis.set_major_formatter(formatter_scientific)
    axes_diefficiency.xaxis.set_inverted(True)
    axes_diefficiency.yaxis.set_tick_params(
        length=0,
        labelright=True,
        labelleft=False,
        pad=60,
    )

    for tick in axes_diefficiency.yaxis.get_ticklabels():
        tick.set_horizontalalignment("center")
        tick.set_fontweight("medium")

    axes_duration.yaxis.set_visible(False)
    axes_duration.set_xlabel("Total query duration (s)", labelpad=10, style="italic")

    info(f"Saving image as {IMAGE_EXT} to in-memory buffer")
    bytes_io = BytesIO()
    fig.savefig(fname=bytes_io, format=IMAGE_EXT, dpi=IMAGE_DPI)
    close(fig)
    bytes_io.seek(0)

    return bytes_io
