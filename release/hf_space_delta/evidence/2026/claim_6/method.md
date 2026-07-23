# Method

Isolate Algorithm 3 by supplying exact L and R, then learn profit with the
paper's optimistic confidence radius and solve its GBB-constrained LP every
round. Sweep T over 64x at fixed K and K over 4x at fixed T, each with 12
seeds. Measure biased-reward pseudo-regret and realized profit shortfall against
K*sqrt(T log(1/delta)). Always playing a negative-profit arm is the negative
control.
