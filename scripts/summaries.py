from typing import Dict
from typing import Literal
from typing import Iterable

from result import BenchmarkResult
from utils import sort_labels


def summary_table(
    combinations: Dict[str, Iterable[BenchmarkResult]],
    table_format: Literal["md", "tsv"],
) -> str:
    """Generate a summary table in markdown for the combinations."""

    combination_names = sort_labels(combinations.keys())

    headers = [
        "Combination",
        "*dieff@full*",
        "*dieff@full* min",
        "*dieff@full* max",
        "Duration",
        "Duration min",
        "Duration max",
        "First result",
        "First result min",
        "First result max",
        "Last result",
        "Last result min",
        "Last result max",
        "Queries",
    ]

    if "baseline" in combination_names:
        headers = [
            f"Δ {h.lower()}" if h not in ("Combination", "Queries") else h
            for h in headers
        ]

    if table_format == "tsv":
        headers = [h.replace("*", "") for h in headers]

    table_rows = [headers]

    if table_format == "md":
        table_rows.append(["-", *("-:" for _ in range(0, len(headers) - 1))])

    baseline_dieff_avg: float | None = None
    baseline_dieff_min: float | None = None
    baseline_dieff_max: float | None = None
    baseline_duration_avg: float | None = None
    baseline_duration_min: float | None = None
    baseline_duration_max: float | None = None
    baseline_first_avg: float | None = None
    baseline_first_min: float | None = None
    baseline_first_max: float | None = None
    baseline_last_avg: float | None = None
    baseline_last_min: float | None = None
    baseline_last_max: float | None = None

    for combination_name in combination_names:
        results = combinations[combination_name]
        combination_dieff_avg = sum(r.diefficiency_avg for r in results)
        combination_dieff_min = sum(r.diefficiency_min for r in results)
        combination_dieff_max = sum(r.diefficiency_max for r in results)
        combination_duration_avg = sum(r.duration_avg for r in results)
        combination_duration_min = sum(r.duration_min for r in results)
        combination_duration_max = sum(r.duration_max for r in results)
        combination_first_avg = sum(r.timestamps_avg[0] for r in results)
        combination_first_min = sum(r.timestamps_min[0] for r in results)
        combination_first_max = sum(r.timestamps_max[0] for r in results)
        combination_last_avg = sum(r.timestamps_avg[-1] for r in results)
        combination_last_min = sum(r.timestamps_min[-1] for r in results)
        combination_last_max = sum(r.timestamps_max[-1] for r in results)
        if "baseline" not in combination_names:

            def format_value(v: float) -> str:
                return f"{v:.3f}"

            table_rows.append(
                [
                    combination_name,
                    format_value(combination_dieff_avg),
                    format_value(combination_dieff_min),
                    format_value(combination_dieff_max),
                    format_value(combination_duration_avg),
                    format_value(combination_duration_min),
                    format_value(combination_duration_max),
                    format_value(combination_first_avg),
                    format_value(combination_first_min),
                    format_value(combination_first_max),
                    format_value(combination_last_avg),
                    format_value(combination_last_min),
                    format_value(combination_last_max),
                    str(len(results)),
                ]
            )

        elif baseline_dieff_avg is None:
            baseline_dieff_avg = combination_dieff_avg
            baseline_dieff_min = combination_dieff_min
            baseline_dieff_max = combination_dieff_max
            baseline_duration_avg = combination_duration_avg
            baseline_duration_min = combination_duration_min
            baseline_duration_max = combination_duration_max
            baseline_first_avg = combination_first_avg
            baseline_first_min = combination_first_min
            baseline_first_max = combination_first_max
            baseline_last_avg = combination_last_avg
            baseline_last_min = combination_last_min
            baseline_last_max = combination_last_max
            table_rows.append(
                [
                    combination_name,
                    *("" for _ in range(0, len(headers) - 2)),
                    str(len(results)),
                ]
            )
        else:

            def format_delta(c: float, b: float) -> str:
                if table_format == "tsv":
                    return f"{((c / b) - 1) if b != 0 else 0:.3f}"
                elif b == 0:
                    return "inf %"
                else:
                    delta = ((c / b) - 1) * 100
                    return f"{"**" if delta < 0 else ""}{delta:+.2f}{"**" if delta < 0 else ""}%"

            table_rows.append(
                [
                    combination_name,
                    format_delta(combination_dieff_avg, baseline_dieff_avg),
                    format_delta(combination_dieff_min, baseline_dieff_min),
                    format_delta(combination_dieff_max, baseline_dieff_max),
                    format_delta(combination_duration_avg, baseline_duration_avg),
                    format_delta(combination_duration_min, baseline_duration_min),
                    format_delta(combination_duration_max, baseline_duration_max),
                    format_delta(combination_first_avg, baseline_first_avg),
                    format_delta(combination_first_min, baseline_first_min),
                    format_delta(combination_first_max, baseline_first_max),
                    format_delta(combination_last_avg, baseline_last_avg),
                    format_delta(combination_last_min, baseline_last_min),
                    format_delta(combination_last_max, baseline_last_max),
                    str(len(results)),
                ]
            )

    output_rows = []

    for row in table_rows:
        match table_format:
            case "tsv":
                output_rows.append("\t".join(row))
            case "md":
                output_rows.append("| " + " | ".join(row) + " |")

    return "\n".join(output_rows) + "\n"
