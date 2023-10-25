from pathlib import Path
from csv import DictReader
from typing import Tuple, Dict, List, Set
from math import sqrt
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.ticker import MaxNLocator
from matplotlib.figure import Figure
from matplotlib.pyplot import figure, get_cmap
from matplotlib.colors import Colormap


ROW_INCHES: int = 4
COLUMN_INCHES: int = 6
COLORMAP: str = "tab10"
IMAGE_EXTENSION: str = "svg"

rcParams["font.family"] = "serif"
rcParams["mathtext.fontset"] = "dejavuserif"


def get_colors(
    timestamps: Dict[str, Dict[str, List[float]]]
) -> Dict[str, Tuple[float, float, float, float]]:
    cmap: Colormap = get_cmap("tab10")
    configs: Set[str] = set()
    for query_data in timestamps.values():
        configs.update(query_data.keys())
    configs_list: List[str] = list(sorted(configs))
    return {configs_list[i]: cmap(i) for i in range(0, len(configs_list))}


def get_timestamps(result_directory: Path) -> Dict[str, Dict[str, List[float]]]:
    query_config_timestamps: Dict[str, Dict[str, List[float]]] = {}
    for config_directory in result_directory.iterdir():
        if not config_directory.is_dir():
            continue
        config_name: str = config_directory.name.replace("-", " ")
        config_results: Path = config_directory.joinpath("query-times.csv")
        with open(config_results, "r") as result_file:
            reader: DictReader = DictReader(result_file, delimiter=";")
            for row in reader:
                query: str = row["name"].replace("-", " ") + "." + row["id"]
                if query not in query_config_timestamps:
                    query_config_timestamps[query] = {}
                if row["error"] == "true":
                    # print("Failed query", config_name, query)
                    times = []
                else:
                    times = list(
                        int(t) / 1000 for t in row["timestamps"].split(" ") if t
                    )
                query_config_timestamps[query][config_name] = times
    for query in list(query_config_timestamps.keys()):
        if all(len(v) == 0 for v in query_config_timestamps[query].values()):
            print("Remove query with no results", query)
            del query_config_timestamps[query]
    return query_config_timestamps


def plot_timestamps(
    timestamps: Dict[str, Dict[str, List[float]]], figure_path: Path
) -> None:
    fig: Figure = figure(dpi=300)
    rows: int = int(sqrt(len(timestamps)))
    cols: int = int(len(timestamps) / rows + 0.5)
    print("Plotting into", cols, "x", rows, "grid")
    colors: Dict[str, Tuple[float, float, float, float]] = get_colors(timestamps)
    subplot_index: int = 0
    for query, query_data in sorted(timestamps.items(), key=lambda d: d[0]):
        subplot_index += 1
        ax: Axes = fig.add_subplot(rows, cols, subplot_index)
        ax.set_title(query)
        for config, config_timestamps in sorted(query_data.items(), key=lambda d: d[0]):
            result_count: int = len(config_timestamps)
            ax.step(
                x=config_timestamps,
                y=range(1, result_count + 1),
                lw=1,
                alpha=0.8,
                label=config,
                color=colors[config],
            )
            if result_count > 0:
                ax.plot(
                    config_timestamps[-1],
                    result_count,
                    alpha=0.8,
                    lw=1,
                    marker="x",
                    color=colors[config],
                )
        ax_ybound_upper = int(ax.get_xbound()[1] + 1)
        ax_xbound_upper = int(ax.get_ybound()[1] + 1)
        ax.set_xbound(lower=0, upper=ax_ybound_upper)
        ax.set_ybound(lower=0, upper=ax_xbound_upper)
        ax.set_xlabel("time [s]")
        ax.set_ylabel("# results")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        handles, labels = ax.get_legend_handles_labels()
    fig.legend(
        handles=handles,
        labels=labels,
        bbox_to_anchor=(0.9, 0.1),
        loc="lower right",
        ncols=int(sqrt(len(labels))),
    )
    fig.set_size_inches(cols * COLUMN_INCHES, rows * ROW_INCHES)
    fig.tight_layout(pad=1, h_pad=1, w_pad=1)
    fig.savefig(figure_path)


def plot_timestamps_for_results() -> None:
    results_path: Path = Path(__file__).parent.parent.joinpath("results")
    for result_directory in results_path.iterdir():
        figure_path = result_directory.joinpath(f"timestamps.{IMAGE_EXTENSION}")
        print("Plot:", figure_path.as_posix())
        timestamps = get_timestamps(result_directory)
        plot_timestamps(timestamps, figure_path)


if __name__ == "__main__":
    plot_timestamps_for_results()
