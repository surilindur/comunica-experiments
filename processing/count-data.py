from typing import Set
from pathlib import Path
from rdflib import Graph
from sys import argv

EXCLUDE_FILENAMES: Set[str] = set((".meta"))
INCLUDE_EXTENSIONS: Set[str] = set((".nq"))
PATHS_TO_PROCESS: Set[Path] = set()


def calculate_data(pods: Path) -> None:
    print(f"Pods path: {pods.as_posix()}")
    PATHS_TO_PROCESS.update(pods.iterdir())
    pod_count: int = len(PATHS_TO_PROCESS)
    file_count: int = 0
    triple_count: int = 0
    while PATHS_TO_PROCESS:
        path: Path = PATHS_TO_PROCESS.pop()
        if path.name in EXCLUDE_FILENAMES:
            continue
        elif path.is_dir():
            PATHS_TO_PROCESS.update(path.iterdir())
        elif path.is_file() and any(
            path.name.endswith(ext) for ext in INCLUDE_EXTENSIONS
        ):
            data: Graph = Graph()
            data.parse(path)
            triple_count += len(data)
            file_count += 1
        else:
            print(f"Skipping: {path.as_posix()}")
    print(f"Total of {pod_count} pods, {file_count} files, {triple_count} triples")


if __name__ == "__main__":
    pods_path: Path = Path(argv[1])
    calculate_data(pods_path)
