"""All read-decision strategies under one registry: ours + the baselines."""
from __future__ import annotations

from ..consensus.strategy import neutro_waa, neutro_wga
from .base import DecisionParams, PeerReply, Reading, Strategy
from .strategies import (
    centralized,
    lww_crdt,
    naive_cache,
    quorum_bool,
    raft_lww,
    single_peer,
)

#: name -> strategy function. The two ``neutro-*`` entries are ours; the rest are baselines.
STRATEGIES: dict[str, Strategy] = {
    "neutro-waa": neutro_waa,
    "neutro-wga": neutro_wga,
    "centralized": centralized,
    "quorum-bool": quorum_bool,
    "raft-lww": raft_lww,
    "lww-crdt": lww_crdt,
    "single-peer": single_peer,
    "naive-cache": naive_cache,
}

__all__ = ["STRATEGIES", "Strategy", "PeerReply", "Reading", "DecisionParams"]
