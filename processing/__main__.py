"""The CLI tool implementation."""

from io import BytesIO
from time import perf_counter
from typing import Dict
from typing import List
from typing import Callable
from typing import Iterable
from typing import Literal
from logging import DEBUG
from logging import INFO
from logging import info
from logging import debug
from logging import basicConfig
from pathlib import Path
from argparse import ArgumentParser
from argparse import Namespace
from argparse import BooleanOptionalAction

from collect import collect_results
from jbrcsv import JbrQuery
from jbrcsv import parse_jbr_queries
from jbrstats import JbrStats
from jbrstats import parse_jbr_stats
from tables import generate_combination_comparison_table
from figures import IMAGE_FORMAT
from figures import plot_combination_resources_over_time
from figures import plot_combination_completeness_trends
from figures import plot_combination_http_requests
from figures import plot_combination_diefficiency_values
from figures import plot_combination_timestamp_values
from figures import plot_combination_duration_values
from figures import plot_template_completeness_trends


class CliArgs(Namespace):
    debug: bool
    source: Path
    action: Literal["collect", "analyse"]


def parse_cli_args() -> type[CliArgs]:
    """Helper function to parse CLI args."""

    parser = ArgumentParser(allow_abbrev=False)

    parser.add_argument(
        "action",
        choices=["collect", "analyse"],
        help="The action to take",
    )

    parser.add_argument(
        "--debug",
        action=BooleanOptionalAction,
        help="Enables additional logging for debugging",
    )

    parser.add_argument(
        "--source",
        type=lambda p: Path(p).resolve(strict=True),
        help="Path to data in need of processing",
    )

    return parser.parse_args(namespace=CliArgs)


def analyse_results(source: Path) -> None:
    """Analyse the results in the specified path."""

    readme_rows: List[str] = []

    queries = parse_jbr_queries(path=source, ignore_failed=True)
    stats = parse_jbr_stats(path=source)

    readme_rows.append("## Combinations\n\n")
    table_header = True

    for row_cells in generate_combination_comparison_table(queries=queries, stats=stats):
        readme_rows.append("| " + " | ".join(row_cells) + " |\n")
        if table_header:
            cell_count = len(tuple(row_cells))
            readme_rows.append("|" + "|".join([":-", *["-:" for _ in range(0, cell_count - 1)]]) + "|\n")
            table_header = False

    readme_rows.append("\n")

    queries_plot_targets: Dict[str, Callable[[Iterable[JbrQuery]], BytesIO]] = {
        "templates": plot_template_completeness_trends,
        "combinations": plot_combination_completeness_trends,
        "httprequests": plot_combination_http_requests,
        "diefficiency": plot_combination_diefficiency_values,
        "timestamps": plot_combination_timestamp_values,
        "durations": plot_combination_duration_values,
    }

    for name, function in queries_plot_targets.items():
        image_path = source.joinpath(f"{name}.{IMAGE_FORMAT}")
        readme_rows.extend([f"## {name}\n\n", f"![{name}]({image_path.name})\n\n"])
        with open(image_path, "wb") as image_file:
            debug(f"Generating {name} figure")
            image_buffer = function(queries)
            image_file.write(image_buffer.read())

    stats_plot_targets: Dict[str, Callable[[Iterable[JbrStats], str], BytesIO]] = {
        "resources": plot_combination_resources_over_time,
    }

    for name, function in stats_plot_targets.items():
        image_path = source.joinpath(f"{name}.{IMAGE_FORMAT}")
        readme_rows.extend([f"## {name}\n\n", f"![{name}]({image_path.name})\n\n"])
        with open(image_path, "wb") as image_file:
            debug(f"Generating {name} figure")
            image_buffer = function(stats, "sparql")
            image_file.write(image_buffer.read())

    readme_path = source.joinpath("README.md")

    info(f"Writing readme to {readme_path}")

    with open(readme_path, "w") as readme_file:
        readme_file.writelines(readme_rows)


def main() -> None:
    """The main entrypoint."""

    args = parse_cli_args()

    basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=DEBUG if args.debug else INFO,
    )

    time_start = perf_counter()

    match args.action:
        case "analyse":
            info(f"Analysing results in {args.source}")
            analyse_results(source=args.source)
        case "collect":
            info(f"Collecting results from {args.source}")
            collect_results(path=args.source)

    info(f"Finished in {(perf_counter() - time_start):.1f} seconds")


if __name__ == "__main__":
    main()
