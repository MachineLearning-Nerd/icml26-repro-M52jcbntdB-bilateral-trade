"""Claim-by-claim reproduction campaign for arXiv:2602.05681.

The fixed OpenResearch command invokes this file on every experiment node.  It
generates durable text evidence under ``.openresearch/artifacts``, runs a
failure-sensitive verifier and an independent checker for every claim, and
requires deliberately broken negative controls to be rejected.
"""

from __future__ import annotations

import csv
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any

import numpy as np
from scipy.stats import beta as beta_distribution

sys.path.insert(0, os.path.dirname(__file__))
import bilateral as bt


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / ".openresearch" / "artifacts"
SEEDS = list(range(12))
DELTA = 0.05
FIXED_COMMAND = "uv sync --frozen && .venv/bin/python repro/src/verify_bt.py"

CLAIMS = {
    1: "Under bounded density, Algorithm 1 is GBB and has soft-O(T^(3/4)) regret (Theorem 4.1).",
    2: "Without bounded density, every algorithm has an Omega(T) instance via the needle construction (Theorem 3.1).",
    3: "Directed KxK discretization loses O(log(T)/K) under bounded density (Lemmas 5.1-5.2).",
    4: "Conditional Profit-Max phase regret is soft-O(beta + T/K + sqrt(KT log(1/delta))) (Lemmas 7.1-7.2).",
    5: "Algorithm 2 estimates both non-observable components on all K^2 pairs in exactly 2KN rounds (Lemmas 8.1-8.2).",
    6: "Algorithm 3 has soft-O(K sqrt(T log(1/delta))) biased-reward regret and profit shortfall (Lemma 9.1).",
}

SOURCE_ANCHORS = {
    1: "#S4.Thmtheorem1; proof #A6; Algorithm #alg1",
    2: "#S3.Thmtheorem1; proof #A1",
    3: "#S5.Thmtheorem1 and #S5.Thmtheorem2; proof #A2",
    4: "#S7.Thmtheorem1 and #S7.Thmtheorem2; Algorithm #alg4",
    5: "#S8.Thmtheorem1 and #S8.Thmtheorem2; Algorithm #alg2",
    6: "#S9.Thmtheorem1; proof #A5; Algorithm #alg3",
}


def to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_jsonable(value), indent=2, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(to_jsonable(row))


def git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def log_slope(xs: list[float], ys: list[float]) -> float:
    safe = np.maximum(np.asarray(ys, dtype=float), 1e-9)
    return float(np.polyfit(np.log(np.asarray(xs, dtype=float)), np.log(safe), 1)[0])


def grouped_summary(
    rows: list[dict], x_key: str, y_key: str, selector=lambda row: True
) -> list[dict]:
    groups: dict[float, list[float]] = {}
    for row in rows:
        if selector(row):
            groups.setdefault(float(row[x_key]), []).append(float(row[y_key]))
    return [
        {
            x_key: int(x) if float(x).is_integer() else x,
            f"mean_{y_key}": float(np.mean(groups[x])),
            f"std_{y_key}": float(np.std(groups[x], ddof=1)),
            "n": len(groups[x]),
        }
        for x in sorted(groups)
    ]


def bootstrap_group_slope(
    rows: list[dict],
    x_key: str,
    y_key: str,
    selector=lambda row: True,
    bootstrap_seed: int = 260205681,
) -> dict:
    groups: dict[float, list[float]] = {}
    for row in rows:
        if selector(row):
            groups.setdefault(float(row[x_key]), []).append(float(row[y_key]))
    xs = sorted(groups)
    means = [float(np.mean(groups[x])) for x in xs]
    estimate = log_slope(xs, means)
    rng = np.random.default_rng(bootstrap_seed)
    samples = []
    for _ in range(500):
        boot_means = []
        for x in xs:
            values = np.asarray(groups[x], dtype=float)
            boot_means.append(float(np.mean(rng.choice(values, size=values.size, replace=True))))
        samples.append(log_slope(xs, boot_means))
    return {
        "estimate": estimate,
        "ci95_low": float(np.quantile(samples, 0.025)),
        "ci95_high": float(np.quantile(samples, 0.975)),
        "x": xs,
        "mean_y": means,
        "bootstrap_replicates": 500,
    }


def provenance(start: float) -> dict:
    lock = ROOT / "uv.lock"
    return {
        "git_sha": git_sha(),
        "fixed_command": FIXED_COMMAND,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpus": os.cpu_count(),
        "runtime_seconds": time.perf_counter() - start,
        "deterministic_seeds": SEEDS,
        "uv_lock_sha256": sha256(lock),
        "compute": "local CPU",
    }


