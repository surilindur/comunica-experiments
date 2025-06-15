from io import BytesIO
from typing import Dict
from typing import Iterable
from typing import Sequence
from logging import info

from numpy import interp
from numpy import minimum
from numpy import maximum
from numpy.typing import NDArray

from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.pyplot import style
from matplotlib.pyplot import figure
from matplotlib.pyplot import close
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import ScalarFormatter
from matplotlib.pyplot import get_cmap

from result import BenchmarkResult
from result import CombinationContainerStats
from utils import sort_labels

IMAGE_DPI = 600
IMAGE_EXT = "svg"

rcParams["font.family"] = "Noto Serif"


def plot_category_values(
    axes: Axes,
    measurements: Dict[str, Sequence[float]],
    vertical=False,
) -> None:
    """Plot all measurement values as a bar chart-like scatter plot."""

    labels = sort_labels(measurements.keys())

    value_ticks = set()
    label_ticks = []

    for index, label in enumerate(labels):
        label_ticks.append(index)
        values = measurements[label]
        values_count = len(values)
        if values_count < 5:
            value_ticks.update(round(v) for v in values)
        positions = list(index for _ in range(0, values_count))
        if vertical:
            x = positions
            y = values
        else:
            x = values
            y = positions

        axes.plot(x, y, "C0.")

    if vertical:
        axes.set_xticks(ticks=label_ticks, labels=labels)
        if len(value_ticks) == len(labels):
            axes.set_yticks(ticks=list(value_ticks))
    else:
        axes.set_yticks(ticks=label_ticks, labels=labels)
        if len(value_ticks) == len(labels):
            axes.set_xticks(ticks=list(value_ticks))


def plot_network_metrics(
    combination_results: Dict[str, Iterable[BenchmarkResult]],
    combination_stats: Dict[str, Iterable[CombinationContainerStats]],
) -> BytesIO:
    """Create an illustration of the HTTP request count and GB per combination."""

    info(f"Plotting network metrics for {len(combination_results)} combinations")

    fig = figure(
        figsize=(8, 3 * (len(combination_results) / 10)),
        layout="constrained",
    )

    axes_requests = fig.add_subplot(121)
    axes_traffic = fig.add_subplot(122, sharey=axes_requests)

    request_counts: Dict[str, Sequence[float]] = {}
    data_transfer_gb: Dict[str, Sequence[float]] = {}

    for combination_name in sort_labels(combination_results.keys())[::-1]:
        results = combination_results[combination_name]
        request_counts[combination_name] = tuple(r.http_requests_avg for r in results)
        data_transfer_gb[combination_name] = tuple(
            s.gigabytes_outbound
            for s in combination_stats[combination_name]
            if s.container == "server"
        )

    plot_category_values(axes=axes_requests, measurements=request_counts)
    plot_category_values(axes=axes_traffic, measurements=data_transfer_gb)

    # axes_requests.bxp(
    #    stats_requests,
    #    widths=0.5,
    #    vert=False,
    #    patch_artist=True,
    #    showbox=False,
    #    showmeans=False,
    #    capprops=dict(color="lightgrey"),
    #    whiskerprops=dict(color="lightgrey"),
    # )

    y = list(range(1, len(combination_results) + 1))
    # axes_traffic.plot(values_gb_downloaded, y, ".")
    # axes_traffic.plot(values_gb_uploaded, y, ".")

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
    # axes_requests.yaxis.set_major_locator()
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


def plot_result_trends(
    combination_results: Dict[str, Iterable[BenchmarkResult]],
) -> BytesIO:
    """Plot result arrival graphs for all combinations."""

    combination_count = len(combination_results)
    combination_names = sort_labels(combination_results.keys())

    col_count = 5
    row_count = round(combination_count / col_count + 0.5)

    info(f"Plotting result arrival trends for {combination_count} combinations")

    fig = figure(figsize=(col_count * 3.5, row_count * 3), layout="constrained")

    ax_shared = None
    y_max = 0
    y_locator = MaxNLocator(integer=True)

    cmap = get_cmap(name="plasma", lut=combination_count)
    index = 0

    for combination_name in combination_names:
        results = combination_results[combination_name]

        # The result timestamps (x-axis) are treated as the y-axis,
        # and the result counts (y-axis) are scaled to an array [0:100:1].
        # This way, the min, max and avg can be plotted uniformly for all queries.
        # The actual plot will be done on a time axis (x-axis).
        x_target = list(range(0, 101))

        t_sum = None
        t_min = None
        t_max = None

        d_sum = None
        d_min = None
        d_max = None

        for result in results:
            r_x = list(range(0, result.result_count))
            r_avg = interp(x_target, r_x, result.timestamps_avg)
            r_min = interp(x_target, r_x, result.timestamps_min)
            r_max = interp(x_target, r_x, result.timestamps_max)
            if (
                t_sum is None
                or t_min is None
                or t_max is None
                or d_min is None
                or d_max is None
                or d_sum is None
            ):
                t_sum = r_avg
                t_min = r_min
                t_max = r_max
                d_sum = result.duration_avg
                d_min = result.duration_min
                d_max = result.duration_max
            else:
                t_min += r_min
                t_max += r_max
                t_sum += r_avg
                d_min = min(d_min, result.duration_min)
                d_max = max(d_max, result.duration_max)
                d_sum += result.duration_avg

        assert (
            t_min is not None
            and t_max is not None
            and t_sum is not None
            and d_sum is not None
        ), "Missing data for result trends"

        t_min = t_min / combination_count
        t_max = t_max / combination_count
        t_avg = t_sum / combination_count
        d_avg = d_sum / combination_count

        ax = fig.add_subplot(
            row_count,
            col_count,
            index + 1,
            sharex=ax_shared,
            sharey=ax_shared,
        )

        if ax_shared is None:
            ax_shared = ax

        y_max = max(y_max, d_avg, t_max[-1])

        color = cmap(index)

        ax.set_title(combination_name, pad=20, weight=500)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.yaxis.set_major_locator(y_locator)
        ax.set_ylim(bottom=0, top=y_max)
        ax.set_ylabel("time (s)", rotation=0, labelpad=30)

        ax.set_xlabel("result completeness (%)", labelpad=10)
        ax.set_xticks([x_target[0], x_target[-1]])

        # Average
        ax.plot(x_target, t_avg, color=color)
        ax.plot(x_target[-1], d_avg, "x", color=color)

        # Minimum and maximum
        ax.fill_between(x_target, t_min, t_max, color=color, alpha=0.1)
        # ax.plot(x_target[-1], d_min, "x", color=color, alpha=0.1)
        # ax.plot(x_target[-1], d_max, "x", color=color, alpha=0.1)

        index += 1

    fig.tight_layout(pad=4, h_pad=2, w_pad=2)

    info(f"Saving image as {IMAGE_EXT} to in-memory buffer")
    bytes_io = BytesIO()
    fig.savefig(fname=bytes_io, format=IMAGE_EXT, dpi=IMAGE_DPI)
    close(fig)
    bytes_io.seek(0)

    return bytes_io
