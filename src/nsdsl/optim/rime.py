"""
RIME optimization algorithm — clean-room implementation.

Su, Zhao, Heidari, Liu, Zhang, Mafarja & Chen, "RIME: A physics-based optimization,"
Neurocomputing 532:183-214, 2023, DOI 10.1016/j.neucom.2023.02.010.

Physics-inspired optimizer modelling rime-ice growth. We implement its two published
operators and positive greedy selection:
  - Soft-rime search (exploration): each dimension is updated toward the best agent with a
    cosine-annealed RIME-factor when a random draw is below the environment coefficient E.
        R_new[i,j] = R_best[j] + RIME * (h*(Ub-Lb) + Lb),  RIME = r1*cos(theta)*beta,
        theta = pi * t / (10 T),  beta = 1 - floor(t*W/T)/W  (W=5),  E = sqrt(t/T).
  - Hard-rime puncture (exploitation): with probability equal to the normalised fitness,
    a dimension is replaced by the best agent's value (cross-over toward the incumbent).
RIME has public reference code; this is an independent re-implementation for a
dependency-light, equal-budget panel and is cited accordingly.

Author : Independent Research | License: MIT
"""

from __future__ import annotations

import numpy as np

POP = 20
W = 5.0


def rime(obj, bounds, budget, seed):
    rng = np.random.default_rng(seed)
    dim = len(bounds)
    lo, hi = bounds[:, 0], bounds[:, 1]
    span = hi - lo

    R = lo + span * rng.random((POP, dim))
    F = np.array([obj(x) for x in R])
    best = R[F.argmin()].copy()
    best_f = float(F.min())

    T = max(1, budget // POP)
    t = 0
    while True:
        t += 1
        E = np.sqrt(min(1.0, t / T))                         # environment coefficient
        beta = 1.0 - np.floor(t * W / T) / W                 # step-function factor
        theta = np.pi * t / (10.0 * T)
        fmin, fmax = F.min(), F.max()
        norm_f = (F - fmin) / (fmax - fmin + 1e-12)          # normalised fitness

        for i in range(POP):
            cand = R[i].copy()
            for j in range(dim):
                if rng.random() < E:                          # soft-rime search
                    r1 = rng.uniform(-1.0, 1.0)
                    rime_factor = r1 * np.cos(theta) * beta
                    h = rng.random()
                    cand[j] = best[j] + rime_factor * (h * span[j] + lo[j])
                if rng.random() < norm_f[i]:                  # hard-rime puncture
                    cand[j] = best[j]
            cand = np.clip(cand, lo, hi)
            fc = obj(cand)
            if fc < F[i]:                                     # positive greedy selection
                R[i], F[i] = cand, fc
                if fc < best_f:
                    best_f, best = fc, cand.copy()
