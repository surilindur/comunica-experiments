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
from summaries import diefficiency_summary_table
from summaries import network_summary_table
from summaries import template_summary_table
from summaries import resource_summary_table
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
    combination_results_unfiltered = load_combination_results(
        result_path,
        filter_failed=False,
    )
    combination_stats = load_combination_stats(result_path)

    # Generate images
    dieff_image = plot_dieff_metrics(combination_results)
    network_image = plot_network_metrics(combination_results, combination_stats)

    # Generate tables
    summary_dieff_md = diefficiency_summary_table(combination_results, "md")
    summary_dieff_tsv = diefficiency_summary_table(combination_results, "tsv")
    summary_network_md = network_summary_table(
        combination_results,
        combination_stats,
        "md",
    )
    summary_network_tsv = network_summary_table(
        combination_results,
        combination_stats,
        "tsv",
    )
    summary_template_md = template_summary_table(combination_results_unfiltered, "md")
    summary_template_tsv = template_summary_table(combination_results_unfiltered, "tsv")
    summary_resources_md = resource_summary_table(combination_stats, "md")
    summary_resources_tsv = resource_summary_table(combination_stats, "tsv")

    # Write the files on disk
    markdown_path = result_path.joinpath("README.md")
    dieff_tsv_path = result_path.joinpath("processing.tsv")
    dieff_image_path = result_path.joinpath(f"processing.{IMAGE_EXT}")
    network_tsv_path = result_path.joinpath("resources.tsv")
    network_image_path = result_path.joinpath(f"resources.{IMAGE_EXT}")
    template_tsv_path = result_path.joinpath("templates.tsv")
    resource_tsv_path = result_path.joinpath("resources.tsv")

    markdown_content = "\n\n".join(
        [
            "### Template overview",
            # TODO: template plot
            summary_template_md,
            "### Processing",
            f"![processing](./{dieff_image_path.name})",
            summary_dieff_md,
            "### Network",
            f"![network](./{network_image_path.name})",
            summary_network_md,
            "### Resource consumption",
            # TODO: resource graph
            summary_resources_md,
        ]
    )

    with open(dieff_image_path, "wb") as dieff_file:
        dieff_file.write(dieff_image.read())

    with open(network_image_path, "wb") as network_file:
        network_file.write(network_image.read())

    with open(markdown_path, "w") as markdown_file:
        markdown_file.write(markdown_content)

    with open(dieff_tsv_path, "w") as tsv_file:
        tsv_file.write(summary_dieff_tsv)

    with open(network_tsv_path, "w") as tsv_file:
        tsv_file.write(summary_network_tsv)

    with open(template_tsv_path, "w") as tsv_file:
        tsv_file.write(summary_template_tsv)

    with open(resource_tsv_path, "w") as tsv_file:
        tsv_file.write(summary_resources_tsv)


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
