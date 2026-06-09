import pytest

from server.kegg.fetch import normalize_map_id


@pytest.mark.parametrize(
    "value,expected",
    [
        ("map05163", "map05163"),
        ("MAP05163", "map05163"),
        ("https://www.kegg.jp/pathway/map05163", "map05163"),
        ("https://www.genome.jp/kegg/pathway/map05171", "map05171"),
    ],
)
def test_normalize_map_id(value: str, expected: str):
    assert normalize_map_id(value) == expected


def test_normalize_map_id_invalid():
    with pytest.raises(ValueError):
        normalize_map_id("not-a-pathway")
