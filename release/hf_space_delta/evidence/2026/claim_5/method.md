# Method

Run Algorithm 2 exactly: N observations for each of K buyer-price lines and N
for each of K seller-price lines, updating K cells from each observation. Test
all K^2 L and R estimates against analytic truth across 128 trials per
configuration and use a one-sided exact binomial confidence limit for the
simultaneous failure probability. Also check GFT=L+R+PRO to machine precision.
Reversing both sample-reuse indicators is the conceptual negative control.
