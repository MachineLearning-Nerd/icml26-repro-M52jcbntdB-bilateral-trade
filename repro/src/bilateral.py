"""Faithful CPU primitives for arXiv:2602.05681.

The paper studies a seller price ``p`` and buyer price ``q``.  A trade occurs
iff ``s <= p`` and ``b >= q``.  This module keeps that convention everywhere.
It contains analytic bounded-density environments, the paper's three phases,
and exact one-constraint LP helpers.  No claim verdict is decided here.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class RectangleComponent:
    weight: float
    s_lo: float
    s_hi: float
    b_lo: float
    b_hi: float


class RectangleMixture:
    """Mixture of uniforms on axis-aligned rectangles in valuation space."""

    def __init__(self, name: str, components: Iterable[RectangleComponent]):
        self.name = name
        self.components = tuple(components)
        total = sum(c.weight for c in self.components)
        if not np.isclose(total, 1.0):
            raise ValueError(f"weights sum to {total}, not one")
        if any(
            c.weight <= 0
            or not (0 <= c.s_lo < c.s_hi <= 1)
            or not (0 <= c.b_lo < c.b_hi <= 1)
            for c in self.components
        ):
            raise ValueError("invalid rectangle component")

    @property
    def sigma_upper(self) -> float:
        # A valid upper bound even when rectangles overlap.
        return float(
            sum(
                c.weight / ((c.s_hi - c.s_lo) * (c.b_hi - c.b_lo))
                for c in self.components
            )
        )

    def sample(self, rng: np.random.Generator, n: int = 1) -> tuple[np.ndarray, np.ndarray]:
        weights = np.array([c.weight for c in self.components], dtype=float)
        choice = rng.choice(len(self.components), size=n, p=weights)
        u = rng.random((2, n))
        s = np.empty(n, dtype=float)
        b = np.empty(n, dtype=float)
        for idx, c in enumerate(self.components):
            mask = choice == idx
            s[mask] = c.s_lo + (c.s_hi - c.s_lo) * u[0, mask]
            b[mask] = c.b_lo + (c.b_hi - c.b_lo) * u[1, mask]
        return s, b

    @staticmethod
    def _lower_probability(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
        return np.clip((x - lo) / (hi - lo), 0.0, 1.0)

    @staticmethod
    def _upper_probability(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
        return np.clip((hi - x) / (hi - lo), 0.0, 1.0)

    @staticmethod
    def _lower_first_moment(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
        top = np.clip(x, lo, hi)
        return (top * top - lo * lo) / (2.0 * (hi - lo))

    @staticmethod
    def _upper_first_moment(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
        bottom = np.clip(x, lo, hi)
        return (hi * hi - bottom * bottom) / (2.0 * (hi - lo))

    def expectations(
        self, p: np.ndarray | float, q: np.ndarray | float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return analytic ``(GFT, PRO, L, R)`` at broadcastable prices."""
        p_arr, q_arr = np.broadcast_arrays(
            np.asarray(p, dtype=float), np.asarray(q, dtype=float)
        )
        gft = np.zeros_like(p_arr)
        pro = np.zeros_like(p_arr)
        left = np.zeros_like(p_arr)
        right = np.zeros_like(p_arr)
        for c in self.components:
            ps = self._lower_probability(p_arr, c.s_lo, c.s_hi)
            pb = self._upper_probability(q_arr, c.b_lo, c.b_hi)
            es = self._lower_first_moment(p_arr, c.s_lo, c.s_hi)
            eb = self._upper_first_moment(q_arr, c.b_lo, c.b_hi)
            comp_gft = eb * ps - es * pb
            comp_pro = (q_arr - p_arr) * ps * pb
            comp_left = p_arr * ps * pb - es * pb
            comp_right = eb * ps - q_arr * ps * pb
            gft += c.weight * comp_gft
            pro += c.weight * comp_pro
            left += c.weight * comp_left
            right += c.weight * comp_right
        return gft, pro, left, right


def bounded_environments() -> tuple[RectangleMixture, ...]:
    return (
        RectangleMixture(
            "uniform",
            [RectangleComponent(1.0, 0.0, 1.0, 0.0, 1.0)],
        ),
        RectangleMixture(
            "separated_markets",
            [
                RectangleComponent(0.55, 0.00, 0.55, 0.35, 1.00),
                RectangleComponent(0.45, 0.35, 1.00, 0.00, 0.65),
            ],
        ),
        RectangleMixture(
            "correlated_four_rectangles",
            [
                RectangleComponent(0.30, 0.00, 0.35, 0.55, 1.00),
                RectangleComponent(0.25, 0.20, 0.65, 0.35, 0.85),
                RectangleComponent(0.25, 0.45, 0.90, 0.15, 0.65),
                RectangleComponent(0.20, 0.65, 1.00, 0.00, 0.45),
            ],
        ),
    )


