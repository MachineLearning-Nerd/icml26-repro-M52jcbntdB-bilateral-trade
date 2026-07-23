"""Independent post-hoc checks using only serialized claim evidence."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import linprog


def fail(message: str) -> None:
    raise AssertionError(message)


def slope(xs: list[float], ys: list[float]) -> float:
    if any(y <= 0 for y in ys):
        fail("non-positive value in log slope")
    return float(np.polyfit(np.log(xs), np.log(ys), 1)[0])


def check_1(data: dict) -> None:
    grouped: dict[int, list[float]] = {}
    for row in data["rows"]:
        grouped.setdefault(int(row["T"]), []).append(float(row["regret"]))
        if float(row["cumulative_profit"]) < -1e-9:
            fail("independent GBB check failed")
    xs = sorted(grouped)
    ys = [float(np.mean(grouped[x])) for x in xs]
    observed = slope(xs, ys)
    if abs(observed - float(data["regret_scaling"]["estimate"])) > 1e-9:
        fail("serialized slope does not recompute")


def check_2(data: dict) -> None:
    if not math.isclose(
        float(data["constant_gap"]),
        float(data["optimal_gbb"]) - float(data["no_needle_gbb"]),
        abs_tol=1e-12,
    ):
        fail("gap arithmetic mismatch")
    for row in data["packing_certificates"]:
        expected = int(row["history_count"]) / int(row["packed_instances"])
        if not math.isclose(expected, float(row["identification_success_upper"]), rel_tol=1e-15):
            fail("packing ratio mismatch")


def check_3(data: dict) -> None:
    # Small-grid SciPy LP certificates are produced separately from the hull solver.
    for certificate in data["linprog_certificates"]:
        c = -np.asarray(certificate["gft"], dtype=float)
        profit = np.asarray(certificate["profit"], dtype=float)
        result = linprog(
            c,
            A_ub=-profit[None, :],
            b_ub=np.array([0.0]),
            A_eq=np.ones((1, profit.size)),
            b_eq=np.array([1.0]),
            bounds=(0.0, 1.0),
            method="highs",
        )
        if not result.success:
            fail("independent scipy LP failed")
        if abs(-float(result.fun) - float(certificate["value"])) > 1e-9:
            fail("hull and scipy LP values disagree")


def check_4(data: dict) -> None:
    for row in data["rows"]:
        expected = (
            float(row["beta"])
            + float(row["T"]) / float(row["K"])
            + math.sqrt(
                float(row["K"])
                * float(row["T"])
                * math.log(1.0 / float(row["delta"]))
            )
        )
        if not math.isclose(expected, float(row["denominator"]), rel_tol=1e-12):
            fail("bound denominator mismatch")


def check_5(data: dict) -> None:
    for row in data["rows"]:
        expected = math.sqrt(
            math.log(4.0 * int(row["K"]) ** 2 / float(row["delta"]))
            / int(row["N"])
        )
        if not math.isclose(expected, float(row["bound"]), rel_tol=1e-12):
            fail("Hoeffding/union bound mismatch")
        if int(row["rounds"]) != 2 * int(row["K"]) * int(row["N"]):
            fail("round count mismatch")


def check_6(data: dict) -> None:
    for row in data["rows"]:
        scale = float(row["K"]) * math.sqrt(
            float(row["T"]) * math.log(1.0 / float(row["delta"]))
        )
        if not math.isclose(scale, float(row["scale"]), rel_tol=1e-12):
            fail("K sqrt(T log(1/delta)) scale mismatch")


CHECKERS = {1: check_1, 2: check_2, 3: check_3, 4: check_4, 5: check_5, 6: check_6}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", type=int, choices=range(1, 7), required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    try:
        CHECKERS[args.claim](data)
    except Exception as exc:
        print(f"CLAIM {args.claim} INDEPENDENT CHECK: FAIL")
        print(f"{type(exc).__name__}: {exc}")
        return 1
    print(f"CLAIM {args.claim} INDEPENDENT CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
