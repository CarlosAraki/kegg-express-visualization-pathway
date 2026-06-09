"""Load and validate expression CSV; dedupe by symbol (min p-value)."""

from __future__ import annotations

import csv
import io
from typing import BinaryIO, TextIO

REQUIRED_COLUMNS = ("symbol", "pvalue", "log2foldchange")


class CsvValidationError(Exception):
    """Raised when the uploaded CSV is invalid."""


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_pvalue(value: str) -> float:
    parsed = _safe_float(value)
    return parsed if parsed is not None else float("inf")


def load_csv_genes(source: str | TextIO | BinaryIO) -> list[dict[str, str]]:
    """
    Parse CSV keeping only symbol, pvalue, log2foldchange.
    One row per symbol; duplicates keep the lowest p-value.
    """
    if isinstance(source, (bytes, bytearray)):
        text = source.decode("utf-8-sig")
        handle: TextIO = io.StringIO(text)
    elif isinstance(source, str):
        handle = io.StringIO(source)
    else:
        handle = source  # type: ignore[assignment]

    reader = csv.DictReader(handle)
    if not reader.fieldnames:
        raise CsvValidationError("CSV is empty or missing a header row")

    normalized = {name.strip().lower(): name for name in reader.fieldnames}
    missing = [col for col in REQUIRED_COLUMNS if col not in normalized]
    if missing:
        raise CsvValidationError(
            f"CSV missing required columns: {', '.join(missing)}"
        )

    best: dict[str, dict[str, str]] = {}
    row_count = 0

    for row in reader:
        row_count += 1
        symbol = (row.get(normalized["symbol"]) or "").strip()
        if not symbol:
            continue

        pvalue_raw = row.get(normalized["pvalue"], "")
        log2_raw = row.get(normalized["log2foldchange"], "")
        if _safe_float(pvalue_raw) is None:
            raise CsvValidationError(
                f"Invalid pvalue for symbol {symbol!r} at row {row_count + 1}"
            )
        if _safe_float(log2_raw) is None:
            raise CsvValidationError(
                f"Invalid log2foldchange for symbol {symbol!r} at row {row_count + 1}"
            )

        record = {
            "symbol": symbol,
            "pvalue": str(pvalue_raw).strip(),
            "log2foldchange": str(log2_raw).strip(),
        }
        current = best.get(symbol)
        if current is None or _safe_pvalue(record["pvalue"]) < _safe_pvalue(
            current["pvalue"]
        ):
            best[symbol] = record

    if not best:
        raise CsvValidationError("CSV contains no valid gene rows")

    return list(best.values())