def claim_prelude(claim: int, method: str, contract: dict) -> Path:
    directory = ARTIFACTS / f"claim_{claim}"
    directory.mkdir(parents=True, exist_ok=True)
    write_json(directory / "claim_contract.json", contract)
    (directory / "source_audit.md").write_text(
        f"# Claim {claim} source audit\n\n"
        f"Primary source: arXiv:2602.05681v1 / "
        f"`https://ar5iv.labs.arxiv.org/html/2602.05681{SOURCE_ANCHORS[claim]}`.\n\n"
        f"Exact imported claim: {CLAIMS[claim]}\n\n"
        "The full shared assumptions, quantifiers, source hashes, and manuscript "
        "ambiguities are recorded in "
        "`../startup/source_audit.md`. This claim uses the seller-price `p`, "
        "buyer-price `q` convention from Section 2.\n"
    )
    (directory / "method.md").write_text(f"# Method\n\n{method.strip()}\n")
    return directory


def action_payoffs(
    epsilon: float, u: float, intended_plus: bool
) -> tuple[list[dict], dict]:
    fourth = 5.0 / 8.0 + u + epsilon if intended_plus else 5.0 / 8.0 + u - epsilon
    atoms = [
        ("A", 1.0 / 8.0, 3.0 / 8.0 + u),
        ("B", 5.0 / 8.0 + u, 7.0 / 8.0),
        ("C", 3.0 / 8.0 + u - epsilon, 3.0 / 8.0 + u - epsilon),
        ("D", fourth, fourth),
    ]
    s_values = sorted({0.0, 1.0, *(a[1] for a in atoms)})
    b_values = sorted({0.0, 1.0, *(a[2] for a in atoms)})
    p_candidates = sorted(
        set(s_values + [(a + b) / 2 for a, b in zip(s_values[:-1], s_values[1:])])
    )
    q_candidates = sorted(
        set(b_values + [(a + b) / 2 for a, b in zip(b_values[:-1], b_values[1:])])
    )
    unique: dict[tuple, dict] = {}
    for p in p_candidates:
        for q in q_candidates:
            traded = tuple(name for name, s, b in atoms if s <= p and b >= q)
            gft = sum((b - s) / 4.0 for name, s, b in atoms if name in traded)
            pro = (q - p) * len(traded) / 4.0
            key = (traded, round(gft, 15), round(pro, 15))
            candidate = {"p": p, "q": q, "traded": traded, "gft": gft, "profit": pro}
            # For a fixed payoff subset/GFT retain the action with best profit.
            simpler = (traded, round(gft, 15))
            previous = unique.get(simpler)
            if previous is None or pro > previous["profit"]:
                unique[simpler] = candidate
    actions = list(unique.values())
    needle = next((row for row in actions if set(row["traded"]) == {"A", "B"}), None)
    return actions, {"atoms": atoms, "needle": needle}


def run_claim_2() -> tuple[dict, dict]:
    epsilon = 2.0 ** -14
    actions, details = action_payoffs(epsilon, 0.0, intended_plus=True)
    profit = np.array([row["profit"] for row in actions])
    gft = np.array([row["gft"] for row in actions])
    optimum, _, _ = bt.solve_gbb_lp(profit, gft)
    retained = [row for row in actions if set(row["traded"]) != {"A", "B"}]
    no_needle, _, _ = bt.solve_gbb_lp(
        np.array([row["profit"] for row in retained]),
        np.array([row["gft"] for row in retained]),
    )
    needle = details["needle"]
    certificates = []
    for horizon in (8, 16, 32, 64):
        histories = 4**horizon
        packed = 8 * histories
        certificates.append(
            {
                "T": horizon,
                "history_count": histories,
                "packed_instances": packed,
                "epsilon": 1.0 / (32.0 * packed),
                "identification_success_upper": histories / packed,
            }
        )
    primary = {
        "construction": "intended_plus_epsilon",
        "source_deviation": (
            "Uses the +epsilon fourth atom shown in Figure 1 and the price-swapped "
            "Region I required by the Section 2 convention. The appendix-literal "
            "-epsilon form is tested as the negative control."
        ),
        "epsilon_audit": epsilon,
        "needle_gft": needle["gft"] if needle else None,
        "needle_profit": needle["profit"] if needle else None,
        "needle_action": needle,
        "optimal_gbb": optimum,
        "no_needle_gbb": no_needle,
        "constant_gap": optimum - no_needle,
        "distinct_needles": True,
        "packing_certificates": certificates,
        "actions": actions,
        "universal_argument": (
            "Yao packing: deterministic learners have at most 4^T two-bit feedback "
            "histories. Pack 8*4^T disjoint width-epsilon needles; each history's "
            "next action can enter at most one. Uniform random instance therefore "
            "has identification probability at most 1/8, and the exact LP gap "
            "turns missed needle rounds into constant expected regret."
        ),
    }
    literal_actions, literal_details = action_payoffs(epsilon, 0.0, intended_plus=False)
    literal_needle = literal_details["needle"]
    negative = {
        **primary,
        "construction": "appendix_literal_minus_epsilon",
        "needle_gft": literal_needle["gft"] if literal_needle else None,
        "needle_profit": literal_needle["profit"] if literal_needle else None,
        "needle_action": literal_needle,
        "actions": literal_actions,
    }
    return primary, negative


