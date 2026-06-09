"""Aggregate correlated rows by idarea."""

from __future__ import annotations

from collections import defaultdict


def aggregate_by_idarea(rows: list[dict[str, str]]) -> dict[str, dict]:
    """Group by idarea: mean log2, min pvalue, per-gene entries."""
    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        buckets[row["idarea"]].append(row)

    result: dict[str, dict] = {}
    for area_id, area_rows in buckets.items():
        log2_values = [float(row["log2foldchange"]) for row in area_rows]
        pvalues = [float(row["pvalue"]) for row in area_rows]
        entries = [
            {
                "symbol": row["symbol"],
                "log2": float(row["log2foldchange"]),
                "pvalue": float(row["pvalue"]),
            }
            for row in area_rows
        ]
        log2 = sum(log2_values) / len(log2_values)
        result[area_id] = {
            "log2": log2,
            "pvalue": min(pvalues),
            "symbols": [row["symbol"] for row in area_rows],
            "entries": entries,
            "abs": abs(log2),
        }
    return result
