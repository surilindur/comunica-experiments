"""Utility script to process experiment results, and provide various summaries."""

from time import perf_counter
from typing import Literal
from logging import basicConfig
from logging import info
from logging import INFO
from pathlib import Path
from argparse import ArgumentParser
from argparse import Namespace

from plots import IMAGE_EXT
from plots import plot_dieff_metrics
from plots import plot_network_metrics
from result import load_combination_results
from result import load_combination_stats
from summaries import combination_summary_table
from collect import collect_results


class ArgsNamespace(Namespace):
    action: Literal["collect", "analyse"]
    target: Path


def parse_args() -> ArgsNamespace:
    parser = ArgumentParser()
    parser.add_argument(
        "action",
        choices=["collect", "analyse"],
        help="The action to take",
    )
    parser.add_argument(
        "target",
        type=lambda p: Path(p).resolve(strict=True),
        help="Path to the action target",
    )
    return parser.parse_args(namespace=ArgsNamespace)


def setup_logging() -> None:
    basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        level=INFO,
    )


def analyse_results(result_path: Path) -> None:
    """Performs results analysis on the given experiment results."""

    info(f"Processing results in {result_path}")

    # Acquire the data
    combination_results = load_combination_results(result_path)
    combination_stats = load_combination_stats(result_path)

    # Generate images
    dieff_image = plot_dieff_metrics(combination_results)
    network_image = plot_network_metrics(combination_results, combination_stats)

    # Generate tables
    summary_table_markdown = combination_summary_table(combination_results, "md")
    summary_table_tsv = combination_summary_table(combination_results, "tsv")

    # Write the files on disk
    markdown_path = result_path.joinpath("README.md")
    tsv_path = result_path.joinpath("metrics.tsv")
    dieff_path = result_path.joinpath(f"diefficiency.{IMAGE_EXT}")
    network_path = result_path.joinpath(f"network.{IMAGE_EXT}")

    markdown_content = "\n\n".join(
        [
            "### Query processing",
            f"![diefficiency](./{dieff_path.name})",
            summary_table_markdown,
            "### Network utilisation",
            f"![network](./{network_path.name})",
            # TODO: network table
            "### Resource consumption",
            # TODO: resource graph
            # TODO: resource table
        ]
    )

    with open(dieff_path, "wb") as dieff_file:
        dieff_file.write(dieff_image.read())

    with open(network_path, "wb") as network_file:
        network_file.write(network_image.read())

    with open(markdown_path, "w") as markdown_file:
        markdown_file.write(markdown_content)

    with open(tsv_path, "w") as tsv_file:
        tsv_file.write(summary_table_tsv)


def main() -> None:
    setup_logging()
    args = parse_args()
    time_start = perf_counter()
    match args.action:
        case "analyse":
            analyse_results(args.target)
        case "collect":
            collect_results(args.target)
    info(f"Finished in {perf_counter() - time_start:.2f} seconds")


if __name__ == "__main__":
    main()
