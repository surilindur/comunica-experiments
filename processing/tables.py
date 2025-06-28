"""Utility functions for generating tables of summaries."""

from typing import Set
from typing import Dict
from typing import List
from typing import Iterable

from numpy import mean

from utils import sort_labels
from jbrcsv import JbrQuery
from jbrstats import JbrStats
from analysis import calculate_diefficiency_at_full_results


def generate_combination_comparison_table(
    all_queries: Iterable[JbrQuery],
    successful_queries: Iterable[JbrQuery],
    stats: Iterable[JbrStats],
) -> Iterable[Iterable[str]]:
    """Generate a table for comparing combination metrics with each other."""

    table_cells: List[List[str]] = [
        [
            "Combination",
            "Duration (s)",
            "First result (s)",
            "Last result (s)",
            "dieff@full",
            "HTTP requests",
            "CPU-seconds (%)",
            "GB-seconds",
            "Network ingress (GB)",
            "Network egress (GB)",
            "Total results",
            # "Queries faster than baseline",
            # "Queries slower than baseline",
            "Successgul queries",
        ]
    ]

    query_names: Set[str] = set()
    combination_successes: Dict[str, int] = {}
    combination_stats: Dict[str, JbrStats] = {}
    combination_queries: Dict[str, Dict[str, JbrQuery]] = {}

    baseline_mappings: Dict[str, str] = {}

    def find_baseline(name: str) -> str:
        for key, value in baseline_mappings.items():
            if name.endswith(key):
                return value
        return sort_labels([*baseline_mappings.values()])[0]

    for q in all_queries:
        query_names.add(q.name)
        if q.combination.startswith("baseline"):
            baseline_mappings[q.combination.removeprefix("baseline")] = q.combination
        if q.combination not in combination_successes:
            combination_successes[q.combination] = 0
        if not q.failed:
            combination_successes[q.combination] += 1

    for q in successful_queries:
        if q.combination not in combination_queries:
            combination_queries[q.combination] = {}
        combination_queries[q.combination][q.name] = q

    for s in stats:
        combination_stats[s.combination] = s

    combination_names = sort_labels(list(combination_queries.keys()))

    for combination in combination_names:
        c_durations: List[float] = []
        c_first_results: List[float] = []
        c_last_results: List[float] = []
        c_dieff_fulls: List[float] = []
        c_http_reqs: List[float] = []
        c_total_results: float = 0
        c_successful: int = combination_successes[combination]

        c_faster_than_baseline: int = 0
        c_slower_than_baseline: int = 0

        for q in combination_queries[combination].values():
            c_durations.append(q.duration_avg)
            c_http_reqs.append(q.http_requests_avg)
            c_total_results += q.results_avg
            for t_replication in q.timestamps:
                c_first_results.append(t_replication[0])
                c_last_results.append(t_replication[-1])
                c_dieff_fulls.append(
                    calculate_diefficiency_at_full_results(t_replication)
                )
            if "baseline" not in q.name:
                q_baseline_combination = find_baseline(q.name)
                q_baseline = combination_queries[q_baseline_combination][q.name]
                if q.duration_avg < q_baseline.duration_avg:
                    c_faster_than_baseline += 1
                elif q.duration_avg > q_baseline.duration_avg:
                    c_slower_than_baseline += 1

        c_stat = combination_stats[combination]

        table_cells.append(
            [
                combination,
                f"{mean(c_durations):.2f}",
                f"{mean(c_first_results):.2f}",
                f"{mean(c_last_results):.2f}",
                f"{mean(c_dieff_fulls):.2f}",
                f"{mean(c_http_reqs):.2f}",
                f"{c_stat.cpu_seconds_percent:.2f}",
                f"{c_stat.gigabyte_seconds:.2f}",
                f"{c_stat.gigabytes_inbound:.2f}",
                f"{c_stat.gigabytes_outbound:.2f}",
                f"{c_total_results:.0f}",
                # f"{c_faster_than_baseline:.0f}",
                # f"{c_slower_than_baseline:.0f}",
                f"{c_successful} / {len(query_names)}",
            ]
        )

    return table_cells
