from typing import Dict
from typing import Literal
from typing import Iterable
from itertools import groupby

from result import BenchmarkResult
from result import CombinationContainerStats
from utils import sort_labels


def uncapitalize(value: str) -> str:
    """Return the non-capitalized version."""
    return value[0].lower() + value[1:]


def template_summary_table(
    combination_results: Dict[str, Iterable[BenchmarkResult]],
    table_format: Literal["md", "tsv"],
) -> str:
    """Generate a template summary table."""

    combination_names = set()
    template_names = set()
    finished_queries: Dict[str, Dict[str, int]] = {}

    for combination_name, results in combination_results.items():
        combination_names.add(combination_name)
        finished_queries[combination_name] = {}
        for template_name, template_results in groupby(
            results, key=lambda r: r.template
        ):
            template_names.add(template_name)
            finished_queries[combination_name][template_name] = sum(
                0 if t.failed else 1 for t in template_results
            )

    template_names_sorted = sort_labels(template_names)

    headers = [
        "Combination",
        *(
            t.removeprefix("interactive-")
            .replace("short", "S")
            .replace("discover", "D")
            for t in template_names_sorted
        ),
        "Total",
    ]

    table_rows = [headers]

    if table_format == "md":
        table_rows.append(["-", *("-:" for _ in range(0, len(headers) - 1))])

    for combination_name in sort_labels(combination_names):
        column_values = []
        for t in template_names_sorted:
            column_values.append(str(finished_queries[combination_name][t]))
        table_rows.append(
            [
                combination_name,
                *column_values,
                str(sum(finished_queries[combination_name].values())),
            ]
        )

    output_rows = []

    for row in table_rows:
        match table_format:
            case "tsv":
                output_rows.append("\t".join(row))
            case "md":
                output_rows.append("| " + " | ".join(row) + " |")

    return "\n".join(output_rows) + ("\n" if table_format == "tsv" else "")


def resource_summary_table(
    combination_results: Dict[str, Iterable[BenchmarkResult]],
    combination_stats: Dict[str, Iterable[CombinationContainerStats]],
    table_format: Literal["md", "tsv"],
) -> str:
    """Generate a stats comparison table."""

    combination_names = sort_labels(combination_stats.keys())

    headers = [
        "Combination",
        "Total duration (s)",
        "Total CPU-seconds (%)",
        "Total GB-seconds",
        "Queries",
    ]

    if "baseline" in combination_names:
        headers = [
            f"Δ {uncapitalize(h)}" if h not in ("Combination", "Queries") else h
            for h in headers
        ]

    table_rows = [headers]

    if table_format == "md":
        table_rows.append(["-", *("-:" for _ in range(0, len(headers) - 1))])

    baseline_duration: float | None = None
    baseline_cpu_seconds: float | None = None
    baseline_gb_seconds: float | None = None

    for combination_name in combination_names:
        stats = combination_stats[combination_name]
        combination_duration = max(len(s.cpu_percent) for s in stats)
        combination_cpu_seconds = sum(s.cpu_seconds_percent for s in stats)
        combination_gb_seconds = sum(s.gigabyte_seconds for s in stats)

        # Without baseline present, provide raw statistics
        if "baseline" not in combination_names:

            def format_value(v: float) -> str:
                return str(round(v))

            table_rows.append(
                [
                    combination_name,
                    format_value(combination_duration),
                    format_value(combination_cpu_seconds),
                    format_value(combination_gb_seconds),
                    str(len(combination_results[combination_name])),
                ]
            )

        # With baseline present, provide statistics relative to it
        elif baseline_duration is None:
            baseline_duration = combination_duration
            baseline_cpu_seconds = combination_cpu_seconds
            baseline_gb_seconds = combination_gb_seconds
            table_rows.append(
                [
                    combination_name,
                    *("" for _ in range(0, len(headers) - 3)),
                    str(len(combination_results[combination_name])),
                ]
            )
        else:

            def format_delta(c: float, b: float) -> str:
                if table_format == "tsv":
                    delta = ((c / b) - 1) if b != 0 else 0
                    return f"{delta:+.3f}"
                elif b == 0:
                    return "inf %"
                else:
                    delta = ((c / b) - 1) * 100
                    value = f"{delta:+.0f}"
                    bold = "**" if delta < 0 else ""
                    return f"{bold}{value}{bold}%"

            table_rows.append(
                [
                    combination_name,
                    format_delta(combination_duration, baseline_duration),
                    format_delta(combination_cpu_seconds, baseline_cpu_seconds),
                    format_delta(combination_gb_seconds, baseline_gb_seconds),
                    str(len(combination_results[combination_name])),
                ]
            )

    output_rows = []

    for row in table_rows:
        match table_format:
            case "tsv":
                output_rows.append("\t".join(row))
            case "md":
                output_rows.append("| " + " | ".join(row) + " |")

    return "\n".join(output_rows) + ("\n" if table_format == "tsv" else "")


