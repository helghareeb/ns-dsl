"""S3 ("White Friday") clone catch-up: quantify how a fresh replica reconverges via log replay.

A clone boots empty (every key DEFAULT) and replays the logs-as-DSL stream one event at a time.
After each replayed event we measure (i) how much true state it has recovered and (ii) the
cluster's consensus acceptance with the clone participating. Under the conservative SVNNWGA the
clone drags consensus to reject until it catches up; under the optimistic SVNNWAA the established
peers carry the decision throughout -- the two operators' behavior under cloning, made quantitative.
Output: results/tables/s3_convergence.csv.
"""
from __future__ import annotations

import csv
from pathlib import Path

from nsdsl.consensus import Peer, run_round
from nsdsl.consensus.replay import apply_event, item_key
from nsdsl.oracle import GodLog, Oracle
from nsdsl.state_store import NeutrosophicStateStore

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables" / "s3_convergence.csv"
N_KEYS = 50
N_ESTABLISHED = 5
TAU = 0.5


def _event(i: int) -> str:
    return f'{{"guid":"k{i}","cartItems":[{{"item":"v{i}","status":"(1,0,0)"}}],"nodeID":"1"}}'


def _keys() -> list[str]:
    return [item_key(f"k{i}", "item") for i in range(N_KEYS)]


def main() -> None:
    events = [_event(i) for i in range(N_KEYS)]
    keys = _keys()

    oracle_log = GodLog()
    established = [Peer(f"e{j}", NeutrosophicStateStore()) for j in range(N_ESTABLISHED)]
    for i, ev in enumerate(events):
        oracle_log.append(keys[i], f"v{i}")          # ground truth
        for p in established:
            apply_event(p.store, ev)                 # established peers are fully caught up
    oracle = Oracle(oracle_log)

    clone = Peer("clone", NeutrosophicStateStore())
    peers = [*established, clone]

    rows = []
    for m in range(N_KEYS + 1):
        recovered = sum(1 for i, k in enumerate(keys)
                        if clone.store.get(k).value == oracle.true_value(k))
        wga_acc = sum(1 for k in keys if run_round(peers, k, method="wga", tau=TAU).accept)
        waa_acc = sum(1 for k in keys if run_round(peers, k, method="waa", tau=TAU).accept)
        rows.append({"events_replayed": m,
                     "recovery_fraction": round(recovered / N_KEYS, 4),
                     "wga_accept_rate": round(wga_acc / N_KEYS, 4),
                     "waa_accept_rate": round(waa_acc / N_KEYS, 4)})
        if m < N_KEYS:
            apply_event(clone.store, events[m])      # replay the next log event

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    converged = next(r["events_replayed"] for r in rows if r["wga_accept_rate"] >= 0.95)
    print(f"s3 convergence -> {OUT}; WGA reaches 95% acceptance after {converged} events "
          f"(of {N_KEYS}); WAA stays >= {min(r['waa_accept_rate'] for r in rows):.2f} throughout")


if __name__ == "__main__":
    main()