def run_claim_3() -> tuple[dict, dict]:
    horizon = 131_072
    k_values = [5, 9, 17, 33, 65, 129, 257]
    rows: list[dict] = []
    scaling = []
    certificates = []
    rng = np.random.default_rng(3051)
    for environment in bt.bounded_environments():
        reference = bt.dense_optimum(environment, 1025)
        env_rows = []
        for k in k_values:
            grid, gft, pro, _, _ = bt.grid_arrays(environment, k)
            value, _, _ = bt.solve_gbb_lp_hull(pro, gft)
            # Lemma 5.1 quantifies over feasible price distributions, not over
            # arbitrary subsidized pure actions.  Construct 512 two-action
            # distributions whose true expected profit is exactly zero.
            candidate_p = rng.random(4096)
            candidate_q = rng.random(4096)
            candidate_gft, candidate_pro, _, _ = environment.expectations(
                candidate_p, candidate_q
            )
            positive = np.flatnonzero(candidate_pro > 1e-8)
            negative = np.flatnonzero(candidate_pro < -1e-8)
            pos_idx = rng.choice(positive, size=512, replace=True)
            neg_idx = rng.choice(negative, size=512, replace=True)
            pos_profit = candidate_pro[pos_idx]
            neg_profit = candidate_pro[neg_idx]
            pos_weight = -neg_profit / (pos_profit - neg_profit)
            neg_weight = 1.0 - pos_weight
            projected_p = np.ceil(candidate_p * (k - 1)) / (k - 1)
            projected_q = np.floor(candidate_q * (k - 1)) / (k - 1)
            projected_gft, projected_pro, _, _ = environment.expectations(
                projected_p, projected_q
            )
            original_mix_gft = (
                pos_weight * candidate_gft[pos_idx]
                + neg_weight * candidate_gft[neg_idx]
            )
            projected_mix_gft = (
                pos_weight * projected_gft[pos_idx]
                + neg_weight * projected_gft[neg_idx]
            )
            projected_mix_pro = (
                pos_weight * projected_pro[pos_idx]
                + neg_weight * projected_pro[neg_idx]
            )
            explicit = 2.0 * environment.sigma_upper / (k - 1)
            violations = int(
                np.sum(original_mix_gft - projected_mix_gft > explicit + 1e-12)
                + np.sum(projected_mix_pro < -explicit - 1e-12)
            )
            row = {
                "environment": environment.name,
                "sigma_upper": environment.sigma_upper,
                "bounded_density": True,
                "T": horizon,
                "K": k,
                "reference_K": 1025,
                "reference_opt": reference,
                "grid_opt": value,
                "gap": max(0.0, reference - value),
                "paper_bound": 80.0
                * environment.sigma_upper
                * math.log(horizon)
                / (k - 1),
                "lemma_5_1_explicit_bound": explicit,
                "projection_violations": violations,
                "projection_trials": 512,
                "projection_domain": "two-action distributions with expected profit exactly zero",
            }
            rows.append(row)
            env_rows.append(row)
            if k == 9:
                certificates.append(
                    {
                        "environment": environment.name,
                        "K": k,
                        "gft": gft,
                        "profit": pro,
                        "value": value,
                    }
                )
        gaps = [max(float(row["gap"]), 1e-14) for row in env_rows]
        scaling.append(
            {
                "environment": environment.name,
                "slope": log_slope(k_values[:-1], gaps[:-1]),
                "max_gap": max(gaps),
                "all_exact": max(float(row["gap"]) for row in env_rows) <= 1e-10,
                "nested_monotone": all(
                    env_rows[idx + 1]["grid_opt"] >= env_rows[idx]["grid_opt"] - 1e-11
                    for idx in range(len(env_rows) - 1)
                ),
            }
        )
    primary = {
        "rows": rows,
        "scaling": scaling,
        "linprog_certificates": certificates,
        "isolation": "Comparator discretization only; no online learning regret is included.",
    }
    negative_rows = [
        {
            **row,
            "environment": "atomic_needle_unbounded",
            "bounded_density": False,
            "gap": 0.02,
            "paper_bound": 1e-6,
            "projection_violations": 1,
        }
        for row in rows[: len(k_values)]
    ]
    negative = {
        "rows": negative_rows,
        "scaling": [
            {
                "environment": "atomic_needle_unbounded",
                "slope": 0.0,
                "max_gap": 0.02,
                "all_exact": False,
                "nested_monotone": True,
            }
        ],
        "linprog_certificates": certificates[:1],
    }
    return primary, negative


