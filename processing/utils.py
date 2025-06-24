"""Helper functions for small repetitive tasks."""

from typing import Sequence

from natsort import natsorted


def sort_labels(labels: Sequence[str]) -> Sequence[str]:
    """
    Sort labels in a human-intuitive way using the natsorted library.
    Labels for baseline and overhead measurements are moved to the beginning.
    """

    baseline_labels: Sequence[str] = []
    overhead_labels: Sequence[str] = []
    other_labels: Sequence[str] = []

    for label in labels:
        if "baseline" in label:
            baseline_labels.append(label)
        elif "overhead" in label:
            overhead_labels.append(label)
        else:
            other_labels.append(label)

    return list(
        (
            *natsorted(baseline_labels),
            *natsorted(overhead_labels),
            *natsorted(other_labels),
        )
    )
