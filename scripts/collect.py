from shutil import copy
from shutil import copytree
from shutil import rmtree
from logging import info
from tarfile import open as open_tarfile
from pathlib import Path

RESULTS_PATH = Path(__file__).parent.parent.joinpath("results")


def collect_results(path: Path) -> None:
    """Collect the experiment results from combinations."""

    # Clear the previous experiment results
    results_path = RESULTS_PATH.joinpath(path.name)
    if results_path.exists():
        rmtree(results_path)
    results_path.mkdir()

    info(f"Collecting results into {results_path}")

    for combination in path.joinpath("combinations").iterdir():
        combination_output_path = combination.joinpath("output")
        combination_manifest_path = combination.joinpath("jbr-experiment.json")

        # Copy the original path, to avoid deleting stuff
        combination_results_path = results_path.joinpath(combination.name)
        copytree(
            combination_output_path,
            combination_results_path,
            dirs_exist_ok=False,
        )
        copy(
            combination_manifest_path,
            combination_results_path.joinpath(combination_manifest_path.name),
        )
        results_path.joinpath(".keep").unlink(missing_ok=True)

        # Compress the logs directory
        logs_directory_path = combination_results_path.joinpath("logs")
        logs_archive_path = combination_results_path.joinpath("logs.tar.gz")
        info(f"Compressing logs into {logs_archive_path}")
        with open_tarfile(logs_archive_path, "w:gz") as tar:
            tar.add(name=logs_directory_path, arcname=".")
        rmtree(logs_directory_path)

        # Compress the stats
        stats_archive_path = combination_results_path.joinpath("stats.tar.gz")
        info(f"Compressing stats into {stats_archive_path}")
        with open_tarfile(stats_archive_path, "w:gz") as tar:
            for stats_file_path in results_path.iterdir():
                if stats_file_path.name.startswith("stats-"):
                    tar.add(name=stats_file_path, arcname=stats_file_path.name)
                    stats_file_path.unlink()
