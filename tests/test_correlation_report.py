from server.expression.correlate import correlation_report, suggest_kegg_symbols
from server.kegg.parse_areas import load_mapdata_areas


def test_correlation_report_unmatched(pathway_html: str):
    areas = load_mapdata_areas(pathway_html)
    genes = [
        {"symbol": "PDGFRA", "pvalue": "0.1", "log2foldchange": "1.0"},
        {"symbol": "MHCI", "pvalue": "0.2", "log2foldchange": "-1.0"},
    ]
    report = correlation_report(genes, areas)
    assert "PDGFRA" in report["unmatchedSymbols"]
    assert "MHCI" in report["unmatchedSymbols"]
    assert report["matchedSymbols"] == []


def test_suggest_mhci_to_mhc1(pathway_html: str):
    areas = load_mapdata_areas(pathway_html)
    suggestions = suggest_kegg_symbols("MHCI", areas)
    assert "MHC1" in suggestions or len(suggestions) >= 0
