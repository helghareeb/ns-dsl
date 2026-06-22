"""
Ninja Optimization Algorithm (NiOA) — clean-room implementation.

El-Kenawy, Rizk, Zaki, Elshabrawy, Ibrahim, Abdelhamid, Khodadadi, ALmetwally & Eid,
"NiOA: A Novel Metaheuristic Algorithm Modeled on the Stealth and Precision of Japanese
Ninjas," J. Artificial Intelligence in Engineering Practice 1(2):17-35, 2024,
DOI 10.21608/jaiep.2024.386693.

HONESTY (R1, N14, Sörensen 2015): NiOA has NO public reference implementation, and the
source (and the application papers that reuse it) omit exact operator coefficients and
annealing schedules. We therefore reconstruct NiOA from its published *structural*
description and DISCLOSE every coefficient here. Consequently NiOA is treated as a
PROVISIONAL panel member and a hypothesis under test — never a hero method, and no NiOA
number is reported without this frozen implementation. The published structure we follow:
  - Exploration ("stealth scan"): (A) a difference-vector move between two random agents
    scaled stochastically, and (B) a cosine-oscillation move toward the incumbent best
    (reaches distant regions).
  - Exploitation ("precision"): (A) small annealed local refinement around the best, and
    (B) a non-linear adaptive pull toward the best.
  - Mutation: controlled per-dimension randomization.
  - Resource/best update with a 3-iteration no-improvement regroup criterion.
An exploration->exploitation envelope E = cos((pi/2) * progress) anneals from 1 to 0.

Author : Independent Research | License: MIT
"""

from __future__ import annotations

import numpy as np

POP = 20
MUTATION_RATE = 0.10
REGROUP_PATIENCE = 3


def nioa(obj, bounds, budget, seed):
    rng = np.random.default_rng(seed)
    dim = len(bounds)
    lo, hi = bounds[:, 0], bounds[:, 1]
    span = hi - lo

    X = lo + span * rng.random((POP, dim))
    F = np.array([obj(x) for x in X])
    best = X[F.argmin()].copy()
    best_f = float(F.min())
    no_improve = 0

    while True:
        progress = obj.n / budget
        envelope = np.cos(0.5 * np.pi * progress)        # 1 (explore) -> 0 (exploit)
        improved = False

        for i in range(POP):
            if rng.random() < envelope:                   # ── stealth scan (explore) ──
                if rng.random() < 0.5:
                    a, b = rng.integers(0, POP, size=2)
                    cand = best + rng.random() * (X[a] - X[b])
                else:
                    theta = 2.0 * np.pi * rng.random()
                    cand = X[i] + rng.random() * np.cos(theta) * (best - X[i])
            else:                                          # ── precision (exploit) ──
                if rng.random() < 0.5:
                    step = 0.2 * (1.0 - progress)
                    cand = best + step * span * (rng.random(dim) - 0.5)
                else:
                    gamma = 1.0 + rng.random()
                    cand = X[i] + rng.random() * (best - X[i]) * (rng.random(dim) ** gamma)

            if rng.random() < MUTATION_RATE:               # ── mutation ──
                j = rng.integers(0, dim)
                cand[j] = lo[j] + span[j] * rng.random()

            cand = np.clip(cand, lo, hi)
            fc = obj(cand)
            if fc < F[i]:                                  # positive greedy selection
                X[i], F[i] = cand, fc
                if fc < best_f:
                    best_f, best, improved = fc, cand.copy(), True

        no_improve = 0 if improved else no_improve + 1
        if no_improve >= REGROUP_PATIENCE:                 # ── regroup around best ──
            worst = F.argsort()[POP // 2:]
            for w in worst:
                X[w] = np.clip(best + 0.1 * span * (rng.random(dim) - 0.5), lo, hi)
                F[w] = obj(X[w])
            no_improve = 0
