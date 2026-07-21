"""Clean-room online bilateral trade from "A Stronger Benchmark for Online Bilateral Trade"
(arXiv 2602.05681). numpy, CPU. Bilateral trade: each round a buyer (val b_t) and seller (val s_t)
arrive; the learner posts prices (p_b, p_s); trade iff s_t <= p_s and b_t >= p_b; GFT = b_t - s_t.
Benchmark: best fixed (p_b*, p_s*). Algorithm: explore K*K grid + UCB optimize.
c1: O~(T^{3/4}) regret with bounded density; c3: discretization O(log T/K); c6: UCB O~(K sqrt T).
"""
from __future__ import annotations
import numpy as np


def bilateral_trade_round(p_b, p_s, b_val, s_val):
    """One trade round: return (trade_happened, gft)."""
    if s_val <= p_s and b_val >= p_b:
        return True, b_val - s_val
    return False, 0.0


def best_fixed_prices(grid_pts, b_dists, s_dists, n_samples=2000):
    """Find the best fixed (p_b, p_s) on the grid maximizing expected GFT."""
    rng = np.random.default_rng(42)
    best_gft, best_pair = -1, (0.5, 0.5)
    for p_b in grid_pts:
        for p_s in grid_pts:
            if p_b <= p_s: continue  # no profit
            gft = 0.0
            for _ in range(n_samples):
                b = rng.uniform(0, 1); s = rng.uniform(0, 1)
                _, g = bilateral_trade_round(p_b, p_s, b, s)
                gft += g
            if gft > best_gft:
                best_gft, best_pair = gft, (p_b, p_s)
    return best_pair, best_gft / n_samples


def bilateral_ucb(K, T, seed=0):
    """Multi-phase: explore K*K grid + UCB optimize. Returns cumulative regret."""
    rng = np.random.default_rng(seed)
    grid = np.linspace(0.01, 0.99, K)
    # Phase 1: exploration (2K rounds — sample reuse)
    n_explore = 2 * K
    estimates = np.zeros((K, K))  # estimated GFT per grid point
    counts = np.zeros((K, K))
    for i in range(K):
        p_b = grid[i]
        for j in range(K):
            p_s = grid[j]
            if p_b <= p_s: continue
            b = rng.uniform(0, 1); s = rng.uniform(0, 1)
            _, g = bilateral_trade_round(p_b, p_s, b, s)
            estimates[i, j] += g; counts[i, j] += 1
    # Phase 2: UCB on the grid
    remaining = T - n_explore
    total_gft = float(estimates.sum())
    best_pair, best_gft_per_round = best_fixed_prices(grid, None, None)
    regret = 0.0; regrets = []
    for t in range(remaining):
        # UCB: pick grid point with highest upper confidence bound
        ucb = estimates / np.maximum(counts, 1) + np.sqrt(2 * np.log(max(t + 2, 2)) / np.maximum(counts, 1))
        i_star, j_star = np.unravel_index(np.argmax(ucb), (K, K))
        p_b, p_s = grid[i_star], grid[j_star]
        b = rng.uniform(0, 1); s = rng.uniform(0, 1)
        _, g = bilateral_trade_round(p_b, p_s, b, s)
        estimates[i_star, j_star] += g; counts[i_star, j_star] += 1
        regret += best_gft_per_round - g
        regrets.append(regret)
    return regrets, best_gft_per_round
