# Method

Run the actual Exp3 Profit-Max phase on the additive-multiplicative F_K grid.
Sweep T over 64x, two beta coefficients, and 12 seeds. Record beta, achieved
budget, stopping round tau, phase regret, and every term in
beta+T/K+sqrt(KT log(1/delta)). The contract is conditional on reaching beta.
An artificially non-stopping, linear-regret phase is the negative control.