def network_summary_table(
    combination_results: Dict[str, Iterable[BenchmarkResult]],
    combination_stats: Dict[str, Iterable[CombinationContainerStats]],
    table_format: Literal["md", "tsv"],
) -> str:
    """Generate a network summary table."""

    combination_names = sort_labels(combination_results.keys())

    headers = [
        "Combination",
        "HTTP requests",
        "HTTP requests min",
        "HTTP requests max",
        "Total data transfer (GB)",
        "Queries",
    ]

    if "baseline" in combination_names:
        headers = [
            uncapitalize(h) if h not in ("Combination", "Queries") else h
            for h in headers
        ]

    table_rows = [headers]

    if table_format == "md":
        table_rows.append(["-", *("-:" for _ in range(0, len(headers) - 1))])

    baseline_http_avg: float | None = None
    baseline_http_min: float | None = None
    baseline_http_max: float | None = None
    baseline_data_transfer: float | None = None

    for combination_name in combination_names:
        results = combination_results[combination_name]
        combination_http_avg = sum(r.http_requests_avg for r in results)
        combination_http_min = sum(r.http_requests_min for r in results)
        combination_http_max = sum(r.http_requests_max for r in results)

        stats = combination_stats[combination_name]
        combination_data_transfer = sum(
            s.gigabytes_inbound + s.gigabytes_outbound for s in stats
        )

        # Without baseline present, provide raw statistics
        if "baseline" not in combination_names:

            def format_value(v: float, integer=False) -> str:
                return str(round(v)) if integer else f"{v:.3f}"

            table_rows.append(
                [
                    combination_name,
                    format_value(combination_http_avg, integer=True),
                    format_value(combination_http_min, integer=True),
                    format_value(combination_http_max, integer=True),
                    format_value(combination_data_transfer),
                    str(len(results)),
                ]
            )

        # With baseline present, provide statistics relative to it
        elif baseline_http_avg is None:
            baseline_http_avg = combination_http_avg
            baseline_http_min = combination_http_min
            baseline_http_max = combination_http_max
            baseline_data_transfer = combination_data_transfer
            table_rows.append(
                [
                    combination_name,
                    *("" for _ in range(0, len(headers) - 3)),
                    str(len(results)),
                ]
            )
        else:

            def format_delta(c: float, b: float, integer=False) -> str:
                if table_format == "tsv":
                    delta = ((c / b) - 1) if b != 0 else 0
                    value = f"{delta:+.0f}" if integer else f"{delta:+.3f}"
                    return value
                elif b == 0:
                    return "inf %"
                else:
                    delta = ((c / b) - 1) * 100
                    value = f"{delta:+.0f}" if integer else f"{delta:+.2f}"
                    bold = "**" if delta < 0 else ""
                    return f"{bold}{value}{bold}%"

            table_rows.append(
                [
                    combination_name,
                    format_delta(combination_http_avg, baseline_http_avg, integer=True),
                    format_delta(combination_http_min, baseline_http_min, integer=True),
                    format_delta(combination_http_max, baseline_http_max, integer=True),
                    format_delta(combination_data_transfer, baseline_data_transfer),
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

    return "\n".join(output_rows) + ("\n" if table_format == "tsv" else "")


def diefficiency_summary_table(
    combination_results: Dict[str, Iterable[BenchmarkResult]],
    table_format: Literal["md", "tsv"],
) -> str:
    """Generate a diefficiency summary table."""

    combination_names = sort_labels(combination_results.keys())

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
        "Results",
    ]

    if "baseline" in combination_names:
        headers = [
            f"Δ {h.lower()}" if h not in ("Combination", "Queries", "Results") else h
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
        results = combination_results[combination_name]
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

        # Without baseline present, provide raw statistics
        if "baseline" not in combination_names:

            def format_value(v: float, integer=False) -> str:
                return str(round(v)) if integer else f"{v:.3f}"

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
                    str(sum(r.result_count for r in results)),
                ]
            )

        # With baseline present, provide statistics relative to it
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
                    *("" for _ in range(0, len(headers) - 3)),
                    str(len(results)),
                    str(sum(r.result_count for r in results)),
                ]
            )
        else:

            def format_delta(c: float, b: float, integer=False) -> str:
                if table_format == "tsv":
                    delta = ((c / b) - 1) if b != 0 else 0
                    value = f"{delta:+.0f}" if integer else f"{delta:+.3f}"
                    return value
                elif b == 0:
                    return "inf %"
                else:
                    delta = ((c / b) - 1) * 100
                    value = f"{delta:+.0f}" if integer else f"{delta:+.2f}"
                    bold = "**" if delta < 0 else ""
                    return f"{bold}{value}{bold}%"

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
                    str(sum(r.result_count for r in results)),
                ]
            )

    output_rows = []

    for row in table_rows:
        match table_format:
            case "tsv":
                output_rows.append("\t".join(row))
            case "md":
                output_rows.append("| " + " | ".join(row) + " |")

    return "\n".join(output_rows) + ("\n" if table_format == "tsv" else "")