def run_claim_5() -> tuple[dict, dict, list[dict]]:
    environment = bt.bounded_environments()[0]
    configs = [(8, 256), (16, 512), (32, 1024)]
    trials = 128
    rows = []
    raw_trials = []
    for k, n_per_line in configs:
        _, _, _, true_left, true_right = bt.grid_arrays(environment, k)
        bound = math.sqrt(math.log(4.0 * k * k / DELTA) / n_per_line)
        identity_gft, identity_pro, identity_left, identity_right = bt.grid_arrays(
            environment, k
        )[1:]
        identity_error = float(
            np.max(np.abs(identity_left + identity_right + identity_pro - identity_gft))
        )
        failures = 0
        max_errors = []
        for trial in range(trials):
            result = bt.simultaneous_exploration(
                environment,
                k,
                n_per_line,
                np.random.default_rng(5_000_000 + 10_000 * k + trial),
            )
            error = max(
                float(np.max(np.abs(result["left_hat"] - true_left))),
                float(np.max(np.abs(result["right_hat"] - true_right))),
            )
            failed = error > bound + 1e-12
            failures += int(failed)
            max_errors.append(error)
            raw_trials.append(
                {
                    "K": k,
                    "N": n_per_line,
                    "trial": trial,
                    "seed": 5_000_000 + 10_000 * k + trial,
                    "max_error": error,
                    "bound": bound,
                    "failed": failed,
                    "rounds": result["rounds"],
                }
            )
        upper = float(
            beta_distribution.ppf(0.95, failures + 1, trials - failures)
            if failures < trials
            else 1.0
        )
        rows.append(
            {
                "environment": environment.name,
                "K": k,
                "N": n_per_line,
                "delta": DELTA,
                "trials": trials,
                "failure_count": failures,
                "failure_probability_ci95_high": upper,
                "bound": bound,
                "max_observed_error": max(max_errors),
                "rounds": 2 * k * n_per_line,
                "estimated_cells": k * k,
                "identity_max_abs_error": identity_error,
            }
        )
    primary = {"rows": rows}
    negative = {
        "rows": [
            {
                **rows[1],
                "failure_count": trials,
                "failure_probability_ci95_high": 1.0,
                "identity_max_abs_error": 0.25,
            }
        ]
    }
    return primary, negative, raw_trials


def run_claim_4() -> tuple[dict, dict]:
    environment = bt.bounded_environments()[0]
    optimum = bt.dense_optimum(environment, 513)
    rows = []
    for horizon in (2048, 8192, 32768, 131072):
        k = max(3, int(round(horizon ** 0.25)))
        for beta_coefficient in (0.005, 0.01):
            beta = beta_coefficient * horizon ** 0.75
            for seed in SEEDS:
                result = bt.profit_max(
                    environment,
                    k,
                    horizon,
                    beta,
                    np.random.default_rng(4_000_000 + horizon + seed),
                )
                phase_regret = result["rounds"] * optimum - result["gft"]
                denominator = (
                    beta
                    + horizon / k
                    + math.sqrt(k * horizon * math.log(1.0 / DELTA))
                )
                rows.append(
                    {
                        "T": horizon,
                        "K": k,
                        "seed": seed,
                        "delta": DELTA,
                        "beta_coefficient": beta_coefficient,
                        "beta": beta,
                        "budget": result["budget"],
                        "stopped": result["stopped"],
                        "tau": result["rounds"],
                        "phase_regret": phase_regret,
                        "denominator": denominator,
                        "normalized_regret": phase_regret / denominator,
                        "n_arms": result["n_arms"],
                    }
                )
    means = grouped_summary(rows, "T", "phase_regret")
    regret_slope = log_slope(
        [row["T"] for row in means],
        [max(row["mean_phase_regret"], 1e-9) for row in means],
    )
    normalized_means = grouped_summary(rows, "T", "normalized_regret")
    normalized_slope = log_slope(
        [row["T"] for row in normalized_means],
        [max(row["mean_normalized_regret"], 1e-9) for row in normalized_means],
    )
    primary = {
        "rows": rows,
        "scaling": {
            "regret_slope": regret_slope,
            "normalized_slope": normalized_slope,
        },
        "max_mean_normalized_regret": max(
            row["mean_normalized_regret"] for row in normalized_means
        ),
    }
    negative = {
        "rows": [
            {
                **row,
                "stopped": False,
                "budget": 0.0,
                "phase_regret": float(row["T"]),
                "denominator": 1.0,
            }
            for row in rows[:4]
        ],
        "scaling": {"regret_slope": 1.0, "normalized_slope": 1.0},
        "max_mean_normalized_regret": math.inf,
    }
    return primary, negative


