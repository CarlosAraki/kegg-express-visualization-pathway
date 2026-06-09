"""Correlate gene symbols with KEGG mapdata areas."""

from __future__ import annotations

import re


def symbol_title_pattern(symbol: str) -> re.Pattern[str]:
    """Exact symbol match inside parentheses in KEGG area title."""
    return re.compile(r"\(" + re.escape(symbol) + r"\)")


def correlate(
    gene_rows: list[dict[str, str]], areas: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Match genes to areas; one gene may map to multiple areas."""
    rows: list[dict[str, str]] = []
    for gene in gene_rows:
        symbol = gene["symbol"]
        pattern = symbol_title_pattern(symbol)
        for area in areas:
            if not pattern.search(area["title"]):
                continue
            rows.append(
                {
                    "symbol": symbol,
                    "title": area["title"],
                    "pvalue": gene["pvalue"],
                    "log2foldchange": gene["log2foldchange"],
                    "idarea": area["idarea"],
                }
            )
    rows.sort(key=lambda row: (row["symbol"], row["idarea"]))
    return rows
