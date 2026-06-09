"""Correlate gene symbols with KEGG mapdata areas."""

from __future__ import annotations

import re

KEGG_SYMBOL_RE = re.compile(r"\(([A-Za-z0-9]+)\)")


def symbol_title_pattern(symbol: str) -> re.Pattern[str]:
    """Exact symbol match inside parentheses in KEGG area title."""
    return re.compile(r"\(" + re.escape(symbol) + r"\)")


def kegg_symbols_in_areas(areas: list[dict[str, str]]) -> set[str]:
    """Collect gene symbols referenced in KEGG area titles."""
    symbols: set[str] = set()
    for area in areas:
        symbols.update(KEGG_SYMBOL_RE.findall(area["title"]))
    return symbols


def suggest_kegg_symbols(query: str, areas: list[dict[str, str]], limit: int = 5) -> list[str]:
    """Suggest KEGG labels similar to a CSV symbol that did not match."""
    query_upper = query.upper()
    if len(query_upper) < 2:
        return []

    scored: dict[str, int] = {}
    for symbol in kegg_symbols_in_areas(areas):
        if len(symbol) < 3:
            continue
        symbol_upper = symbol.upper()
        if symbol_upper == query_upper:
            continue

        common_prefix = 0
        for left, right in zip(query_upper, symbol_upper, strict=False):
            if left != right:
                break
            common_prefix += 1

        score = 0
        if common_prefix >= 3:
            score = common_prefix
        elif len(query_upper) >= 3 and (
            query_upper in symbol_upper or symbol_upper in query_upper
        ):
            score = min(len(query_upper), len(symbol_upper))

        if score >= 3:
            scored[symbol] = score

    return [
        symbol
        for symbol, _score in sorted(
            scored.items(),
            key=lambda item: (-item[1], item[0]),
        )[:limit]
    ]


def correlation_report(
    gene_rows: list[dict[str, str]], areas: list[dict[str, str]]
) -> dict:
    """Summarize matched/unmatched symbols for user-facing errors."""
    matched_symbols: set[str] = set()
    for gene in gene_rows:
        pattern = symbol_title_pattern(gene["symbol"])
        if any(pattern.search(area["title"]) for area in areas):
            matched_symbols.add(gene["symbol"])

    unmatched = [gene["symbol"] for gene in gene_rows if gene["symbol"] not in matched_symbols]
    suggestions = {
        symbol: suggest_kegg_symbols(symbol, areas)
        for symbol in unmatched
    }
    return {
        "matchedSymbols": sorted(matched_symbols),
        "unmatchedSymbols": unmatched,
        "suggestions": {k: v for k, v in suggestions.items() if v},
    }


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
