"""Parse KEGG pathway HTML: mapdata areas and geometry."""

from __future__ import annotations

import re
import struct

AREA_TAG_RE = re.compile(r"<area\b(?P<attrs>[^>]*?)>", re.I)
ID_RE = re.compile(r'\bid="([^"]+)"')
TITLE_RE = re.compile(r'\btitle="([^"]+)"')
HREF_RE = re.compile(r'\bhref="/entry/([^"]+)"')
SHAPE_COORDS_RE = re.compile(
    r'<area id="([^"]+)" shape="([^"]+)"(?:\s+data-coords="([^"]+)"|\s+coords="([^"]+)")'
)
PATHWAY_IMG_RE = re.compile(
    r'<img[^>]*\bid="pathwayimage"[^>]*>',
    re.I,
)
WIDTH_RE = re.compile(r'\bwidth="(\d+)"', re.I)
HEIGHT_RE = re.compile(r'\bheight="(\d+)"', re.I)
MAP_SCALE_RE = re.compile(r'<map id="mapdata"[^>]*\bdata-scale="(\d+)"', re.I)


def load_mapdata_areas(html: str) -> list[dict[str, str]]:
    """Extract human gene areas from <map id="mapdata">."""
    try:
        map_start = html.index('<map id="mapdata"')
        map_end = html.index("</map>", map_start)
    except ValueError as exc:
        raise ValueError("KEGG HTML missing mapdata") from exc

    map_html = html[map_start:map_end]
    areas: list[dict[str, str]] = []

    for match in AREA_TAG_RE.finditer(map_html):
        attrs = match.group("attrs")
        id_match = ID_RE.search(attrs)
        title_match = TITLE_RE.search(attrs)
        href_match = HREF_RE.search(attrs)
        if not id_match or not title_match:
            continue
        href = href_match.group(1) if href_match else ""
        if not href.startswith("K"):
            continue
        areas.append(
            {
                "idarea": id_match.group(1),
                "title": title_match.group(1),
            }
        )
    return areas


def png_pixel_size(image_bytes: bytes) -> tuple[int, int]:
    """Read width/height from PNG header."""
    if len(image_bytes) < 24 or image_bytes[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Downloaded pathway image is not a valid PNG")
    width, height = struct.unpack(">II", image_bytes[16:24])
    return width, height


def map_dimensions_1x(html: str, image_bytes: bytes) -> tuple[float, float]:
    """
    Return 1x map dimensions for overlay and 3D layout.

    Overlay coordinates are always 1x. When the downloaded PNG is @2x,
    halve its pixel size. Live KEGG HTML often exposes only 1x width.
    """
    png_w, png_h = png_pixel_size(image_bytes)
    scale_match = MAP_SCALE_RE.search(html)
    html_scale = int(scale_match.group(1)) if scale_match else None

    img_match = PATHWAY_IMG_RE.search(html)
    html_w: float | None = None
    html_h: float | None = None
    if img_match:
        tag = img_match.group(0)
        width_match = WIDTH_RE.search(tag)
        height_match = HEIGHT_RE.search(tag)
        if width_match:
            html_w = float(width_match.group(1))
        if height_match:
            html_h = float(height_match.group(1))

    if html_scale == 1 and html_w is not None and abs(html_w - png_w) <= 2:
        return html_w, float(png_h)

    if html_w is not None and html_h is not None:
        if html_scale == 2 or html_w > png_w:
            return html_w / 2, html_h / 2
        return html_w, html_h

    if html_w is not None and abs(html_w - png_w / 2) <= 2:
        return html_w, float(png_h / 2)

    if png_w > 2500:
        return png_w / 2, png_h / 2

    return float(png_w), float(png_h)


def parse_area_geometry(shape: str, coords: str) -> dict | None:
    """Convert data-coords (1x) to center + size for 3D bars."""
    parts = [float(v) for v in coords.split(",")]
    if shape == "circle" and len(parts) >= 3:
        cx, cy, r = parts[0], parts[1], parts[2]
        return {"cx": cx, "cy": cy, "w": r * 2, "h": r * 2, "shape": "circle"}
    if shape == "rect" and len(parts) >= 4:
        x1, y1, x2, y2 = parts[0], parts[1], parts[2], parts[3]
        return {
            "cx": (x1 + x2) / 2,
            "cy": (y1 + y2) / 2,
            "w": abs(x2 - x1),
            "h": abs(y2 - y1),
            "shape": "rect",
        }
    return None


def iter_area_geometries(html: str, area_ids: set[str]) -> list[dict]:
    """Collect geometry + overlay data for correlated area IDs."""
    geometries: list[dict] = []
    for match in SHAPE_COORDS_RE.finditer(html):
        area_id, shape = match.group(1), match.group(2)
        coords = match.group(3) or match.group(4) or ""
        if area_id not in area_ids:
            continue
        parts = [float(v) for v in coords.split(",")]
        if shape == "circle" and len(parts) < 3:
            continue
        if shape == "rect" and len(parts) < 4:
            continue
        geom = parse_area_geometry(shape, coords)
        if not geom:
            continue
        geometries.append(
            {
                "id": area_id,
                "shape": shape,
                "coords": parts,
                "geom": geom,
            }
        )
    return geometries
