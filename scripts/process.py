"""Utility script to process experiment results, and provide various summaries."""

from typing import Set
from typing import List
from typing import Dict
from typing import Sequence
from logging import info
from logging import warning
from logging import basicConfig
from logging import INFO
from pathlib import Path
from argparse import ArgumentParser
from argparse import Namespace

from matplotlib.pyplot import subplots
from matplotlib.pyplot import close

from result import BenchmarkResult
from result import load_results_file

RESULTS_FILE_NAME = "query-times.csv"
MARKDOWN_FILE_NAME = "README.md"
ENDPOINT_LOG_NAME = "sparql-endpoint-comunica.txt"


class ArgsNamespace(Namespace):
    target: Path


def parse_args() -> ArgsNamespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--target",
        type=lambda p: Path(p).resolve(strict=True),
        required=True,
        help="Path to the experiment results",
    )
    return parser.parse_args(namespace=ArgsNamespace)


def setup_logging() -> None:
    basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        level=INFO,
    )


def create_readme(experiment: Path) -> None:
    """Create a markdown file with results summary in the target path."""
    readme_path = experiment.joinpath(MARKDOWN_FILE_NAME)
    results_path = experiment.joinpath(RESULTS_FILE_NAME)

    results = load_results_file(results_path)

    with open(readme_path, "w") as readme_file:
        headers = (
            "Query",
            "Results",
            "Duration (s)",
            "HTTP Requests",
            "*dieff@full*",
            "Error",
        )
        readme_file.write(f"|{"|".join(headers)}|\n")
        readme_file.write(f"|-|-:|-:|-:|-:|-|\n")
        for result in sorted(results, key=lambda r: r.name):
            columns = (
                result.name,
                f"{result.results:.0f}",
                f"{result.duration:.3f}",
                f"{result.http_avg:.0f}",
                f"{result.diefficiency:.3f}",
                result.error or "",
            )
            readme_file.write(f"|{"|".join(columns)}|\n")


