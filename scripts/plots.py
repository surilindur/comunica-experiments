from io import BytesIO
from typing import Dict
from typing import Iterable
from logging import info
from itertools import groupby

from matplotlib import rcParams
from matplotlib.pyplot import style
from matplotlib.pyplot import figure
from matplotlib.pyplot import close
from matplotlib.pyplot import subplots
from matplotlib.ticker import ScalarFormatter

from result import BenchmarkResult
from utils import sort_labels

IMAGE_DPI = 600
IMAGE_EXT = "svg"

rcParams["font.family"] = "serif"


def plot_http_requests(combinations: Dict[str, Iterable[BenchmarkResult]]) -> BytesIO:
    """Create an illustration of the HTTP request count per combination."""

    info(f"Plotting HTTP request count for {len(combinations)} combinations")

    fig, axes = subplots(
        figsize=(6, 3 * (len(combinations) / 10)),
        layout="constrained",
    )

    stats = []

    for combination_name in sort_labels(combinations.keys())[::-1]:
        combination_results = combinations[combination_name]
        http_sum_avg = sum(r.http_requests_avg for r in combination_results)
        http_sum_min = sum(r.http_requests_min for r in combination_results)
        http_sum_max = sum(r.http_requests_max for r in combination_results)
        stats.append(
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

    axes.bxp(
        stats,
        widths=0.5,
        vert=False,
        patch_artist=True,
        showbox=False,
        showmeans=False,
        capprops=dict(color="lightgrey"),
        whiskerprops=dict(color="lightgrey"),
    )

    style.use("seaborn-v0_8-colorblind")

    axes.spines["top"].set_visible(False)
    axes.spines["right"].set_visible(False)
    axes.spines["bottom"].set_visible(False)
    axes.spines["left"].set_visible(False)

    formatter_scientific = ScalarFormatter()
    formatter_scientific.set_scientific(True)
    formatter_scientific.set_powerlimits((1, 20))

    axes.xaxis.set_major_formatter(formatter=formatter_scientific)
    axes.xaxis.set_label_text("cumulative HTTP requests", style="italic")

    axes.set_xlim(left=0)

    info(f"Saving image as {IMAGE_EXT} to in-memory buffer")
    bytes_io = BytesIO()
    fig.savefig(fname=bytes_io, format=IMAGE_EXT, dpi=IMAGE_DPI)
    close(fig)
    bytes_io.seek(0)

    return bytes_io


def plot_dieff_metrics(combinations: Dict[str, Iterable[BenchmarkResult]]) -> BytesIO:
    """Create an illustration of the diefficiency metric per combination."""

    info(f"Plotting diefficiency for {len(combinations)} combinations")

    fig = figure(
        figsize=(12, 3 * (len(combinations) / 10)),
        layout="constrained",
    )

    axes_diefficiency = fig.add_subplot(121)
    axes_duration = fig.add_subplot(122, sharey=axes_diefficiency)

    stats_diefficiency = []
    stats_duration = []

    for combination_name in sort_labels(combinations.keys())[::-1]:
        combination_results = combinations[combination_name]
        # Diefficiency
        diefficiency_sum_avg = sum(r.diefficiency_avg for r in combination_results)
        diefficiency_sum_max = sum(r.diefficiency_max for r in combination_results)
        diefficiency_sum_min = sum(r.diefficiency_min for r in combination_results)
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
        duration_sum_avg = sum(r.duration_avg for r in combination_results)
        duration_sum_max = sum(r.duration_max for r in combination_results)
        duration_sum_min = sum(r.duration_min for r in combination_results)
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

    axes_diefficiency.yaxis.set_tick_params(
        length=0,
        labelright=True,
        labelleft=False,
        pad=60,
    )

    for tick in axes_diefficiency.yaxis.get_majorticklabels():
        tick.set_horizontalalignment("center")

    axes_diefficiency.xaxis.set_major_formatter(formatter_scientific)
    axes_diefficiency.xaxis.set_inverted(True)
    axes_diefficiency.xaxis.set_label_text("cumulative dieff@full", style="italic")

    axes_duration.yaxis.set_visible(False)

    axes_duration.xaxis.set_label_text("cumulative query duration (s)", style="italic")

    info(f"Saving image as {IMAGE_EXT} to in-memory buffer")
    bytes_io = BytesIO()
    fig.savefig(fname=bytes_io, format=IMAGE_EXT, dpi=IMAGE_DPI)
    close(fig)
    bytes_io.seek(0)

    return bytes_io
