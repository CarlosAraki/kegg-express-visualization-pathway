"""Build visualization JSON payload from correlated data and KEGG HTML."""

from __future__ import annotations

import base64

from server.kegg.parse_areas import iter_area_geometries, map_dimensions_1x


def build_visualization_payload(
    html: str,
    area_data: dict[str, dict],
    image_bytes: bytes,
    map_id: str,
    summary: dict[str, int],
) -> dict:
    """Assemble AREAS, OVERLAY_SHAPES, bounds, and embedded image for the viewer."""
    if not area_data:
        raise ValueError("No genes correlated with this pathway")

    map_w, map_h = map_dimensions_1x(html, image_bytes)
    geometries = iter_area_geometries(html, set(area_data.keys()))

    areas: list[dict] = []
    overlay_shapes: list[dict] = []

    for item in geometries:
        area_id = item["id"]
        data = area_data[area_id]
        geom = item["geom"]
        log2 = data["log2"]
        areas.append(
            {
                "id": area_id,
                "symbols": data["symbols"],
                "entries": data["entries"],
                "log2": log2,
                "pvalue": data["pvalue"],
                "abs": data["abs"],
                "cx": geom["cx"],
                "cy": geom["cy"],
                "w": geom["w"],
                "h": geom["h"],
            }
        )
        overlay_shapes.append(
            {
                "id": area_id,
                "shape": item["shape"],
                "coords": item["coords"],
                "log2": log2,
                "pvalue": data["pvalue"],
            }
        )

    if not areas:
        raise ValueError("Correlated genes have no drawable areas on this pathway")

    log2_values = [a["log2"] for a in areas]
    pvalues = [a["pvalue"] for a in areas]
    log2_min = min(log2_values)
    log2_max = max(log2_values)
    abs_max = max(abs(log2_min), abs(log2_max))
    pvalue_min = min(pvalues)
    pvalue_max = max(pvalues)

    image_b64 = base64.b64encode(image_bytes).decode("ascii")

    return {
        "mapId": map_id,
        "mapW": map_w,
        "mapH": map_h,
        "areas": areas,
        "overlayShapes": overlay_shapes,
        "log2Min": log2_min,
        "log2Max": log2_max,
        "absMax": abs_max,
        "pvalueMin": pvalue_min,
        "pvalueMax": pvalue_max,
        "imageBase64": image_b64,
        "summary": summary,
    }
