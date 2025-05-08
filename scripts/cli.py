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
from result import load_combination_results
from summaries import summary_table
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
    combinations = load_combination_results(result_path)
    dieff_image = plot_dieff_metrics(combinations)
    summary_table_markdown = summary_table(combinations, "md")
    summary_table_tsv = summary_table(combinations, "tsv")

    # Write the files on disk
    markdown_path = result_path.joinpath("README.md")
    tsv_path = result_path.joinpath("metrics.tsv")
    dieff_path = result_path.joinpath(f"metrics.{IMAGE_EXT}")

    markdown_content = "\n\n".join(
        [
            f"![metrics](./{dieff_path.name})",
            summary_table_markdown,
        ]
    )

    with open(dieff_path, "wb") as dieff_file:
        dieff_file.write(dieff_image.read())

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