def combination_comparison(experiment: Path) -> None:
    """Performs a comparison of combinations in the specified experiment."""

    info(f"Processing experiment at {experiment}")

    combinations: Dict[str, Sequence[BenchmarkResult]] = {}

    for fp in experiment.iterdir():
        result_path = fp.joinpath(RESULTS_FILE_NAME)
        if fp.is_dir() and result_path.exists():
            combinations[fp.name] = load_results_file(result_path)
            create_readme(fp)

    # # Combination titles for use like table column names
    # The baseline and overhead measurements should be at the beginning always
    combination_names = list(sorted(combinations.keys()))
    if "overhead" in combination_names:
        combination_names.remove("overhead")
        combination_names.insert(0, "overhead")
    if "baseline" in combination_names:
        combination_names.remove("baseline")
        combination_names.insert(0, "baseline")

    info(f"Discovered {len(combination_names)} combinations")

    # Tracking the failed queries, to establish a baseline of queries that
    # passed for all combinations, because comparisons in another way would be unfair
    failed_queries: Set[str] = set()
    ok_queries: Set[str] = set()

    # Metrics by query, with values arranged in order of columns above
    combination_diefficiencies: Dict[str, List[float]] = {}
    combination_diefficiencies_min: Dict[str, List[float]] = {}
    combination_diefficiencies_max: Dict[str, List[float]] = {}
    combination_durations: Dict[str, List[float]] = {}
    combination_durations_min: Dict[str, List[float]] = {}
    combination_durations_max: Dict[str, List[float]] = {}
    combination_http_requests: Dict[str, List[float]] = {}

    for combination_name in combination_names:
        for result in combinations[combination_name]:
            if result.failed or result.results < 1:
                failed_queries.add(result.name)
            else:
                ok_queries.add(result.name)
            if result.name in combination_diefficiencies:
                combination_diefficiencies[result.name].append(result.diefficiency)
                combination_diefficiencies_min[result.name].append(
                    result.diefficiency_min
                )
                combination_diefficiencies_max[result.name].append(
                    result.diefficiency_max
                )
                combination_durations[result.name].append(result.duration)
                combination_durations_min[result.name].append(result.duration_min)
                combination_durations_max[result.name].append(result.duration_max)
                combination_http_requests[result.name].append(result.http_avg)
            else:
                combination_diefficiencies[result.name] = [result.diefficiency]
                combination_diefficiencies_min[result.name] = [result.diefficiency_min]
                combination_diefficiencies_max[result.name] = [result.diefficiency_max]
                combination_durations[result.name] = [result.duration]
                combination_durations_min[result.name] = [result.duration_min]
                combination_durations_max[result.name] = [result.duration_max]
                combination_http_requests[result.name] = [result.http_avg]

    info(f"Total of {len(failed_queries)} failed and {len(ok_queries)} passed queries")

    info("Writing summary readme")

    with open(experiment.joinpath(MARKDOWN_FILE_NAME), "w") as summary_file:
        heading = f"| Query | {" | ".join(combination_names)} |"
        heading_separator = f"|-|{"-:|" * len(combination_names)}"
        summary_file.write("# Durations\n\n")
        summary_file.write(f"{heading}\n")
        summary_file.write(f"{heading_separator}\n")
        for query, durations in combination_durations.items():
            duration_strings = (f"{d:.3f}" for d in durations)
            summary_file.write(f"| {query} | {" | ".join(duration_strings)} |\n")
        summary_file.write("\n")
        summary_file.write("# Diefficiency\n\n")
        summary_file.write(f"{heading}\n")
        summary_file.write(f"{heading_separator}\n")
        for query, diefficiencies in combination_diefficiencies.items():
            diefficiency_strings = (f"{d:.3f}" for d in diefficiencies)
            summary_file.write(f"| {query} | {" | ".join(diefficiency_strings)} |\n")

    info("Serializing query-specific plots")

    results_by_query: Dict[str, Dict[str, BenchmarkResult]] = {}

    for results in combinations.values():
        for result in results:
            if result.name in results_by_query:
                results_by_query[result.name][result.combination] = result
            else:
                results_by_query[result.name] = {result.combination: result}

    for query, results in results_by_query.items():
        if sum(1 if r.results > 0 else 0 for r in results.values()) < 1:
            warning(f"Skipping query {query} without results")
            continue
        path = experiment.joinpath(f"{query} timestamps.svg")
        info(f"Saving figure {path}")
        fig, ax = subplots(nrows=1, ncols=1)
        ax.set_title(query)
        labels: List[str] = []
        for combination_name in combination_names:
            result = results[combination_name]
            labels.append(result.combination)
            x = result.timestamps
            y = list(range(1, result.results + 1))
            ax.step(x, y, where="post")
        ax.legend(labels)
        fig.savefig(path)
        close(fig)

    info(f"Writing total summary by combinations")

    total_queries: Dict[str, int] = {}
    total_success: Dict[str, int] = {}
    total_dieff: Dict[str, float] = {}
    dieff_min: Dict[str, float] = {}
    dieff_max: Dict[str, float] = {}
    total_duration: Dict[str, float] = {}
    duration_min: Dict[str, float] = {}
    duration_max: Dict[str, float] = {}
    total_first_result: Dict[str, float] = {}
    first_result_min: Dict[str, float] = {}
    first_result_max: Dict[str, float] = {}
    total_last_result: Dict[str, float] = {}
    last_result_min: Dict[str, float] = {}
    last_result_max: Dict[str, float] = {}
    total_http: Dict[str, float] = {}
    total_restarts: Dict[str, float] = {}

    for combination, results in combinations.items():
        # These are counted per-combination, not compared sum-wise
        total_queries[combination] = len(results)
        total_success[combination] = sum(0 if r.failed else 1 for r in results)
        total_restarts[combination] = 0

        # These must be comaprable between combinations, hence failed queries are ignored
        total_dieff[combination] = 0
        dieff_min[combination] = 999
        dieff_max[combination] = -999

        total_duration[combination] = 0
        duration_max[combination] = -999
        duration_min[combination] = 999

        total_http[combination] = 0

        total_first_result[combination] = 0
        first_result_max[combination] = -999
        first_result_min[combination] = 999

        total_last_result[combination] = 0
        last_result_max[combination] = -999
        last_result_min[combination] = 999

        for result in results:
            if result.name not in failed_queries:
                total_dieff[combination] += result.diefficiency
                dieff_min[combination] = min(
                    dieff_min[combination], result.diefficiency_min
                )
                dieff_max[combination] = max(
                    dieff_max[combination], result.diefficiency_max
                )

                total_duration[combination] += result.duration
                duration_max[combination] = max(
                    duration_max[combination], result.duration_max
                )
                duration_min[combination] = min(
                    duration_min[combination], result.duration_min
                )

                total_http[combination] += result.http_avg

                total_first_result[combination] += result.timestamps[0]
                first_result_max[combination] = max(
                    first_result_max[combination], result.timestamps_max[0]
                )
                first_result_min[combination] = min(
                    first_result_min[combination], result.timestamps_min[0]
                )

                total_last_result[combination] += result.timestamps[-1]
                last_result_max[combination] = max(
                    last_result_max[combination], result.timestamps_min[-1]
                )
                last_result_min[combination] = min(
                    last_result_min[combination], result.timestamps_max[-1]
                )

        log_path = experiment.joinpath(combination, "logs", ENDPOINT_LOG_NAME)

        if log_path.exists() and log_path.is_file():
            with open(log_path, "r") as log_file:
                for row in log_file:
                    if "Swapping join order" in row:
                        total_restarts[combination] += 1

    with open(
        experiment.joinpath("combination-comparison.tsv"), "w"
    ) as templates_summary:
        sep = "\t"
        templates_summary.write(
            sep.join(
                (
                    "combination",
                    "duration_total",
                    "duration_total_delta",
                    "duration_min",
                    "duration_min_delta",
                    "duration_max",
                    "duration_max_delta",
                    "first_result_total",
                    "first_result_total_delta",
                    "first_result_min",
                    "first_result_min_delta",
                    "first_result_max",
                    "first_result_max_delta",
                    "last_result_total",
                    "last_result_total_delta",
                    "last_result_min",
                    "last_result_min_delta",
                    "last_result_max",
                    "last_result_max_delta",
                    "dieff_total",
                    "dieff_total_delta",
                    "dieff_min",
                    "dieff_min_delta",
                    "dieff_max",
                    "dieff_max_delta",
                    "http",
                    "success",
                    "queries",
                    "restarts_total",
                )
            )
            + "\n"
        )
        for combination in combination_names:
            templates_summary.write(
                sep.join(
                    (
                        combination,
                        f"{total_duration[combination]:.3f}",
                        f"{total_duration[combination] / total_duration["baseline"] - 1:.3f}",
                        f"{duration_min[combination]:.3f}",
                        f"{duration_min[combination] / duration_min["baseline"] - 1:.3f}",
                        f"{duration_max[combination]:.3f}",
                        f"{duration_max[combination] / duration_max["baseline"] - 1:.3f}",
                        f"{total_first_result[combination]:.3f}",
                        f"{total_first_result[combination] / total_first_result["baseline"] - 1:.3f}",
                        f"{first_result_min[combination]:.3f}",
                        f"{first_result_min[combination] / first_result_min["baseline"] - 1:.3f}",
                        f"{first_result_max[combination]:.3f}",
                        f"{first_result_max[combination] / first_result_max["baseline"] - 1:.3f}",
                        f"{total_last_result[combination]:.3f}",
                        f"{total_last_result[combination] / total_last_result["baseline"] - 1:.3f}",
                        f"{last_result_min[combination]:.3f}",
                        f"{last_result_min[combination] / last_result_min["baseline"] - 1:.3f}",
                        f"{last_result_max[combination]:.3f}",
                        f"{last_result_max[combination] / last_result_max["baseline"] - 1:.3f}",
                        f"{total_dieff[combination]:.3f}",
                        f"{total_dieff[combination] / total_dieff["baseline"] - 1:.3f}",
                        f"{dieff_min[combination]:.3f}",
                        f"{dieff_min[combination] / dieff_min["baseline"] - 1:.3f}",
                        f"{dieff_max[combination]:.3f}",
                        f"{dieff_max[combination] / dieff_max["baseline"] - 1:.3f}",
                        f"{total_http[combination]:.0f}",
                        f"{total_success[combination]:.0f}",
                        f"{total_queries[combination]:.0f}",
                        f"{total_restarts[combination]:.3f}",
                    )
                )
                + "\n"
            )

    info("Finished")


def main() -> None:
    setup_logging()
    args = parse_args()
    if args.target.joinpath(RESULTS_FILE_NAME).exists():
        create_readme(args.target)
    else:
        combination_comparison(args.target)


if __name__ == "__main__":
    main()
