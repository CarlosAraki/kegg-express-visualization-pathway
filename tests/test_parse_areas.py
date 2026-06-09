from pathlib import Path

from server.kegg.parse_areas import iter_area_geometries, map_dimensions_1x

ROOT = Path(__file__).resolve().parents[1]
PATHWAY_HTML = ROOT / "pathwayApp" / "pathway.html"
IMAGE_2X = ROOT / "pathwayApp" / "map05171@2x_20260606_220006.png"


def test_map_dimensions_local_2x_fixture():
    html = PATHWAY_HTML.read_text(encoding="utf-8")
    image_bytes = IMAGE_2X.read_bytes()
    map_w, map_h = map_dimensions_1x(html, image_bytes)
    assert map_w == 1769
    assert map_h == 2638


def test_iter_geometries_accepts_coords_or_data_coords(pathway_html: str):
    geometries = iter_area_geometries(pathway_html, {"8FAC7FE1"})
    assert len(geometries) == 1
    assert geometries[0]["id"] == "8FAC7FE1"
