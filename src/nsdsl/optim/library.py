"""
Optimizer panel — trusted reference implementations (Axis B).

random  : uniform random search (Bergstra & Bengio 2012) — the sanity floor.
de      : Differential Evolution (Storn & Price 1997) via scipy.optimize.
cmaes   : CMA-ES (Hansen & Ostermeier 2001) via pycma — the strongest derivative-free bar.
tpe     : Tree-structured Parzen Estimator (Bergstra 2011) via Optuna — Bayesian HPO.
pso     : Particle Swarm Optimization (Kennedy & Eberhart 1995) via pyswarms.

Each tunes the [tau, peer-weights] vector; the shared BudgetedObjective caps every optimizer at
the same number of evaluations and records the best-so-far trajectory. The hand-set baseline
(uniform weights at the calibrated tau) is the control the harness reports separately.

Author : Independent Research | License: MIT
"""

from __future__ import annotations

import numpy as np

from nsdsl.optim.base import BudgetExhausted


def random_search(obj, bounds, budget, seed):
    while True:
        obj(obj.sample())


def de(obj, bounds, budget, seed):
    from scipy.optimize import differential_evolution

    differential_evolution(
        obj,
        [tuple(b) for b in bounds],
        seed=seed,
        maxiter=10_000,
        popsize=15,
        tol=0.0,
        mutation=(0.5, 1.0),
        recombination=0.7,
        polish=False,
        init="latinhypercube",
        updating="deferred",
        workers=1,
    )


def cmaes(obj, bounds, budget, seed):
    import cma

    x0 = obj.sample()
    es = cma.CMAEvolutionStrategy(
        x0.tolist(),
        0.25,
        {
            "bounds": [bounds[:, 0].tolist(), bounds[:, 1].tolist()],
            "seed": int(seed) + 1,          # pycma requires a positive seed
            "verbose": -9,
            "maxfevals": budget,
        },
    )
    while not es.stop():
        X = es.ask()
        es.tell(X, [obj(np.asarray(x)) for x in X])


def tpe(obj, bounds, budget, seed):
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(
        direction="minimize", sampler=optuna.samplers.TPESampler(seed=seed)
    )

    def trial_fn(trial):
        x = np.array(
            [trial.suggest_float(f"x{i}", float(lo), float(hi))
             for i, (lo, hi) in enumerate(bounds)]
        )
        return obj(x)

    study.optimize(trial_fn, n_trials=budget, catch=())


def pso(obj, bounds, budget, seed):
    import pyswarms as ps

    np.random.seed(seed)                     # pyswarms draws from the global RNG
    n_particles = 10
    optimizer = ps.single.GlobalBestPSO(
        n_particles=n_particles,
        dimensions=len(bounds),
        options={"c1": 1.5, "c2": 1.5, "w": 0.7},
        bounds=(bounds[:, 0], bounds[:, 1]),
    )

    def batch(X):
        return np.array([obj(x) for x in X])

    iters = budget // n_particles + 2
    optimizer.optimize(batch, iters=iters, verbose=False)


LIBRARY_OPTIMIZERS = {
    "random": random_search,
    "de": de,
    "cmaes": cmaes,
    "tpe": tpe,
    "pso": pso,
}
