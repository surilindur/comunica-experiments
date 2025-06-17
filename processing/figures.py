"""Helper functions for plotting figures."""

from io import BytesIO
from typing import Set
from typing import Dict
from typing import List
from typing import Iterable
from typing import Sequence
from typing import Mapping
from logging import INFO
from logging import debug
from logging import getLogger

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.pyplot import rcParams
from matplotlib.pyplot import subplots
from matplotlib.pyplot import close
from matplotlib.pyplot import get_cmap

from numpy import arange
from numpy import array
from numpy import vstack
from numpy import float64
from numpy.typing import NDArray

from analysis import resample_timestamps
from analysis import calculate_confidence_interval
from analysis import calculate_diefficiency_at_full_results
from analysis import calculate_aggregate_completeness_curve
from jbrcsv import JbrQuery
from jbrstats import JbrStats
from jbrstats import MB_BYTES
from jbrstats import GB_BYTES
from utils import sort_labels

SINGLE_COLOR = tuple(t / 255 for t in (0, 100, 190, 255))
IMAGE_COLORMAP = "viridis"  # viridis and cividis should be colorblind-friendly
IMAGE_FORMAT = "svg"
IMAGE_DPI = 600

rcParams["font.family"] = "Noto Serif"
rcParams["font.weight"] = 400

getLogger("matplotlib.font_manager").setLevel(INFO)


def cleanup_axes(ax: Axes) -> None:
    """Helper function to clean up axes."""

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.set_yticks([])
    ax.set_xticks([])


def save_figure(fig: Figure) -> BytesIO:
    """Saves a figure into an in-memory byte buffer, and then closes it."""

    fig_buffer = BytesIO()
    fig.savefig(fname=fig_buffer, format=IMAGE_FORMAT, dpi=IMAGE_DPI)
    close(fig=fig)
    fig_buffer.seek(0)

    return fig_buffer


def plot_template_completeness_trends(queries: Iterable[JbrQuery]) -> BytesIO:
    """Aggregates the queries by template, and plots the result arrival trends."""

    template_query_timestamps: Dict[str, Dict[str, NDArray[float64]]] = {}
    combination_names_set: Set[str] = set()

    for query in queries:
        combination_names_set.add(query.combination)
        if query.template not in template_query_timestamps:
            template_query_timestamps[query.template] = {}
        if query.combination in template_query_timestamps[query.template]:
            template_query_timestamps[query.template][query.combination] = vstack([
                template_query_timestamps[query.template][query.combination],
                resample_timestamps(query.timestamps),
            ])
        else:
            template_query_timestamps[query.template][query.combination] = resample_timestamps(query.timestamps,)

    template_count = len(template_query_timestamps)
    template_names = sort_labels([ *template_query_timestamps.keys() ])
    combination_names = sort_labels([ * combination_names_set ])
    combination_colors = get_cmap(name=IMAGE_COLORMAP, lut=len(combination_names))

    # determine column and row count
    ncols = min(6, template_count)
    nrows = max(round(template_count / ncols + 0.5), 1)

    debug(f"Plotting {template_count} templates in {ncols}x{nrows} grid")

    fig, axs = subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(ncols * 3, nrows * 3),
        sharex="all",
        layout="constrained",
    )

    # flatten in case of multiple rows, and remove unused cells
    if nrows > 1:
        axs = axs.flatten()  # type: ignore
        for i in range(template_count, len(axs)):
            axs[i].remove()

    # typing helper for autocompletion, and an assertion to encorce it
    assert len(axs) >= template_count and isinstance(axs[0], Axes)
    axs: Sequence[Axes] = axs

    for template_index, template_name in enumerate(template_names):
        for combination_index, combination_name in enumerate(combination_names):
            # calculate the completeness trend across every instance
            t_min, t_avg, t_max = calculate_aggregate_completeness_curve(
                timestamps=template_query_timestamps[template_name][combination_name],
            )

            # ensure the completeness percent makes sense
            c_percent = arange(start=0, stop=template_query_timestamps[template_name][combination_name].shape[1],)

            # average as a single lineplot: y-axis is the time, x-axis the completeness
            axs[template_index].plot(c_percent, t_avg, color=combination_colors(combination_index),)

        # clean up the axis
        cleanup_axes(axs[template_index])

        # add template name
        axs[template_index].set_title(template_name, pad=0, weight=400, size=11)
        if template_index % ncols == 0:
            axs[template_index].set_ylabel(
                ylabel="time (s)",
                rotation=0,
                labelpad=30,
                style="italic",
            )

        # add x-axis ticks
        axs[template_index].xaxis.set_ticks(
            ticks=[0, 100],
            labels=[str(0), str(100)]
        )

        # adjust y-axis ticks
        y_max = round(axs[template_index].get_ylim()[1] + 0.5)
        y_min = 0
        axs[template_index].set_ylim(bottom=y_min, top=y_max)
        axs[template_index].yaxis.set_ticks(ticks=[y_min, y_max], labels=[str(y_min), str(y_max)],)
        axs[template_index].yaxis.set_tick_params(length=0)

    return save_figure(fig=fig)

