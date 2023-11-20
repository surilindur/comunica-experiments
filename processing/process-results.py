from json import loads
from pathlib import Path
from typing import Tuple, List, Dict, Any


def get_result_timestamps(data: Dict[str, Dict[str, Any]]) -> List[int]:
    timestamps: List[int] = []
    for key in data["result_data"].keys():
        timestamps.append(int(key))
    timestamps.sort()
    return timestamps


def process_from_path(path: Path) -> Dict[str, Dict[str, Any]] | None:
    print(f"Processing: {path.as_posix()}")
    output: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for result in path.iterdir():
        if not result.name.endswith(".json"):
            continue
        with open(result, "r") as result_file:
            data: Dict[str, Any] = loads(result_file.read())
            name, id = data["engine_query"].split("/queries/")[-1].split(".sparql#")
            timestamps: List[int] = get_result_timestamps(data)
            if (name, id) not in output:
                output[(name, id)] = {
                    "name": name,
                    "id": id,
                    "results": data["result_count"],
                    "time": round(float(data["time_taken_seconds"]) * 1000),
                    "error": data["engine_timeout_reached"] or data["result_count"] < 1,
                    "timestamps": timestamps,
                    "timestampsMin": timestamps,
                    "timestampsMax": timestamps,
                    "httpRequests": data["requested_urls_count"],
                    "restarts": len(data["result_data_other"]),
                }
            else:
                if data["result_count"] != output[(name, id)]["results"]:
                    output[(name, id)]["error"] = True
                    print(f"Varying number of results for {name} {id}")
                else:
                    for i in range(0, len(timestamps)):
                        old_timestamp = output[(name, id)]["timestamps"][i]
                        new_timestamp = round((old_timestamp + timestamps[i]) / 2)
                        output[(name, id)]["timestamps"][i] = new_timestamp
                        output[(name, id)]["timestampsMin"][i] = min(
                            old_timestamp, timestamps[i]
                        )
                        output[(name, id)]["timestampsMax"][i] = max(
                            old_timestamp, timestamps[i]
                        )
                    restart_count_new = len(data["result_data_other"])
                    output[(name, id)]["restarts"] = max(
                        output[(name, id)]["restarts"], restart_count_new
                    )
    for result in output.values():
        for column in ("timestamps", "timestampsMin", "timestampsMax"):
            result[column] = list(str(round(k / 1000000)) for k in result[column])
        result["error"] = "true" if result["error"] else "false"
    return output if len(output) > 0 else None


def serialize_processed(data: Dict[str, Dict[str, Any]], path: Path) -> None:
    columns: List[str] = [
        "name",
        "id",
        "results",
        "time",
        "error",
        "timestamps",
        "timestampsMin",
        "timestampsMax",
        "httpRequests",
        "restarts",
    ]
    csv_sep: str = ";"
    csv_sep_list: str = " "
    with open(path, "w") as csv_file:
        csv_file.write(csv_sep.join(columns) + "\n")
        for entry in data.values():
            csv_file.write(
                csv_sep.join(
                    csv_sep_list.join(entry[k])
                    if isinstance(entry[k], list)
                    else str(entry[k])
                    for k in columns
                )
                + "\n"
            )
    print(f"Wrote: {path}")


def split_by_config(unprocessed: Path) -> None:
    for result in unprocessed.iterdir():
        with open(result, "r") as result_file:
            result_data: Dict[str, str | Any] = loads(result_file.read())
            config_id = (
                result_data["engine_config"].removesuffix(".json").split("/config-")[-1]
            )
            target_path: Path = unprocessed.parent.joinpath(config_id)
            if not target_path.exists():
                target_path.mkdir()
            result.rename(target_path.joinpath(result.name))


def process_all() -> None:
    results_path: Path = Path(__file__).parent.parent.joinpath("results").resolve()
    for results in results_path.iterdir():
        # unprocessed: Path = results.joinpath("unprocessed")
        # if unprocessed.exists():
        #    split_by_config(unprocessed)
        if results.is_dir():
            for config_results in results.iterdir():
                if config_results.is_dir():
                    processed = process_from_path(config_results)
                    if processed:
                        serialize_processed(
                            processed, config_results.joinpath("query-times.csv")
                        )


if __name__ == "__main__":
    process_all()
