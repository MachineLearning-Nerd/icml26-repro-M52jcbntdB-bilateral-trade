"""Regenerate the report figures from the committed winning-run evidence."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / ".openresearch" / "artifacts"
OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(parents=True, exist_ok=True)

GREEN = "#087E5B"
ORANGE = "#D97706"
BLUE = "#2563EB"
PURPLE = "#7C3AED"
RED = "#B42318"
INK = "#17212B"
GRID = "#D8DEE7"


def load(claim: int) -> dict:
    return json.loads((EVIDENCE / f"claim_{claim}" / "result.json").read_text())


def finish(fig: plt.Figure, name: str) -> None:
    fig.patch.set_facecolor("white")
    fig.savefig(OUT / name, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def style_axis(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, color=GRID, linewidth=0.8, alpha=0.7)
    ax.tick_params(colors=INK)


def headline() -> None:
    diagnostic = load(1)["finite_regime_diagnostic"]
    x = np.asarray(diagnostic["horizons"], dtype=float)
    y = np.asarray(diagnostic["mean_regret"], dtype=float)
    ref_075 = y[0] * (x / x[0]) ** 0.75
    ref_1 = y[0] * (x / x[0])

    fig, (ax, status_ax) = plt.subplots(
        1, 2, figsize=(12.4, 4.5), gridspec_kw={"width_ratios": [1.45, 1]}
    )
    ax.loglog(x, y, "o-", color=ORANGE, linewidth=2.5, label="Observed mean regret")
    ax.loglog(x, ref_075, "--", color=GREEN, linewidth=2, label=r"$T^{3/4}$ reference")
    ax.loglog(x, ref_1, ":", color=RED, linewidth=2, label=r"$T$ reference")
    ax.set_title("The end-to-end finite run stayed near-linear", loc="left", weight="bold")
    ax.set_xlabel("Horizon T (12 seeds)")
    ax.set_ylabel("Mean regret")
    ax.legend(frameon=False, loc="upper left")
    ax.text(
        0.98,
        0.05,
        "slope 0.9903\n95% CI [0.9873, 0.9935]",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color=ORANGE,
        weight="bold",
    )
    style_axis(ax)

    claims = np.arange(1, 7)
    values = [0.35, 1, 1, 1, 1, 1]
    colors = [ORANGE] + [GREEN] * 5
    status_ax.barh(claims, values, color=colors, height=0.62)
    status_ax.set_xlim(0, 1.05)
    status_ax.set_yticks(claims, [f"Claim {c}" for c in claims])
    status_ax.invert_yaxis()
    status_ax.set_xticks([])
    status_ax.set_title("Cumulative evidence verdicts", loc="left", weight="bold")
    for claim, verdict in zip(claims, ["BLOCKED"] + ["VERIFIED"] * 5):
        status_ax.text(
            0.31 if claim == 1 else 0.96,
            claim,
            verdict,
            va="center",
            ha="right",
            color="white",
            weight="bold",
        )
    status_ax.spines[:].set_visible(False)
    status_ax.grid(False)
    fig.suptitle(
        "Five component claims verify; the headline theorem remains blocked",
        x=0.06,
        ha="left",
        fontsize=15,
        weight="bold",
        color=INK,
    )
    finish(fig, "headline_evidence.png")


def needle() -> None:
    data = load(2)
    fig, (ax, pack_ax) = plt.subplots(1, 2, figsize=(11.8, 4.2))
    labels = ["Full hard instance", "Needle removed"]
    vals = [data["optimal_gbb"], data["no_needle_gbb"]]
    ax.bar(labels, vals, color=[PURPLE, "#AAB3C2"], width=0.62)
    ax.set_ylabel("Optimal feasible expected GFT")
    ax.set_ylim(0, max(vals) * 1.24)
    ax.set_title("Exact GBB LP certificate", loc="left", weight="bold")
    ax.text(
        0.5,
        max(vals) * 1.08,
        f"constant gap = {data['constant_gap']:.6f} > 1/200",
        ha="center",
        color=PURPLE,
        weight="bold",
    )
    for idx, val in enumerate(vals):
        ax.text(idx, val + 0.001, f"{val:.6f}", ha="center")
    style_axis(ax)

    certs = data["packing_certificates"]
    horizons = [row["T"] for row in certs]
    success = [row["identification_success_upper"] for row in certs]
    pack_ax.plot(horizons, success, "o-", color=PURPLE, linewidth=2.5)
    pack_ax.axhline(0.125, color=ORANGE, linestyle="--", label="1/8 certificate")
    pack_ax.set_xlabel("Horizon T")
    pack_ax.set_ylabel("Identification success upper bound")
    pack_ax.set_ylim(0, 0.16)
    pack_ax.set_title("Feedback-history packing", loc="left", weight="bold")
    pack_ax.legend(frameon=False)
    style_axis(pack_ax)
    fig.suptitle(
        "Claim 2: the actual needle changes the feasible optimum",
        x=0.07,
        ha="left",
        fontsize=14,
        weight="bold",
        color=INK,
    )
    finish(fig, "claim2_needle_certificate.png")


def discretization() -> None:
    data = load(3)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in data["rows"]:
        grouped[row["environment"]].append(row)
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    palette = [BLUE, GREEN, PURPLE]
    for color, (name, rows) in zip(palette, grouped.items()):
        rows = sorted(rows, key=lambda row: row["K"])
        k = np.asarray([row["K"] for row in rows])
        gap = np.asarray([row["gap"] for row in rows])
        plotted = np.maximum(gap, 1e-8)
        ax.loglog(k, plotted, "o-", color=color, linewidth=2, label=name.replace("_", " "))
        exact = gap <= 1e-12
        if exact.any():
            ax.scatter(k[exact], plotted[exact], facecolors="white", edgecolors=color, s=55, zorder=3)
    ax.axhline(1e-8, color="#9AA4B2", linestyle=":", linewidth=1)
    ax.text(260, 1.25e-8, "plot floor = exact zero", ha="right", color="#667085")
    ax.set_xlabel("Grid size K")
    ax.set_ylabel("Dense optimum − grid optimum")
    ax.set_title("Claim 3: isolated comparator discretization error", loc="left", weight="bold")
    ax.legend(frameon=False)
    style_axis(ax)
    finish(fig, "claim3_discretization.png")


def phase_bounds() -> None:
    c4 = load(4)
    c6 = load(6)
    fig, (ax4, ax6) = plt.subplots(1, 2, figsize=(12.2, 4.4))

    grouped4: dict[tuple[float, int], list[float]] = defaultdict(list)
    for row in c4["rows"]:
        grouped4[(float(row["beta_coefficient"]), int(row["T"]))].append(
            float(row["normalized_regret"])
        )
    for coefficient, color in [(0.005, BLUE), (0.01, PURPLE)]:
        horizons = sorted(t for c, t in grouped4 if c == coefficient)
        means = [np.mean(grouped4[(coefficient, t)]) for t in horizons]
        ax4.semilogx(
            horizons,
            means,
            "o-",
            color=color,
            linewidth=2,
            label=fr"$\beta={coefficient}T^{{3/4}}$",
        )
    ax4.set_xlabel("Horizon T")
    ax4.set_ylabel("Mean regret / stated scale")
    ax4.set_title("Claim 4: Profit-Max bound", loc="left", weight="bold")
    ax4.legend(frameon=False)
    style_axis(ax4)

    grouped6: dict[int, dict[str, list[float]]] = defaultdict(
        lambda: {"regret": [], "shortfall": []}
    )
    for row in c6["rows"]:
        if row["sweep"] == "T":
            scale = float(row["scale"])
            grouped6[int(row["T"])]["regret"].append(float(row["pseudo_regret"]) / scale)
            grouped6[int(row["T"])]["shortfall"].append(
                float(row["profit_shortfall"]) / scale
            )
    horizons = sorted(grouped6)
    ax6.semilogx(
        horizons,
        [np.mean(grouped6[t]["regret"]) for t in horizons],
        "o-",
        color=GREEN,
        linewidth=2,
        label="biased-reward regret",
    )
    ax6.semilogx(
        horizons,
        [np.mean(grouped6[t]["shortfall"]) for t in horizons],
        "s-",
        color=ORANGE,
        linewidth=2,
        label="profit shortfall",
    )
    ax6.set_xlabel("Horizon T (K=8)")
    ax6.set_ylabel(r"Mean / $K\sqrt{T\log(1/\delta)}$")
    ax6.set_title("Claim 6: constrained UCB scale", loc="left", weight="bold")
    ax6.legend(frameon=False)
    style_axis(ax6)
    fig.suptitle(
        "The two online phases were tested against their stated scales",
        x=0.06,
        ha="left",
        fontsize=14,
        weight="bold",
        color=INK,
    )
    finish(fig, "claims4_6_phase_bounds.png")


def exploration() -> None:
    rows = sorted(load(5)["rows"], key=lambda row: row["K"])
    k = np.asarray([row["K"] for row in rows], dtype=float)
    observed = np.asarray([row["max_observed_error"] for row in rows])
    bounds = np.asarray([row["bound"] for row in rows])
    actual_rounds = np.asarray([row["rounds"] for row in rows], dtype=float)
    naive_rounds = np.asarray([row["K"] ** 2 * row["N"] for row in rows], dtype=float)

    fig, (err_ax, rounds_ax) = plt.subplots(1, 2, figsize=(12, 4.3))
    err_ax.plot(k, observed, "o-", color=BLUE, linewidth=2.5, label="max observed error")
    err_ax.plot(k, bounds, "s--", color=ORANGE, linewidth=2, label="simultaneous bound")
    err_ax.set_xlabel("K")
    err_ax.set_ylabel("Absolute estimation error")
    err_ax.set_title("128 trials per configuration", loc="left", weight="bold")
    err_ax.legend(frameon=False)
    style_axis(err_ax)

    rounds_ax.loglog(k, actual_rounds, "o-", color=GREEN, linewidth=2.5, label="sample reuse: 2KN")
    rounds_ax.loglog(k, naive_rounds, "s--", color="#7A8699", linewidth=2, label=r"naive: $K^2N$")
    rounds_ax.set_xlabel("K")
    rounds_ax.set_ylabel("Exploration rounds")
    rounds_ax.set_title("Actual phase, not an arithmetic-only check", loc="left", weight="bold")
    rounds_ax.legend(frameon=False)
    style_axis(rounds_ax)
    fig.suptitle(
        "Claim 5: 2K exploration lines estimate every K² pair",
        x=0.06,
        ha="left",
        fontsize=14,
        weight="bold",
        color=INK,
    )
    finish(fig, "claim5_sample_reuse.png")


if __name__ == "__main__":
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "text.color": INK,
        }
    )
    headline()
    needle()
    discretization()
    phase_bounds()
    exploration()