def plot_combination_completeness_trends(queries: Iterable[JbrQuery]) -> BytesIO:
    """Aggregates the queries by combination, and plots the result arrival trends."""

    combination_timestamps: Dict[str, NDArray[float64]] = {}

    for query in queries:
        if query.combination in combination_timestamps:
            combination_timestamps[query.combination] = vstack(
                [
                    combination_timestamps[query.combination],
                    resample_timestamps(query.timestamps),
                ]
            )
        else:
            combination_timestamps[query.combination] = resample_timestamps(
                query.timestamps,
            )

    combination_count = len(combination_timestamps)
    combination_colors = get_cmap(name=IMAGE_COLORMAP, lut=combination_count)

    # determine column and row count
    ncols = min(6, combination_count)
    nrows = max(int(combination_count / ncols + 0.5), 1)

    debug(f"Plotting {combination_count} combinations in {ncols}x{nrows} grid")

    fig, axs = subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(ncols * 3, nrows * 3),
        sharex="all",
        layout="constrained",
    )

    # flatten in case of multiple rows, and remove unused cells
    if nrows > 1:
        axs = axs.flatten()  # type: ignore
        for i in range(combination_count, len(axs)):
            axs[i].remove()

    # typing helper for autocompletion, and an assertion to encorce it
    assert len(axs) >= combination_count and isinstance(axs[0], Axes)
    axs: Sequence[Axes] = axs

    combination_names = sort_labels(list(combination_timestamps.keys()))

    for i, combination_name in enumerate(combination_names):
        # calculate the completeness trend across every query and replication
        t_min, t_avg, t_max = calculate_aggregate_completeness_curve(
            timestamps=combination_timestamps[combination_name],
        )

        # override the min and max in the plots with the 95% confidence interval
        t_min, t_max = calculate_confidence_interval(
            data=combination_timestamps[combination_name],
            confidence=0.95,
        )

        # ensure the completeness percent makes sense
        c_percent = arange(start=0, stop=combination_timestamps[combination_name].shape[1])

        # shaded area between min and max to illustrate the spread
        axs[i].fill_between(
            c_percent,
            t_min,
            t_max,
            color=combination_colors(i),
            alpha=0.1,
            linewidth=0,
        )

        # average as a single lineplot: y-axis is the time, x-axis the completeness
        axs[i].plot(c_percent, t_avg, color=combination_colors(i))

        # add relevant labels
        axs[i].set_title(combination_name, pad=0, weight=400, size=11)
        if i % ncols == 0:
            axs[i].set_ylabel(
                ylabel="time (s)",
                rotation=0,
                labelpad=30,
                style="italic",
            )

        # clean up the axis
        cleanup_axes(axs[i])

        # add x-axis ticks
        axs[i].xaxis.set_ticks(
            ticks=[0, combination_timestamps[combination_name].shape[1]],
            labels=[str(0), str(combination_timestamps[combination_name].shape[1])],
        )

        # add y-axis ticks
        axs[i].yaxis.tick_right()
        axs[i].yaxis.set_ticks(
            ticks=[t_avg[-1]],
            labels=[f"{t_avg[-1]:.2f}"],
            color=combination_colors(i),
        )
        axs[i].yaxis.set_tick_params(length=0)

    # ensure the axes all have same ranges
    y_lims = [ax.get_ylim() for ax in axs]
    y_min = min(t[0] for t in y_lims)
    y_max = max(t[1] for t in y_lims)
    for ax in axs:
        ax.set_ylim(bottom=y_min, top=y_max)

    # adjust spacing depending on row count
    # if nrows > 1:
    #    fig.subplots_adjust(wspace=0.1, hspace=0.1)
    # else:
    #    fig.subplots_adjust(wspace=0.5, hspace=0)

    return save_figure(fig=fig)


def plot_combination_points(
    combination_points: Mapping[str, Sequence[float]],
    xlabel: str,
) -> BytesIO:
    """Generate a plot of point values by combination, as a bar-like scatter plot."""

    combination_count = len(combination_points)
    combination_colors = get_cmap(name=IMAGE_COLORMAP, lut=combination_count)

    fig, ax = subplots(
        nrows=1,
        ncols=1,
        figsize=(5, round(combination_count / 3)),
        sharex="all",
        layout="tight",
    )

    assert isinstance(ax, Axes), "Invalid figure setup"

    combination_names = sort_labels(list(combination_points.keys()))
    x_max = 0

    for i, combination_name in enumerate(combination_names):
        x = combination_points[combination_name]
        x_max = round(max([x_max, *x]))
        y = array([1 for _ in range(0, len(x))]) * i + 1
        ax.scatter(x=x, y=y, color=combination_colors(i), marker=".")

    # remove everything from the axes
    cleanup_axes(ax)

    # add labels on the y-axis
    ax.yaxis.set_ticks(
        ticks=range(1, combination_count + 1),
        labels=combination_names,
        ha="left",
    )
    ax.yaxis.set_tick_params(length=0, pad=180)
    ax.yaxis.set_inverted(True)

    # add ticks on the x-axis
    ax.xaxis.set_ticks(ticks=[0, x_max], labels=[str(0), str(x_max)])
    ax.set_xlabel(xlabel=xlabel, style="italic", labelpad=10)

    return save_figure(fig=fig)