def trade_feedback(
    p: float, q: float, s: float, b: float
) -> tuple[int, float, float]:
    trade = int(s <= p and b >= q)
    return trade, (b - s) * trade, (q - p) * trade


def solve_gbb_lp(
    profit: np.ndarray, reward: np.ndarray, tolerance: float = 1e-12
) -> tuple[float, np.ndarray, np.ndarray]:
    """Solve a simplex LP with one expected-profit constraint.

    The optimum has support on at most two actions.  This implementation first
    checks feasible pure actions, then evaluates every positive/negative pair.
    The latter is vectorized and is fast for the paper-scale K^2 grids used here.
    """
    x = np.asarray(profit, dtype=float).ravel()
    y = np.asarray(reward, dtype=float).ravel()
    if x.shape != y.shape or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("invalid LP arrays")

    feasible = np.flatnonzero(x >= -tolerance)
    if feasible.size == 0:
        raise ValueError("no feasible action; diagonal grid actions should prevent this")
    pure_idx = int(feasible[np.argmax(y[feasible])])
    best_value = float(y[pure_idx])
    best_indices = np.array([pure_idx], dtype=int)
    best_weights = np.array([1.0], dtype=float)

    pos = np.flatnonzero(x > tolerance)
    neg = np.flatnonzero(x < -tolerance)
    if pos.size and neg.size:
        xp = x[pos][:, None]
        xn = x[neg][None, :]
        yp = y[pos][:, None]
        yn = y[neg][None, :]
        values = (xp * yn - xn * yp) / (xp - xn)
        flat = int(np.argmax(values))
        i, j = np.unravel_index(flat, values.shape)
        candidate = float(values[i, j])
        if candidate > best_value + tolerance:
            pi, ni = int(pos[i]), int(neg[j])
            w_pos = float(-x[ni] / (x[pi] - x[ni]))
            best_value = candidate
            best_indices = np.array([pi, ni], dtype=int)
            best_weights = np.array([w_pos, 1.0 - w_pos], dtype=float)
    return best_value, best_indices, best_weights


def solve_gbb_lp_hull(
    profit: np.ndarray, reward: np.ndarray
) -> tuple[float, np.ndarray, np.ndarray]:
    """Independent-scale LP solver using dominance pruning and an upper hull."""
    x = np.asarray(profit, dtype=float).ravel()
    y = np.asarray(reward, dtype=float).ravel()
    original = np.arange(x.size)
    order = np.lexsort((-y, x))
    x, y, original = x[order], y[order], original[order]

    # Keep only points not dominated by a point with at least as much profit.
    right_best = np.maximum.accumulate(y[::-1])[::-1]
    keep = y >= right_best - 1e-14
    x, y, original = x[keep], y[keep], original[keep]

    # Remove duplicate x values after retaining their best y.
    if x.size > 1:
        same_as_previous = np.r_[False, np.isclose(np.diff(x), 0.0, atol=1e-14)]
        x, y, original = x[~same_as_previous], y[~same_as_previous], original[~same_as_previous]

    hull: list[int] = []
    for idx in range(x.size):
        while len(hull) >= 2:
            a, b = hull[-2], hull[-1]
            cross = (x[b] - x[a]) * (y[idx] - y[b]) - (y[b] - y[a]) * (
                x[idx] - x[b]
            )
            if cross >= -1e-14:
                hull.pop()
            else:
                break
        hull.append(idx)

    best_value = -math.inf
    best_indices = np.array([], dtype=int)
    best_weights = np.array([], dtype=float)
    for h in hull:
        if x[h] >= -1e-12 and y[h] > best_value:
            best_value = float(y[h])
            best_indices = np.array([int(original[h])])
            best_weights = np.array([1.0])
    for left_idx, right_idx in zip(hull[:-1], hull[1:]):
        if x[left_idx] < 0 < x[right_idx]:
            w_right = float(-x[left_idx] / (x[right_idx] - x[left_idx]))
            value = (1.0 - w_right) * y[left_idx] + w_right * y[right_idx]
            if value > best_value:
                best_value = float(value)
                best_indices = np.array(
                    [int(original[left_idx]), int(original[right_idx])]
                )
                best_weights = np.array([1.0 - w_right, w_right])
    if not np.isfinite(best_value):
        raise ValueError("hull solver found no feasible point")
    return best_value, best_indices, best_weights


