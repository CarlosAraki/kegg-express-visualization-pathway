from server.expression.correlate import correlate, symbol_title_pattern
from server.kegg.parse_areas import load_mapdata_areas


def test_symbol_title_pattern_exact_match():
    assert symbol_title_pattern("SELP").search("K06496 (SELP)")
    assert not symbol_title_pattern("SELP").search("K06496 (SEL)")
    assert not symbol_title_pattern("IL6").search("K05055 (IL6R)")


def test_correlate_matches_known_genes(pathway_html: str):
    areas = load_mapdata_areas(pathway_html)
    genes = [
        {"symbol": "ACE", "pvalue": "0.1", "log2foldchange": "0.5"},
        {"symbol": "IL6R", "pvalue": "0.2", "log2foldchange": "-0.3"},
        {"symbol": "NOTREAL", "pvalue": "0.01", "log2foldchange": "1.0"},
    ]
    rows = correlate(genes, areas)
    symbols = {row["symbol"] for row in rows}
    assert "ACE" in symbols
    assert "IL6R" in symbols
    assert "NOTREAL" not in symbols
    assert all(row["idarea"] for row in rows)