def plot_combination_http_requests(queries: Iterable[JbrQuery]) -> BytesIO:
    """Generate a plot of HTTP request counts by combination."""

    combination_requests: Dict[str, List[float]] = {}

    for query in queries:
        if query.combination in combination_requests:
            combination_requests[query.combination].append(query.http_requests_min)
        else:
            combination_requests[query.combination] = [query.http_requests_min]

    return plot_combination_points(
        combination_points=combination_requests,
        xlabel="minimum HTTP request count",
    )


def plot_combination_diefficiency_values(queries: Iterable[JbrQuery]) -> BytesIO:
    """Generate a plot of diefficiency values per combination."""

    combination_diefficiencies: Dict[str, List[float]] = {}

    for query in queries:
        for replication_timestamps in query.timestamps:
            replication_diefficiency = calculate_diefficiency_at_full_results(
                timestamps=replication_timestamps,
            )
            if query.combination in combination_diefficiencies:
                combination_diefficiencies[query.combination].append(
                    replication_diefficiency,
                )
            else:
                combination_diefficiencies[query.combination] = [
                    replication_diefficiency,
                ]

    return plot_combination_points(
        combination_points=combination_diefficiencies,
        xlabel="diefficiency at full results",
    )


def plot_combination_duration_values(queries: Iterable[JbrQuery]) -> BytesIO:
    """Generate a plot of query durations per combinations."""

    combination_durations: Dict[str, List[float]] = {}

    for query in queries:
        if query.combination in combination_durations:
            combination_durations[query.combination].append(query.duration_avg)
        else:
            combination_durations[query.combination] = [ query.duration_avg ]

    return plot_combination_points(
        combination_points=combination_durations,
        xlabel="query durations (s)",
    )


def plot_combination_timestamp_values(queries: Iterable[JbrQuery]) -> BytesIO:
    """Generate a plot of timestamp values per combination."""

    combination_timestamps: Dict[str, List[float]] = {}

    for query in queries:
        for replication_timestamps in query.timestamps:
            if query.combination in combination_timestamps:
                combination_timestamps[query.combination].extend(replication_timestamps)
            else:
                combination_timestamps[query.combination] = list(replication_timestamps)

    return plot_combination_points(
        combination_points=combination_timestamps,
        xlabel="result arrival timestamps (s)",
    )

def plot_combination_resources(stats: Iterable[JbrStats]) -> BytesIO:
    """Generate a plot of combination resources summary for comparison."""

    fig, axs = subplots(nrows=1, ncols=4, figsize=(8, 16), layout="constrained",)

    assert len(axs) == 4 and isinstance(axs[0], Axes)
    axs: Sequence[Axes] = axs

    for ax in axs:
        cleanup_axes(ax)

    return save_figure(fig=fig)

def plot_combination_resources_over_time(stats: Iterable[JbrStats], container: str,) -> BytesIO:
    """Generate a plot of combination resource consumptions for comparison."""

    combination_stats = {s.combination: s for s in stats if container in s.container}
    combination_names = sort_labels([ *combination_stats.keys() ])
    combination_colors = get_cmap(name=IMAGE_COLORMAP, lut=len(combination_names))

    fig, axs = subplots(
        nrows=4,
        ncols=1,
        sharex="all",
        sharey="none",
        figsize=(16, 8),
        layout="constrained",
    )

    assert len(axs) == 4 and isinstance(axs[0], Axes)
    axs: Sequence[Axes] = axs

    for ax in axs:
        cleanup_axes(ax)

    for i, combination_name in enumerate(combination_names):
        color = combination_colors(i)
        axs[0].plot(combination_stats[combination_name].cpu_percent, color=color)
        axs[1].plot(combination_stats[combination_name].mem_bytes / GB_BYTES, color=color)
        axs[2].plot(combination_stats[combination_name].net_rx_bytes / MB_BYTES, color=color)
        axs[3].plot(combination_stats[combination_name].net_tx_bytes / MB_BYTES, color=color)

    axs[0].set_ylabel(ylabel="CPU (%)", rotation=0, labelpad=70)
    axs[1].set_ylabel(ylabel="Memory (GB)", rotation=0, labelpad=60)
    axs[2].set_ylabel(ylabel="Inbound (MB)", rotation=0, labelpad=50)
    axs[3].set_ylabel(ylabel="Outbound (MB)", rotation=0, labelpad=50)

    for i, ax in enumerate(axs):
        y_max = round(ax.get_ylim()[1]) if i > 0 else 100
        y_min = 0
        ax.set_ylim(bottom=y_min, top=y_max)
        ax.set_yticks(ticks=[y_min, y_max], labels=[str(y_min), str(y_max)])

    return save_figure(fig=fig)