def grid_arrays(
    environment: RectangleMixture, k: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    grid = np.linspace(0.0, 1.0, k)
    p, q = np.meshgrid(grid, grid, indexing="ij")
    gft, pro, left, right = environment.expectations(p, q)
    return grid, gft.ravel(), pro.ravel(), left.ravel(), right.ravel()


@lru_cache(maxsize=None)
def dense_optimum(environment: RectangleMixture, k_ref: int = 1025) -> float:
    _, gft, pro, _, _ = grid_arrays(environment, k_ref)
    value, _, _ = solve_gbb_lp_hull(pro, gft)
    return value


def additive_multiplicative_grid(k: int, horizon: int) -> np.ndarray:
    base = np.linspace(0.0, 1.0, k)
    pairs: set[tuple[float, float]] = set()
    for level in range(math.ceil(math.log2(max(horizon, 2))) + 1):
        gap = 2.0 ** (-level)
        for q in base:
            p = q - gap
            if p >= 0:
                pairs.add((round(float(p), 15), round(float(q), 15)))
        for p in base:
            q = p + gap
            if q <= 1:
                pairs.add((round(float(p), 15), round(float(q), 15)))
    if not pairs:
        raise ValueError("empty F_K")
    return np.array(sorted(pairs), dtype=float)


def profit_max(
    environment: RectangleMixture,
    k: int,
    horizon: int,
    beta: float,
    rng: np.random.Generator,
) -> dict:
    actions = additive_multiplicative_grid(k, horizon)
    n_arms = actions.shape[0]
    weights = np.ones(n_arms, dtype=float)
    gamma = min(
        1.0,
        math.sqrt(n_arms * math.log(max(n_arms, 2)) / ((math.e - 1.0) * horizon)),
    )
    budget = 0.0
    gft_total = 0.0
    actions_taken = 0
    while actions_taken < horizon and budget < beta:
        probs = (1.0 - gamma) * weights / weights.sum() + gamma / n_arms
        arm = int(rng.choice(n_arms, p=probs))
        p, q = actions[arm]
        s, b = environment.sample(rng, 1)
        trade, gft, profit = trade_feedback(float(p), float(q), float(s[0]), float(b[0]))
        estimate = profit / max(probs[arm], 1e-15)
        weights[arm] *= math.exp(gamma * estimate / n_arms)
        # Avoid numerical overflow without changing probabilities.
        if weights.max() > 1e100:
            weights /= weights.max()
        budget += profit
        gft_total += gft
        actions_taken += 1
    return {
        "rounds": actions_taken,
        "budget": budget,
        "gft": gft_total,
        "stopped": bool(budget >= beta),
        "n_arms": n_arms,
        "target_beta": beta,
    }


def simultaneous_exploration(
    environment: RectangleMixture,
    k: int,
    n_per_line: int,
    rng: np.random.Generator,
    broken_indicator: bool = False,
) -> dict:
    """Algorithm 2 with exactly N samples for each of 2K lines."""
    grid = np.linspace(0.0, 1.0, k)
    left_hat = np.zeros((k, k), dtype=float)
    right_hat = np.zeros((k, k), dtype=float)
    budget = 0.0
    gft_total = 0.0

    for q_idx, q in enumerate(grid):
        s, b = environment.sample(rng, n_per_line)
        u = rng.random(n_per_line)
        feedback = (s <= u) & (b >= q)
        indicator = u[:, None] >= grid[None, :] if broken_indicator else u[:, None] <= grid[None, :]
        left_hat[:, q_idx] = (feedback[:, None] & indicator).mean(axis=0)
        trades = feedback
        budget += float(np.sum((q - u) * trades))
        gft_total += float(np.sum((b - s) * trades))

    for p_idx, p in enumerate(grid):
        s, b = environment.sample(rng, n_per_line)
        v = rng.random(n_per_line)
        feedback = (s <= p) & (b >= v)
        indicator = v[:, None] <= grid[None, :] if broken_indicator else v[:, None] >= grid[None, :]
        right_hat[p_idx, :] = (feedback[:, None] & indicator).mean(axis=0)
        trades = feedback
        budget += float(np.sum((v - p) * trades))
        gft_total += float(np.sum((b - s) * trades))

    return {
        "left_hat": left_hat.ravel(),
        "right_hat": right_hat.ravel(),
        "rounds": 2 * k * n_per_line,
        "budget": budget,
        "gft": gft_total,
    }


def explore_exploit(
    environment: RectangleMixture,
    k: int,
    horizon: int,
    delta: float,
    rng: np.random.Generator,
    left_bias: np.ndarray,
    right_bias: np.ndarray,
    broken_policy: bool = False,
) -> dict:
    """Algorithm 3 over ``horizon`` phase rounds."""
    grid, true_gft, true_pro, true_left, true_right = grid_arrays(environment, k)
    n_arms = k * k
    counts = np.zeros(n_arms, dtype=np.int64)
    profit_sums = np.zeros(n_arms, dtype=float)
    pro_ucb = np.ones(n_arms, dtype=float)
    gamma_indices = np.arange(n_arms)
    gamma_weights = np.full(n_arms, 1.0 / n_arms)
    cumulative_reward = 0.0
    cumulative_profit = 0.0

    comparator, _, _ = solve_gbb_lp(true_pro, true_gft)
    for _ in range(horizon):
        if broken_policy:
            negative = np.flatnonzero(true_pro < 0)
            arm = int(negative[np.argmax(true_gft[negative])])
        else:
            arm = int(rng.choice(gamma_indices, p=gamma_weights))
        p_idx, q_idx = divmod(arm, k)
        p, q = float(grid[p_idx]), float(grid[q_idx])
        s, b = environment.sample(rng, 1)
        _, gft, profit = trade_feedback(p, q, float(s[0]), float(b[0]))
        cumulative_reward += gft
        cumulative_profit += profit
        counts[arm] += 1
        profit_sums[arm] += profit
        mean = profit_sums[arm] / counts[arm]
        radius = min(
            1.0,
            math.sqrt(
                2.0
                * math.log(max(8.0 * horizon * n_arms / delta, math.e))
                / counts[arm]
            ),
        )
        pro_ucb[arm] = mean + radius

        if not broken_policy:
            optimistic_reward = left_bias + right_bias + pro_ucb
            _, gamma_indices, gamma_weights = solve_gbb_lp(
                pro_ucb, optimistic_reward
            )

    return {
        "rounds": horizon,
        "cumulative_gft": cumulative_reward,
        "cumulative_profit": cumulative_profit,
        "pseudo_regret": horizon * comparator - cumulative_reward,
        "profit_shortfall": max(0.0, -cumulative_profit),
        "comparator": comparator,
        "min_count": int(counts.min()),
        "max_count": int(counts.max()),
    }


def full_algorithm(
    environment: RectangleMixture,
    horizon: int,
    delta: float,
    seed: int,
    beta_coefficient: float,
) -> dict:
    """Algorithm 1 with the paper's K and N exponents and explicit constants."""
    rng = np.random.default_rng(seed)
    k = max(3, int(round(horizon ** 0.25)))
    n_per_line = max(2, int(round(horizon ** 0.5)))
    beta = beta_coefficient * horizon ** 0.75
    optimum = dense_optimum(environment, 513)

    phase1 = profit_max(environment, k, horizon, beta, rng)
    elapsed = int(phase1["rounds"])
    total_gft = float(phase1["gft"])
    budget = float(phase1["budget"])
    phase2_complete = False
    phase3_rounds = 0

    required_exploration = 2 * k * n_per_line
    if phase1["stopped"] and elapsed + required_exploration <= horizon:
        phase2 = simultaneous_exploration(environment, k, n_per_line, rng)
        elapsed += int(phase2["rounds"])
        total_gft += float(phase2["gft"])
        budget += float(phase2["budget"])
        phase2_complete = True
        radius = math.sqrt(math.log(4.0 * k * k / delta) / n_per_line)
        left_bias = np.asarray(phase2["left_hat"]) + radius
        right_bias = np.asarray(phase2["right_hat"]) + radius
        phase3_rounds = horizon - elapsed
        phase3 = explore_exploit(
            environment,
            k,
            phase3_rounds,
            delta,
            rng,
            left_bias,
            right_bias,
        )
        total_gft += float(phase3["cumulative_gft"])
        budget += float(phase3["cumulative_profit"])
        elapsed += phase3_rounds
    else:
        # Profit-Max occupies all remaining rounds if the target is not reached.
        if elapsed < horizon:
            continuation = profit_max(
                environment, k, horizon - elapsed, math.inf, rng
            )
            total_gft += float(continuation["gft"])
            budget += float(continuation["budget"])
            elapsed = horizon

    return {
        "seed": seed,
        "T": horizon,
        "K": k,
        "N": n_per_line,
        "beta": beta,
        "phase1_rounds": int(phase1["rounds"]),
        "phase1_stopped": bool(phase1["stopped"]),
        "phase2_complete": phase2_complete,
        "phase3_rounds": phase3_rounds,
        "cumulative_gft": total_gft,
        "cumulative_profit": budget,
        "gbb": bool(budget >= -1e-9),
        "regret": horizon * optimum - total_gft,
        "optimum": optimum,
        "beta_coefficient": beta_coefficient,
    }
