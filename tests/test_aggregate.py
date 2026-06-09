from server.expression.aggregate import aggregate_by_idarea


def test_aggregate_mean_log2_min_pvalue():
    rows = [
        {
            "symbol": "A",
            "title": "t",
            "pvalue": "0.5",
            "log2foldchange": "1.0",
            "idarea": "X1",
        },
        {
            "symbol": "B",
            "title": "t",
            "pvalue": "0.1",
            "log2foldchange": "3.0",
            "idarea": "X1",
        },
    ]
    result = aggregate_by_idarea(rows)
    assert result["X1"]["log2"] == 2.0
    assert result["X1"]["pvalue"] == 0.1
    assert len(result["X1"]["entries"]) == 2
