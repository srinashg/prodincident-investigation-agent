from app.state import calculate_p95


def test_calculate_p95_returns_slow_tail_value():
    values = [100.0] * 19 + [4000.0]
    assert calculate_p95(values) == 100.0


def test_calculate_p95_for_sustained_latency():
    values = [4000.0] * 20
    assert calculate_p95(values) == 4000.0
