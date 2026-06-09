"""End-to-end visualization pipeline."""

from __future__ import annotations

from server.expression.aggregate import aggregate_by_idarea
from server.expression.correlate import correlate, correlation_report
from server.expression.load_csv import CsvValidationError, load_csv_genes
from server.kegg.fetch import KeggFetchError, fetch_kegg_html, fetch_kegg_image, normalize_map_id
from server.kegg.parse_areas import load_mapdata_areas
from server.viz.build_payload import build_visualization_payload


class PipelineError(Exception):
    """User-facing pipeline failure."""

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


def _no_match_error(
    map_id: str,
    genes: list[dict[str, str]],
    areas: list[dict[str, str]],
) -> PipelineError:
    report = correlation_report(genes, areas)
    unmatched = report["unmatchedSymbols"]
    symbols_text = ", ".join(unmatched)
    message = (
        f"No genes from your CSV matched {map_id}. "
        f"Symbols not found on this pathway: {symbols_text}. "
        "KEGG requires an exact match to the label in parentheses, e.g. K04363 (PDGFRA)."
    )

    hint_lines: list[str] = []
    for symbol, options in report["suggestions"].items():
        hint_lines.append(f"{symbol} → try: {', '.join(options)}")

    if hint_lines:
        message += " Suggestions: " + "; ".join(hint_lines) + "."

    return PipelineError(
        message,
        details={
            "mapId": map_id,
            "genesInput": len(genes),
            **report,
        },
    )


def run_pipeline(pathway_input: str, csv_content: bytes | str) -> dict:
    """Fetch KEGG data, correlate genes, and return visualization payload."""
    try:
        map_id = normalize_map_id(pathway_input)
    except ValueError as exc:
        raise PipelineError(str(exc)) from exc

    try:
        html = fetch_kegg_html(map_id)
    except KeggFetchError as exc:
        raise PipelineError(str(exc)) from exc

    try:
        image_bytes = fetch_kegg_image(map_id)
    except KeggFetchError as exc:
        raise PipelineError(str(exc)) from exc

    try:
        genes = load_csv_genes(csv_content)
    except CsvValidationError as exc:
        raise PipelineError(str(exc)) from exc

    areas = load_mapdata_areas(html)
    correlated = correlate(genes, areas)

    if not correlated:
        raise _no_match_error(map_id, genes, areas)

    area_data = aggregate_by_idarea(correlated)
    summary = {
        "genesInput": len(genes),
        "genesCorrelated": len({row["symbol"] for row in correlated}),
        "areasWithData": len(area_data),
        "keggGeneAreas": len(areas),
    }

    return build_visualization_payload(
        html=html,
        area_data=area_data,
        image_bytes=image_bytes,
        map_id=map_id,
        summary=summary,
    )