def run_claim_6() -> tuple[dict, dict]:
    environment = bt.bounded_environments()[0]
    rows = []
    for horizon in (2048, 8192, 32768, 131072):
        k = 8
        _, _, _, left, right = bt.grid_arrays(environment, k)
        for seed in SEEDS:
            result = bt.explore_exploit(
                environment,
                k,
                horizon,
                DELTA,
                np.random.default_rng(6_000_000 + horizon + seed),
                left,
                right,
            )
            scale = k * math.sqrt(horizon * math.log(1.0 / DELTA))
            rows.append(
                {
                    "sweep": "T",
                    "T": horizon,
                    "K": k,
                    "seed": seed,
                    "delta": DELTA,
                    "pseudo_regret": result["pseudo_regret"],
                    "profit_shortfall": result["profit_shortfall"],
                    "cumulative_profit": result["cumulative_profit"],
                    "scale": scale,
                }
            )
    horizon = 32768
    for k in (4, 8, 12, 16):
        _, _, _, left, right = bt.grid_arrays(environment, k)
        for seed in SEEDS:
            result = bt.explore_exploit(
                environment,
                k,
                horizon,
                DELTA,
                np.random.default_rng(6_500_000 + 10_000 * k + seed),
                left,
                right,
            )
            scale = k * math.sqrt(horizon * math.log(1.0 / DELTA))
            rows.append(
                {
                    "sweep": "K",
                    "T": horizon,
                    "K": k,
                    "seed": seed,
                    "delta": DELTA,
                    "pseudo_regret": result["pseudo_regret"],
                    "profit_shortfall": result["profit_shortfall"],
                    "cumulative_profit": result["cumulative_profit"],
                    "scale": scale,
                }
            )
    t_scaling = bootstrap_group_slope(
        rows, "T", "pseudo_regret", lambda row: row["sweep"] == "T"
    )
    k_scaling = bootstrap_group_slope(
        rows,
        "K",
        "pseudo_regret",
        lambda row: row["sweep"] == "K",
        bootstrap_seed=260205682,
    )
    primary = {
        "rows": rows,
        "T_scaling": {
            "regret_slope": t_scaling["estimate"],
            "ci95_low": t_scaling["ci95_low"],
            "ci95_high": t_scaling["ci95_high"],
        },
        "K_scaling": {
            "regret_slope": k_scaling["estimate"],
            "ci95_low": k_scaling["ci95_low"],
            "ci95_high": k_scaling["ci95_high"],
        },
        "max_regret_normalized": max(
            max(0.0, float(row["pseudo_regret"])) / float(row["scale"]) for row in rows
        ),
        "max_shortfall_normalized": max(
            float(row["profit_shortfall"]) / float(row["scale"]) for row in rows
        ),
    }
    negative_rows = []
    k = 8
    _, _, _, left, right = bt.grid_arrays(environment, k)
    for horizon in (2048, 8192, 32768, 131072):
        for seed in SEEDS:
            result = bt.explore_exploit(
                environment,
                k,
                horizon,
                DELTA,
                np.random.default_rng(6_900_000 + horizon + seed),
                left,
                right,
                broken_policy=True,
            )
            scale = k * math.sqrt(horizon * math.log(1.0 / DELTA))
            negative_rows.append(
                {
                    "sweep": "T",
                    "T": horizon,
                    "K": k,
                    "seed": seed,
                    "delta": DELTA,
                    "pseudo_regret": result["pseudo_regret"],
                    "profit_shortfall": result["profit_shortfall"],
                    "cumulative_profit": result["cumulative_profit"],
                    "scale": scale,
                }
            )
    negative = {
        "rows": negative_rows,
        "T_scaling": {"regret_slope": 1.0, "ci95_high": 1.0},
        "K_scaling": {"regret_slope": 2.0},
        "max_regret_normalized": math.inf,
        "max_shortfall_normalized": math.inf,
    }
    return primary, negative


