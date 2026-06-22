"""All read-decision strategies under one registry: ours + the baselines."""
from __future__ import annotations

from ..consensus.strategy import (
    GRADED_STRATEGIES,
    SCORE_PANEL_STRATEGIES,
    neutro_waa,
    neutro_wga,
)
from .base import DecisionParams, PeerReply, Reading, Strategy
from .strategies import (
    centralized,
    freshness_slo,
    lww_crdt,
    naive_cache,
    pbs_quorum,
    quorum_bool,
    raft_lww,
    single_peer,
)

#: name -> strategy function. The submitted crisp ``neutro-waa``/``neutro-wga`` are ours; the
#: ``neutro-<op>-g`` entries are the Axis-A operator panel under the graded encoding (G1); the rest
#: are baselines.
STRATEGIES: dict[str, Strategy] = {
    "neutro-waa": neutro_waa,
    "neutro-wga": neutro_wga,
    **GRADED_STRATEGIES,
    **SCORE_PANEL_STRATEGIES,
    "centralized": centralized,
    "quorum-bool": quorum_bool,
    "pbs-quorum": pbs_quorum,
    "raft-lww": raft_lww,
    "lww-crdt": lww_crdt,
    "freshness-slo": freshness_slo,
    "single-peer": single_peer,
    "naive-cache": naive_cache,
}

__all__ = ["STRATEGIES", "Strategy", "PeerReply", "Reading", "DecisionParams"]
