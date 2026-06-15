"""Guards for the latency testbed and Tier-B sweep wiring (no network / no full run)."""
from __future__ import annotations

from bench import latency_bench as lb
from bench.peer_server import app
from nsdsl.baselines import STRATEGIES


def test_latency_classes_cover_every_strategy_once():
    classes = lb.ONE_HOP | lb.ALL_HOPS | lb.MAJORITY | lb.LOCAL
    assert classes == set(STRATEGIES)
    # mutually exclusive
    total = len(lb.ONE_HOP) + len(lb.ALL_HOPS) + len(lb.MAJORITY) + len(lb.LOCAL)
    assert total == len(STRATEGIES)


def test_peer_server_exposes_routes():
    paths = {r.path for r in app.routes}
    assert "/health" in paths
    assert "/view/{pid}" in paths


def test_build_app_is_constructable():
    a = lb.build_app()
    assert {"/health", "/view/{pid}"} <= {r.path for r in a.routes}