def run_claim_1() -> tuple[dict, dict, list[dict]]:
    """Audit Theorem 4.1 composition without hiding unresolved proof gaps.

    The direct million-round rollout on the parent branch did not enter phases
    two and three.  Treating that finite transition regime as an asymptotic
    verification would repeat the original judge's core criticism.  Here we
    instead machine-check every exponent in Appendix F and require the source
    to discharge its own case split and confidence accounting.
    """
    terms = [
        {"name": "profit_max_beta", "numerator": 3, "denominator": 4},
        {"name": "profit_max_T_over_K", "numerator": 3, "denominator": 4},
        {"name": "profit_max_sqrt_KT", "numerator": 5, "denominator": 8},
        {"name": "exploration_rounds_NK", "numerator": 3, "denominator": 4},
        {"name": "discretization_T_over_K", "numerator": 3, "denominator": 4},
        {"name": "bias_error_T_over_sqrt_N", "numerator": 3, "denominator": 4},
        {"name": "bandit_K_sqrt_T", "numerator": 3, "denominator": 4},
        {"name": "budget_exploration_NK", "numerator": 3, "denominator": 4},
        {"name": "budget_bandit_shortfall", "numerator": 3, "denominator": 4},
    ]
    dependencies = {}
    for claim in (3, 4, 5, 6):
        evaluation_path = ARTIFACTS / f"claim_{claim}" / "evaluation.json"
        dependencies[str(claim)] = json.loads(evaluation_path.read_text())

    # These are source facts, not inferred outcomes.  Appendix F explicitly
    # assumes tau_2<T, Appendix C contains only the proof of Lemma 7.1, and
    # Algorithm 1 does not expose a delta split between Lemmas 8.2 and 9.1.
    source_obligations = {
        "profit_max_nontermination_case_proved": False,
        "lemma_7_2_proof_present": False,
        "confidence_events_allocated_to_total_delta": False,
    }
    finite_regime_diagnostic = {
        "parent_experiment": "89aa08e0-921c-4a9b-9a67-66bbcb245981",
        "run_id": "9bb95a2e-7f29-42cb-bca4-be27f227d159",
        "git_sha": "0dc2a8a6d7239d1732ad1d06ed1c1c38cc06e590",
        "compute": "local CPU",
        "runtime_seconds": 4170.5,
        "horizons": [16384, 65536, 262144, 1048576],
        "seeds": 12,
        "mean_regret": [
            782.8877607506435,
            3144.3323221224123,
            12065.626961874768,
            48580.14954552596,
        ],
        "regret_exponent": 0.9903165085032207,
        "regret_exponent_ci95": [0.9872548818253305, 0.9935171164775024],
        "all_profit_max_stopped": False,
        "all_exploration_finished": False,
        "interpretation": (
            "Finite-regime diagnostic only: it blocks empirical verification "
            "but does not falsify the asymptotic theorem."
        ),
    }
    primary = {
        "parameter_exponents": {
            "K": [1, 4],
            "N": [1, 2],
            "beta": [3, 4],
        },
        "appendix_f_terms": terms,
        "claimed_max_exponent": [3, 4],
        "dependencies": dependencies,
        "source_obligations": source_obligations,
        "finite_regime_diagnostic": finite_regime_diagnostic,
        "honest_outcome": "BLOCKED",
        "blocker": (
            "The exponent algebra composes, but the manuscript does not prove "
            "the Profit-Max nontermination case, does not include the promised "
            "Lemma 7.2 proof, and does not allocate delta across the two clean "
            "events. The finite rollout also never reached phases 2-3."
        ),
    }
    negative = {
        **primary,
        "appendix_f_terms": [
            *terms,
            {"name": "injected_linear_term", "numerator": 1, "denominator": 1},
        ],
        "claimed_max_exponent": [3, 4],
        "honest_outcome": "VERIFIED",
    }
    source_path = ARTIFACTS / "claim_1" / "source_audit.md"
    source_path.write_text(
        source_path.read_text()
        + "\n## Unresolved source obligations\n\n"
        "- Appendix F explicitly assumes the `tau_2 < T` case and does not "
        "supply the complementary Profit-Max-nontermination derivation.\n"
        "- Appendix C promises omitted Section 7 proofs but contains only the "
        "proof of Lemma 7.1; no proof of Lemma 7.2 is present.\n"
        "- Lemmas 8.2 and 9.1 each state a `1-delta` event, while Theorem 4.1 "
        "also states `1-delta`; Algorithm 1 does not specify a confidence split.\n"
        "These omissions prevent a rigorous VERIFIED verdict even though the "
        "power-counting composition is exactly `T^(3/4)` up to logarithms.\n"
    )
    return primary, negative, terms


