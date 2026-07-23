"""Failure-sensitive verifiers for the six exact claim contracts.

Each invocation verifies one machine-readable result and exits nonzero on any
contract violation.  The campaign also invokes these verifiers on deliberately
broken negative controls and requires those invocations to fail.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def finite(value: object) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def verify_claim_1(data: dict, failures: list[str]) -> None:
    rows = data["rows"]
    summaries = data["summaries"]
    horizons = sorted({int(row["T"]) for row in rows})
    seeds = sorted({int(row["seed"]) for row in rows})
    require(len(horizons) >= 4, "need at least four horizons", failures)
    require(max(horizons) >= 131_072, "maximum horizon below 131072", failures)
    require(max(horizons) / min(horizons) >= 64, "horizon span below 64x", failures)
    require(len(seeds) >= 12, "fewer than 12 deterministic seeds", failures)
    require(all(row["phase1_stopped"] for row in rows), "Profit-Max did not stop", failures)
    require(all(row["phase2_complete"] for row in rows), "exploration did not finish", failures)
    require(all(row["gbb"] for row in rows), "realized GBB violation", failures)
    require(
        all(int(row["phase1_rounds"]) + 2 * int(row["K"]) * int(row["N"]) + int(row["phase3_rounds"]) == int(row["T"]) for row in rows),
        "phase round accounting mismatch",
        failures,
    )
    slope = data["regret_scaling"]
    require(finite(slope["estimate"]), "non-finite regret exponent", failures)
    require(float(slope["estimate"]) <= 0.90, "regret exponent exceeds 0.90", failures)
    require(float(slope["ci95_high"]) <= 1.00, "regret exponent CI includes linear growth", failures)
    require(
        float(summaries[-1]["mean_regret_over_T"])
        < float(summaries[0]["mean_regret_over_T"]),
        "regret/T did not decrease",
        failures,
    )


def verify_claim_2(data: dict, failures: list[str]) -> None:
    require(data["construction"] == "intended_plus_epsilon", "not the intended needle construction", failures)
    require(abs(float(data["needle_gft"]) - 0.125) <= 1e-12, "needle GFT is not 1/8", failures)
    require(float(data["needle_profit"]) < 0, "needle action is not subsidized", failures)
    require(float(data["optimal_gbb"]) > float(data["no_needle_gbb"]), "needle gives no strict GBB gain", failures)
    require(float(data["constant_gap"]) >= 1.0 / 200.0, "gap is not bounded away from zero", failures)
    require(data["distinct_needles"], "packed needle regions overlap", failures)
    require(len(data["packing_certificates"]) >= 4, "insufficient horizon certificates", failures)
    require(
        all(float(row["identification_success_upper"]) <= 0.125 for row in data["packing_certificates"]),
        "decision-tree identification upper bound too weak",
        failures,
    )
    require(
        all(int(row["history_count"]) < int(row["packed_instances"]) for row in data["packing_certificates"]),
        "packing does not dominate feedback histories",
        failures,
    )


def verify_claim_3(data: dict, failures: list[str]) -> None:
    rows = data["rows"]
    envs = sorted({row["environment"] for row in rows})
    require(len(envs) >= 3, "fewer than three bounded-density environments", failures)
    require(max(int(row["K"]) for row in rows) >= 257, "grid sweep stops below K=257", failures)
    require(all(row["bounded_density"] for row in rows), "unbounded instance in primary grid audit", failures)
    require(all(float(row["gap"]) >= -2e-10 for row in rows), "negative comparator gap", failures)
    require(all(float(row["gap"]) <= float(row["paper_bound"]) + 2e-9 for row in rows), "O(log(T)/K) envelope exceeded", failures)
    require(all(int(row["projection_violations"]) == 0 for row in rows), "Lemma 5.1 projection inequality violated", failures)
    for summary in data["scaling"]:
        require(
            bool(summary["all_exact"]) or float(summary["slope"]) <= -0.70,
            f"{summary['environment']} gap is neither exact nor O(1/K)",
            failures,
        )
        require(summary["nested_monotone"], f"{summary['environment']} nested grids not monotone", failures)


def verify_claim_4(data: dict, failures: list[str]) -> None:
    rows = data["rows"]
    horizons = sorted({int(row["T"]) for row in rows})
    seeds = sorted({int(row["seed"]) for row in rows})
    require(len(horizons) >= 4, "need four horizons", failures)
    require(max(horizons) / min(horizons) >= 64, "horizon span below 64x", failures)
    require(len(seeds) >= 12, "fewer than 12 seeds", failures)
    require(all(row["stopped"] for row in rows), "conditional stop event not met", failures)
    require(all(float(row["budget"]) >= float(row["beta"]) for row in rows), "target beta not measured/reached", failures)
    require(all(finite(row["phase_regret"]) for row in rows), "non-finite phase regret", failures)
    require(all(float(row["denominator"]) > 0 for row in rows), "invalid bound denominator", failures)
    scaling = data["scaling"]
    require(float(scaling["regret_slope"]) <= 0.95, "phase regret grows too quickly", failures)
    require(float(scaling["normalized_slope"]) <= 0.20, "regret/bound ratio grows polynomially", failures)
    require(float(data["max_mean_normalized_regret"]) <= 8.0, "empirical constant exceeds audit ceiling", failures)


def verify_claim_5(data: dict, failures: list[str]) -> None:
    rows = data["rows"]
    require(len(rows) >= 3, "insufficient K,N configurations", failures)
    require(max(int(row["K"]) for row in rows) >= 32, "sample-reuse sweep stops below K=32", failures)
    require(min(int(row["trials"]) for row in rows) >= 128, "fewer than 128 trials", failures)
    require(all(int(row["rounds"]) == 2 * int(row["K"]) * int(row["N"]) for row in rows), "not exactly 2KN samples", failures)
    require(all(int(row["estimated_cells"]) == int(row["K"]) ** 2 for row in rows), "not all K^2 cells estimated", failures)
    require(all(float(row["failure_probability_ci95_high"]) <= float(row["delta"]) for row in rows), "simultaneous error guarantee not supported", failures)
    require(all(float(row["identity_max_abs_error"]) <= 1e-12 for row in rows), "GFT=L+R+PRO identity failed", failures)


def verify_claim_6(data: dict, failures: list[str]) -> None:
    rows = data["rows"]
    horizons = sorted({int(row["T"]) for row in rows if row["sweep"] == "T"})
    seeds = sorted({int(row["seed"]) for row in rows})
    require(max(horizons) >= 131_072 and max(horizons) / min(horizons) >= 64, "T sweep is not full scale", failures)
    require(len(seeds) >= 12, "fewer than 12 seeds", failures)
    require(all(finite(row["pseudo_regret"]) and finite(row["profit_shortfall"]) for row in rows), "non-finite phase metric", failures)
    t_scaling = data["T_scaling"]
    k_scaling = data["K_scaling"]
    require(float(t_scaling["regret_slope"]) <= 0.80, "T exponent exceeds finite-sample ceiling", failures)
    require(float(t_scaling["ci95_high"]) <= 0.95, "T exponent CI includes linear growth", failures)
    require(float(k_scaling["regret_slope"]) <= 1.40, "K exponent exceeds finite-sample ceiling", failures)
    require(float(data["max_regret_normalized"]) <= 8.0, "regret exceeds K sqrt(T) envelope", failures)
    require(float(data["max_shortfall_normalized"]) <= 8.0, "profit shortfall exceeds K sqrt(T) envelope", failures)


VERIFIERS = {
    1: verify_claim_1,
    2: verify_claim_2,
    3: verify_claim_3,
    4: verify_claim_4,
    5: verify_claim_5,
    6: verify_claim_6,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", type=int, choices=range(1, 7), required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    failures: list[str] = []
    VERIFIERS[args.claim](data, failures)
    if failures:
        print(f"CLAIM {args.claim} VERIFIER: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"CLAIM {args.claim} VERIFIER: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
