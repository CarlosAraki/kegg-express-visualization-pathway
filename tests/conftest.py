from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATHWAY_HTML = ROOT / "pathwayApp" / "pathway.html"


@pytest.fixture(scope="session")
def pathway_html() -> str:
    return PATHWAY_HTML.read_text(encoding="utf-8")