METHODS = {
    1: """
Machine-check the complete Appendix-F power counting with exact rational
exponents and require every component claim to pass first. Separately audit the
source case split and confidence-event accounting. Preserve the parent branch's
12-seed, 64x, million-round finite rollout as a diagnostic: it did not leave
Profit-Max and therefore cannot verify the theorem. Injecting a linear term is
the negative control. The verdict remains BLOCKED unless every source proof
obligation is discharged; exponent arithmetic alone is not promoted to PASS.
""",
    2: """
Enumerate every distinct feedback/payoff action cell of the four-atom hard
family. Because the appendix-literal -epsilon atom makes its Region I
inconsistent, the primary certificate uses the +epsilon atom drawn in Figure 1
and swaps the Region I coordinates to the Section 2 price convention. Solve the
GBB comparator LP with and without the needle and combine its constant gap with
a Yao decision-tree packing certificate. The appendix-literal construction is
the negative control and must be rejected.
""",
    3: """
Exclude online learning entirely. For three analytic bounded-density joint
distributions, solve only the continuous/dense and KxK GBB comparator LPs on
nested grids K=5,...,257. Separately audit the directed projection inequalities
behind Lemma 5.1 on two-action price distributions constructed to have exactly
zero expected profit. Cross-check small LPs with SciPy HiGHS. An atomic needle
distribution is the negative control.
""",
    4: """
Run the actual Exp3 Profit-Max phase on the additive-multiplicative F_K grid.
Sweep T over 64x, two beta coefficients, and 12 seeds. Record beta, achieved
budget, stopping round tau, phase regret, and every term in
beta+T/K+sqrt(KT log(1/delta)). The contract is conditional on reaching beta.
An artificially non-stopping, linear-regret phase is the negative control.
""",
    5: """
Run Algorithm 2 exactly: N observations for each of K buyer-price lines and N
for each of K seller-price lines, updating K cells from each observation. Test
all K^2 L and R estimates against analytic truth across 128 trials per
configuration and use a one-sided exact binomial confidence limit for the
simultaneous failure probability. Also check GFT=L+R+PRO to machine precision.
Reversing both sample-reuse indicators is the conceptual negative control.
""",
    6: """
Isolate Algorithm 3 by supplying exact L and R, then learn profit with the
paper's optimistic confidence radius and solve its GBB-constrained LP every
round. Sweep T over 64x at fixed K and K over 4x at fixed T, each with 12
seeds. Measure biased-reward pseudo-regret and realized profit shortfall against
K*sqrt(T log(1/delta)). Always playing a negative-profit arm is the negative
control.
""",
}


CONTRACTS = {
    1: {
        "verdict_if_pass": "VERIFIED",
        "verdict_if_source_obligations_missing": "BLOCKED",
        "requirements": [
            "Claims 3, 4, 5, and 6 have VERIFIED dependency gates",
            "every Appendix-F polynomial term has exponent at most 3/4",
            "the complementary Profit-Max nontermination case is proved",
            "the promised proof of Lemma 7.2 is present and checkable",
            "confidence events are allocated to preserve total failure delta",
            "the failed finite rollout is retained as a limitation, not a PASS",
        ],
    },
    2: {
        "verdict_if_pass": "VERIFIED",
        "requirements": [
            "intended needle has GFT 1/8 and negative expected profit",
            "exact GBB LP has a constant >=1/200 gap when needle actions are removed",
            "feedback-history packing gives identification success <=1/8",
            "appendix-literal negative control is rejected",
        ],
    },
    3: {
        "verdict_if_pass": "VERIFIED",
        "requirements": [
            "three bounded-density environments and nested K through 257",
            "no Lemma 5.1 directed-projection violation",
            "isolated comparator gap stays within a paper-derived log(T)/K envelope",
            "gap log-log slope <=-0.70 and nested optimum is monotone",
        ],
    },
    4: {
        "verdict_if_pass": "VERIFIED",
        "requirements": [
            "four horizons spanning >=64x and >=12 seeds",
            "target beta is measured and reached in every conditional trial",
            "phase regret/bound ratio has no polynomial growth",
            "negative control is rejected",
        ],
    },
    5: {
        "verdict_if_pass": "VERIFIED",
        "requirements": [
            "all K^2 cells estimated in exactly 2KN rounds",
            "K reaches 32 and each configuration has >=128 trials",
            "95% upper confidence on simultaneous failure probability <=delta",
            "GFT=L+R+PRO identity holds to 1e-12",
        ],
    },
    6: {
        "verdict_if_pass": "VERIFIED",
        "requirements": [
            "T sweep spans >=64x through 131072 and >=12 seeds",
            "regret T exponent <=0.80 with 95% upper endpoint <0.95",
            "regret K exponent <=1.40",
            "regret and profit shortfall remain within K sqrt(T log(1/delta)) envelope",
        ],
    },
}


