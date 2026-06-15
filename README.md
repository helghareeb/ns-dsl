# ns-dsl — A Neutrosophic Consensus Layer for Global-State Decisions in Microservices

Research software backing an extended journal paper (target: *Future Generation Computer
Systems*, Elsevier, Q1). It implements and **empirically evaluates** the ideas first sketched
conceptually in:

> H. A. El-Ghareeb, *"Neutrosophic-based domain-specific languages and rules engine to ensure
> data sovereignty and consensus achievement in microservices architecture,"* in *Optimization
> Theory Based on Neutrosophic and Plithogenic Sets*, Elsevier, 2020, ch. 2, pp. 22–43.
> DOI: [10.1016/B978-0-12-819670-0.00002-0](https://doi.org/10.1016/B978-0-12-819670-0.00002-0).

The 2020 chapter is purely conceptual (no implementation, no experiments). **This repository is
the fresh, reproducible artifact** that turns those ideas into running, measured code.

## What this is

Each data item in a microservice carries a **single-valued neutrosophic triple** `(T, I, F)`
describing its persistence status:

| State | `(T, I, F)` | Meaning |
|-------|-------------|---------|
| `PERSISTED` | `(1, 0, 0)` | committed to the database |
| `CACHED`    | `(0, 1, 0)` | in cache only (unconfirmed) |
| `DEFAULT`   | `(0, 0, 1)` | neither seen nor persisted |

> Note: the 2020 chapter prints `DEFAULT` as `(0,1,0)`, duplicating `CACHED`. We implement the
> intended `(0,0,1)` (falsity = "never seen") and document this as a corrected erratum — a missing
> or late peer must read as *falsity*, not *indeterminacy*.

Peer microservices fuse their `(T,I,F)` views of global state with the **SVNNWAA** (weighted
arithmetic) and **SVNNWGA** (weighted geometric) aggregation operators, deneutrosophize the
result with a score function, and decide — **without a central authority**. This is a per-item
**freshness/consistency decision layer**; it sits *above* the consistency substrate and is **not**
a replacement for a replication/consensus protocol (Raft/Paxos). See the manuscript for the exact
positioning and honest-claim framing.

## Layout

```
src/nsdsl/      core library: neutro/ dsl/ rules/ consensus/ bus/ oracle/ baselines/
services/       FastAPI e-Commerce microservices (products/orders/users/frontend)
docker/         Docker Compose testbed (+ redis event bus, + postgres, + toxiproxy faults)
grammar/        ANTLR JSON grammar + pinned jar
experiments/    harness + the single canonical aggregator (analyze_results.py)
config/         calibration.json (content-hashed) + scenario/experiment configs
datasets/       seeded synthetic-data generator
paper/          elsarticle manuscript + continuity docs
tests/          pytest suite (mirrors src/)
```

## Quick start

```bash
make dev          # pip install -e '.[dev]'
make test         # run the test suite
make smoke        # import-check the core
```

Reproducing the paper's numbers end-to-end is documented in [REPRODUCE.md](REPRODUCE.md).

## License

MIT (see `LICENSE`). Every numeric claim in the paper is regenerable from committed code +
`config/calibration.json` (SHA-256 stamped into every results CSV) + a recorded seed.
