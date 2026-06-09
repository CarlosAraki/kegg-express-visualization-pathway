"""Regression against reference silver_pathway_areasv1.csv for map05171."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from server.expression.aggregate import aggregate_by_idarea
from server.expression.correlate import correlate
from server.expression.load_csv import load_csv_genes
from server.kegg.parse_areas import load_mapdata_areas

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_CSV = ROOT / "pathwayApp" / "silver_pathway_areasv1.csv"
PATHWAY_HTML = ROOT / "pathwayApp" / "pathway.html"


@pytest.fixture(scope="module")
def pathway_html() -> str:
    return PATHWAY_HTML.read_text(encoding="utf-8")


def _load_reference_rows() -> list[dict[str, str]]:
    with REFERENCE_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _genes_from_reference() -> list[dict[str, str]]:
    best: dict[str, dict[str, str]] = {}
    for row in _load_reference_rows():
        symbol = row["symbol"]
        current = best.get(symbol)
        if current is None or float(row["pvalue"]) < float(current["pvalue"]):
            best[symbol] = {
                "symbol": symbol,
                "pvalue": row["pvalue"],
                "log2foldchange": row["log2foldchange"],
            }
    return list(best.values())


def test_map05171_correlation_matches_reference(pathway_html: str):
    if not REFERENCE_CSV.exists():
        pytest.skip("Reference CSV not available")

    reference = _load_reference_rows()
    genes = _genes_from_reference()
    areas = load_mapdata_areas(pathway_html)
    computed = correlate(genes, areas)

    ref_keys = {(r["symbol"], r["idarea"]) for r in reference}
    comp_keys = {(r["symbol"], r["idarea"]) for r in computed}
    assert comp_keys == ref_keys


def test_map05171_aggregation_matches_reference(pathway_html: str):
    if not REFERENCE_CSV.exists():
        pytest.skip("Reference CSV not available")

    reference = _load_reference_rows()
    genes = _genes_from_reference()
    areas = load_mapdata_areas(pathway_html)
    correlated = correlate(genes, areas)
    aggregated = aggregate_by_idarea(correlated)

    ref_buckets: dict[str, list[float]] = {}
    ref_pvalues: dict[str, list[float]] = {}
    for row in reference:
        ref_buckets.setdefault(row["idarea"], []).append(float(row["log2foldchange"]))
        ref_pvalues.setdefault(row["idarea"], []).append(float(row["pvalue"]))

    for area_id, log2_values in ref_buckets.items():
        expected_log2 = sum(log2_values) / len(log2_values)
        expected_p = min(ref_pvalues[area_id])
        assert area_id in aggregated
        assert abs(aggregated[area_id]["log2"] - expected_log2) < 1e-9
        assert aggregated[area_id]["pvalue"] == expected_p
