from pathlib import Path

import pytest

from server.expression.load_csv import CsvValidationError, load_csv_genes

FIXTURES = Path(__file__).parent / "fixtures"


def test_dedupe_keeps_lowest_pvalue():
    rows = load_csv_genes((FIXTURES / "sample_expression.csv").read_text())
    by_symbol = {row["symbol"]: row for row in rows}
    assert len(rows) == 2
    assert by_symbol["IL6"]["pvalue"] == "0.128"
    assert by_symbol["SELP"]["pvalue"] == "0.00113"


def test_missing_columns():
    with pytest.raises(CsvValidationError, match="missing required columns"):
        load_csv_genes("symbol,log2foldchange\nA,1.0\n")


def test_invalid_pvalue():
    with pytest.raises(CsvValidationError, match="Invalid pvalue"):
        load_csv_genes("symbol,pvalue,log2foldchange\nA,not-a-number,1.0\n")
