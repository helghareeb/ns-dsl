# 2026 Currency Update — Related Work, Datasets, Baselines, Venue

Companion to `related_work_scan.md`. Findings from a 2026 literature/dataset sweep used to position
the extended paper. Citations web-verified; uncertain items marked **(verify)**.

## 1. 2026 framing hooks (the paper connects to a 4-way 2024–2026 convergence)

**(a) Agentic / multi-agent LLM systems over shared, possibly-stale world-state — strongest hook.**
The multi-agent-memory community is importing distributed-systems consistency vocabulary; our
per-item `(T,I,F)` act-vs-abstain is the decision primitive they reach toward.
- Yu et al., "Multi-Agent Memory from a Computer Architecture Perspective," arXiv:2603.10062, 2026 —
  names multi-agent memory *consistency* as the top open challenge.
- Chang et al., "SagaLLM: ... Transaction Guarantees for Multi-Agent LLM Planning," PVLDB 18, 2025,
  DOI 10.14778/3750601.3750611 — we are the decentralized freshness judgment above its validators.
- Pugachev, "CodeCRDT," arXiv:2510.18893, 2025 — CRDTs converge but don't decide freshness-to-act.
- Helmi, "Modeling Response Consistency in Multi-Agent LLM Systems," arXiv:2504.07303, 2025.

**(b) Edge-cloud continuum / serverless-FaaS state.** GoldFish (IoT 2024, arXiv:2412.02867); Truffle
(arXiv:2411.16451, 2024); Cloudburst (PVLDB 13(12), 2020, DOI 10.14778/3407790.3407836).

**(c) ML feature-store freshness — best vocabulary match.** Hopsworks Feature Store (SIGMOD '24
Companion, DOI 10.1145/3626246.3653389); RALF (PVLDB 17(3):563–576, 2024,
DOI 10.14778/3632093.3632116) — also our headline modern baseline (§4).

**(d) Microservice data-consistency surveys.** Laigner et al. (PVLDB 14(13), 2021,
DOI 10.14778/3484224.3484232); Online Marketplace benchmark (SIGMOD 2025, arXiv:2403.12605);
Rodrigues et al. SLR (JSS 230, 2025, DOI 10.1016/j.jss.2025.112500).

## 2. Real datasets to replace the synthetic workload (#1 weakness)

- **Cache traces:** Twitter cache-trace (OSDI '20, CC-BY 4.0, github.com/twitter/cache-trace) — best
  source for key-Zipf skew, read/write split, TTL→freshness; calibrates the **dirty-read rate**.
  Also cacheMon `cache_dataset`, Wikimedia CDN 2019.
- **Microservice call-graphs:** Alibaba cluster-trace-microservices-**v2022** (13 days, DB+memcached
  read/write) and v2021 — github.com/alibaba/clusterdata. (Confirmed: no v2023.) Google ClusterData.
- **Fraud (S2):** IEEE-CIS (590k, isFraud); ULB credit-card (284k, DbCL); PaySim (open simulator,
  TRANSFER→CASH_OUT read-after-write chains).
- **Retail/pricing (S1):** UCI Online Retail II (direct download); Instacart; Olist.
- **IoT (new domain):** Intel Lab Data (54 sensors, direct download, dropouts exercise the I axis).

Replay via a WikiBench-style harness preserving inter-arrival + popularity.

## 3. Additional domains (generality)
IoT telemetry (Intel Lab); social-feed freshness; ML feature serving (Feast + NYC TLC vs RALF);
healthcare/banking asymmetric-cost (MIMIC-IV, credentialed; PaySim/IEEE-CIS open); multi-agent
coordination (Melting Pot, SMAC).

## 4. Recent baselines / competitors (2023–2026)
- **RALF** (PVLDB 2024) — strongest direct modern baseline: centralized accuracy-aware staleness
  scheduler vs our decentralized peer-fused gate.
- CTuner (Internetware 2024, DOI 10.1145/3671016.3674809); RL IoT-consistency (Sci. Reports 2025,
  DOI 10.1038/s41598-025-09698-1 **(verify)**); Pileus/Tuba/Consistency-Rationing lineage; PBS
  (deepen single-probability vs T/I/F contrast).
- **Honest gap:** no 2023–2026 work fuses fuzzy/neutrosophic logic with microservice cache
  consistency — this is our novelty.

## 5. Microservice benchmarks
DeathStarBench (active) + Train Ticket (41 services, fault-replicate) as headline testbeds; Online
Boutique / TeaStore as clean secondary. **Sock Shop is defunct (2024)** — do not adopt.

## 6. Venue (2026)
Information Sciences (~8.1, strongest neutrosophic/decision fit, **chosen**) > FGCS (6.1, systems) >
IEEE TSC (~5.8) > JSS (~5) > IEEE Access (3.6, fast fallback). Zenodo accepted everywhere; no
mandatory artifact badges. Route by lead: theory/neutrosophic → Information Sciences.

## Top 5 highest-leverage moves
1. Real traces (Twitter cache + Alibaba v2022 + IEEE-CIS/PaySim) — kills the #1 weakness.
2. Add RALF as headline modern baseline; deepen PBS contrast.
3. Run on DeathStarBench + Train Ticket.
4. Add 2+ domains (IoT, feature serving).
5. Frame intro around the 4-way convergence; ship a Zenodo-DOI artifact.
