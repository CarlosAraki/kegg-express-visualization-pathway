"""Fetch KEGG pathway HTML and 2x PNG by map ID."""

from __future__ import annotations

import re

import httpx

MAP_ID_RE = re.compile(r"(?i)(map\d{5})")
KEGG_HTML_URL = "https://www.kegg.jp/pathway/{map_id}"
KEGG_IMAGE_2X_URL = "https://www.kegg.jp/kegg/pathway/map/{map_id}@2x.png"
KEGG_IMAGE_1X_URL = "https://www.kegg.jp/kegg/pathway/map/{map_id}.png"
USER_AGENT = "kegg-express-visualization-pathway/1.0 (academic; contact: github)"


class KeggFetchError(Exception):
    """Raised when KEGG pathway or image cannot be fetched."""


def normalize_map_id(url_or_id: str) -> str:
    """Extract map ID from a KEGG URL or bare ID (e.g. map05163)."""
    text = (url_or_id or "").strip()
    match = MAP_ID_RE.search(text)
    if not match:
        raise ValueError(f"Invalid KEGG pathway: expected map#####, got {url_or_id!r}")
    return match.group(1).lower()


def _client() -> httpx.Client:
    return httpx.Client(
        timeout=60.0,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    )


def fetch_kegg_html(map_id: str) -> str:
    """Download pathway HTML from KEGG."""
    url = KEGG_HTML_URL.format(map_id=map_id)
    with _client() as client:
        response = client.get(url)
    if response.status_code != 200:
        raise KeggFetchError(f"Pathway {map_id} not accessible (HTTP {response.status_code})")
    return response.text


def fetch_kegg_image(map_id: str) -> bytes:
    """Download pathway PNG; prefer @2x, fallback to 1x."""
    with _client() as client:
        for url in (
            KEGG_IMAGE_2X_URL.format(map_id=map_id),
            KEGG_IMAGE_1X_URL.format(map_id=map_id),
        ):
            response = client.get(url)
            if response.status_code == 200 and response.content:
                return response.content
    raise KeggFetchError(f"Pathway image for {map_id} not found")