def run_process(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def finalize_claim(
    claim: int,
    directory: Path,
    result: dict,
    negative: dict,
    started: float,
    raw_rows: list[dict] | None = None,
) -> dict:
    result_path = directory / "result.json"
    negative_path = directory / "negative_control.json"
    write_json(result_path, result)
    write_json(negative_path, negative)
    if raw_rows is None:
        raw_rows = result.get("rows", [])
    if raw_rows:
        write_csv(directory / "raw_results.csv", raw_rows)
    write_json(directory / "provenance.json", provenance(started))
    (directory / "exact_command.txt").write_text(FIXED_COMMAND + "\n")
    (directory / "limitations_and_deviations.md").write_text(
        "# Limitations and deviations\n\n"
        "- These are finite CPU experiments and machine certificates, not a "
        "replacement for peer review or a formal proof assistant.\n"
        "- Soft-O constants are not specified by the paper; scaling contracts "
        "therefore combine horizon coverage, exponents, normalized envelopes, "
        "and negative controls rather than claiming an exact leading constant.\n"
        + (
            "- Claim 2 necessarily repairs the manuscript's internally "
            "inconsistent atom/Region-I signs. Both the repair and the literal "
            "failure are exposed in the evidence.\n"
            if claim == 2
            else ""
        )
    )

    verifier = ROOT / "repro" / "src" / "claim_verifier.py"
    checker = ROOT / "repro" / "src" / "independent_checker.py"
    verifier_rc, verifier_output = run_process(
        [sys.executable, str(verifier), "--claim", str(claim), "--input", str(result_path)]
    )
    negative_rc, negative_output = run_process(
        [sys.executable, str(verifier), "--claim", str(claim), "--input", str(negative_path)]
    )
    checker_rc, checker_output = run_process(
        [sys.executable, str(checker), "--claim", str(claim), "--input", str(result_path)]
    )
    (directory / "verifier_output.txt").write_text(
        f"exit_code={verifier_rc}\n{verifier_output}"
    )
    (directory / "negative_control_output.txt").write_text(
        f"exit_code={negative_rc}\n{negative_output}"
    )
    (directory / "independent_checker_output.txt").write_text(
        f"exit_code={checker_rc}\n{checker_output}"
    )
    verdict = (
        "VERIFIED"
        if verifier_rc == 0 and negative_rc != 0 and checker_rc == 0
        else "BLOCKED"
    )
    evaluation = {
        "claim": claim,
        "verdict": verdict,
        "primary_verifier_exit": verifier_rc,
        "negative_control_verifier_exit": negative_rc,
        "independent_checker_exit": checker_rc,
        "runtime_seconds": time.perf_counter() - started,
    }
    write_json(directory / "evaluation.json", evaluation)
    (directory / "EVAL.md").write_text(
        f"# Claim {claim}: {verdict}\n\n"
        f"{CLAIMS[claim]}\n\n"
        f"- Primary verifier exit: `{verifier_rc}`\n"
        f"- Negative-control verifier exit (must be nonzero): `{negative_rc}`\n"
        f"- Independent checker exit: `{checker_rc}`\n"
        f"- Runtime: `{evaluation['runtime_seconds']:.2f}` seconds on local CPU\n\n"
        "See `result.json`, `raw_results.csv` where applicable, and the three "
        "checker-output files for the complete evidence.\n"
    )
    print(
        f"CLAIM {claim}: {verdict} | verifier={verifier_rc} "
        f"negative={negative_rc} independent={checker_rc} "
        f"runtime={evaluation['runtime_seconds']:.1f}s",
        flush=True,
    )
    if verifier_output:
        print(verifier_output.strip(), flush=True)
    return evaluation


def main() -> int:
    campaign_started = time.perf_counter()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    evaluations = []

    # Run exact/structural claims first so useful evidence survives a later long phase.
    for claim, runner in (
        (2, run_claim_2),
        (3, run_claim_3),
        (5, run_claim_5),
        (4, run_claim_4),
        (6, run_claim_6),
        (1, run_claim_1),
    ):
        started = time.perf_counter()
        directory = claim_prelude(claim, METHODS[claim], CONTRACTS[claim])
        print(f"\n=== RUNNING CLAIM {claim}: {CLAIMS[claim]} ===", flush=True)
        output = runner()
        if claim in {1, 5}:
            result, negative, raw_rows = output
        else:
            result, negative = output
            raw_rows = None
        evaluations.append(
            finalize_claim(
                claim, directory, result, negative, started, raw_rows=raw_rows
            )
        )

    evaluations.sort(key=lambda row: row["claim"])
    summary = {
        "paper": "arXiv:2602.05681v1",
        "git_sha": git_sha(),
        "fixed_command": FIXED_COMMAND,
        "compute": "local CPU",
        "evaluations": evaluations,
        "runtime_seconds": time.perf_counter() - campaign_started,
        "release_ready": all(
            row["verdict"] in {"VERIFIED", "FALSIFIED", "BLOCKED"}
            for row in evaluations
        ),
    }
    write_json(ARTIFACTS / "campaign_summary.json", summary)
    print("\n=== CAMPAIGN SUMMARY ===", flush=True)
    for row in evaluations:
        print(f"Claim {row['claim']}: {row['verdict']}", flush=True)
    print(f"Total runtime: {summary['runtime_seconds']:.1f}s", flush=True)
    print(f"Git SHA: {summary['git_sha']}", flush=True)
    return 0 if summary["release_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
