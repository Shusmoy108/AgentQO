# Fairness check: Abacus-style with next-best fill (SIMULATED; exploratory, not registered)

Synthetic 3-tier workflows (agentqo/search/scalability.py --interaction-sweep). Each (agents, seed) instance
is drawn once; the sampled pair interactions are then multiplied by 0, 0.5, 1, 2, 4 (1 = the measured
distribution; 0 = purely additive truth, label noise still present). HV ratio vs the best known front
(oracle NSGA-II pop 200 x 300 gens, union with every method's verified plans). 30 seeds per cell.
Methods: nsga2_pairwise (pairwise m 3, registered surrogate), nsga2_active (re-fits pair terms from verified
plans in 4 rounds), nsga2_independence, abacus (exact Pareto DP over the independence estimate),
greedy_uv (stops after 2n+1 plans), random.

## Where interaction-aware search beats Abacus-style (paired over 30 seeds, tau = 0.0134, 95% CI)

Cell = mean HV-ratio difference (method minus comparator) and W/T/L. abacus = leftover budget filled with
random plans; abacus_nextbest = leftover filled with the next non-dominated layers of the independence
estimate (exact layered DP).

### nsga2_pairwise vs abacus, B = 50

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | +0.004 T | +0.003 T | +0.005 T | +0.006 T | +0.025 T |
| 15 | -0.005 T | +0.003 T | +0.003 T | -0.000 T | -0.004 T |
| 20 | -0.014 L | -0.013 T | -0.012 T | -0.015 L | -0.016 T |
| 30 | -0.020 L | -0.011 T | -0.007 T | +0.001 T | +0.015 T |

### nsga2_pairwise vs abacus, B = 100

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | +0.008 T | +0.012 T | +0.012 T | +0.017 T | +0.026 T |
| 15 | -0.001 T | +0.001 T | -0.006 T | -0.017 T | -0.039 L |
| 20 | -0.010 T | -0.010 T | -0.011 T | -0.015 L | -0.015 T |
| 30 | -0.016 L | -0.009 T | -0.003 T | +0.008 T | +0.015 T |

### nsga2_pairwise vs abacus, B = 200

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | +0.011 T | +0.016 W | +0.013 T | +0.014 T | +0.030 W |
| 15 | +0.004 T | +0.009 T | -0.000 T | -0.012 T | -0.021 T |
| 20 | -0.006 T | -0.004 T | -0.006 T | -0.017 L | -0.038 L |
| 30 | -0.018 L | -0.008 T | -0.000 T | +0.010 T | +0.020 T |

### nsga2_active vs abacus, B = 50

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | +0.004 T | +0.029 W | +0.051 W | +0.066 W | +0.087 W |
| 15 | -0.016 L | +0.009 T | +0.028 W | +0.048 W | +0.056 W |
| 20 | -0.032 L | -0.023 L | -0.006 T | +0.008 T | +0.006 T |
| 30 | -0.036 L | -0.022 L | -0.014 L | +0.007 T | +0.031 T |

### nsga2_active vs abacus, B = 100

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | +0.014 W | +0.035 W | +0.063 W | +0.089 W | +0.098 W |
| 15 | +0.015 W | +0.037 W | +0.059 W | +0.055 W | +0.048 W |
| 20 | -0.003 T | +0.017 W | +0.031 W | +0.038 W | +0.058 W |
| 30 | -0.025 L | -0.009 T | +0.006 T | +0.039 W | +0.060 W |

### nsga2_active vs abacus, B = 200

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | +0.020 W | +0.043 W | +0.062 W | +0.081 W | +0.078 W |
| 15 | +0.022 W | +0.047 W | +0.059 W | +0.060 W | +0.058 W |
| 20 | +0.014 W | +0.038 W | +0.054 W | +0.063 W | +0.048 W |
| 30 | -0.007 T | +0.026 W | +0.042 W | +0.066 W | +0.087 W |

### nsga2_pairwise vs abacus_nextbest, B = 50

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | -0.002 T | -0.000 T | +0.002 T | +0.004 T | +0.026 T |
| 15 | -0.007 T | +0.001 T | +0.004 T | +0.006 T | +0.009 T |
| 20 | -0.017 L | -0.019 L | -0.017 L | -0.019 L | -0.016 T |
| 30 | -0.026 L | -0.015 L | -0.011 T | -0.003 T | +0.011 T |

### nsga2_pairwise vs abacus_nextbest, B = 100

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | -0.002 T | +0.005 T | +0.007 T | +0.018 T | +0.032 W |
| 15 | -0.005 T | +0.000 T | +0.003 T | +0.009 T | +0.018 T |
| 20 | -0.012 T | -0.012 T | -0.011 T | -0.011 T | +0.001 T |
| 30 | -0.020 L | -0.011 T | -0.005 T | +0.007 T | +0.017 T |

### nsga2_pairwise vs abacus_nextbest, B = 200

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | -0.002 T | +0.002 T | +0.008 T | +0.020 W | +0.046 W |
| 15 | -0.006 T | +0.003 T | +0.007 T | +0.016 W | +0.027 W |
| 20 | -0.011 T | -0.011 T | -0.009 T | -0.002 T | +0.007 T |
| 30 | -0.020 L | -0.010 T | -0.000 T | +0.015 T | +0.029 W |

### nsga2_active vs abacus_nextbest, B = 50

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | -0.001 T | +0.026 W | +0.048 W | +0.065 W | +0.088 W |
| 15 | -0.019 L | +0.007 T | +0.030 W | +0.054 W | +0.069 W |
| 20 | -0.035 L | -0.029 L | -0.011 T | +0.004 T | +0.005 T |
| 30 | -0.042 L | -0.027 L | -0.018 L | +0.003 T | +0.027 T |

### nsga2_active vs abacus_nextbest, B = 100

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | +0.004 T | +0.028 W | +0.059 W | +0.090 W | +0.104 W |
| 15 | +0.010 T | +0.037 W | +0.067 W | +0.081 W | +0.105 W |
| 20 | -0.005 T | +0.016 W | +0.031 W | +0.042 W | +0.074 W |
| 30 | -0.029 L | -0.012 T | +0.005 T | +0.038 W | +0.061 W |

### nsga2_active vs abacus_nextbest, B = 200

| agents \ scale | x0 | x0.5 | x1 | x2 | x4 |
|---|---|---|---|---|---|
| 10 | +0.007 T | +0.030 W | +0.057 W | +0.087 W | +0.094 W |
| 15 | +0.013 T | +0.041 W | +0.066 W | +0.087 W | +0.106 W |
| 20 | +0.009 T | +0.031 W | +0.052 W | +0.078 W | +0.093 W |
| 30 | -0.009 T | +0.024 W | +0.042 W | +0.070 W | +0.096 W |

Cells (of 20 per budget) where the method WINS / LOSES against abacus:

- nsga2_pairwise, B=50: W 0, L 3 (losses: 20 agents x0, 20 agents x2, 30 agents x0)
- nsga2_pairwise, B=100: W 0, L 3 (losses: 15 agents x4, 20 agents x2, 30 agents x0)
- nsga2_pairwise, B=200: W 2, L 3 (losses: 20 agents x2, 20 agents x4, 30 agents x0)
- nsga2_active, B=50: W 7, L 6 (losses: 15 agents x0, 20 agents x0, 20 agents x0.5, 30 agents x0, 30 agents x0.5, 30 agents x1)
- nsga2_active, B=100: W 16, L 1 (losses: 30 agents x0)
- nsga2_active, B=200: W 19, L 0

Cells (of 20 per budget) where the method WINS / LOSES against abacus_nextbest:

- nsga2_pairwise, B=50: W 0, L 6 (losses: 20 agents x0, 20 agents x0.5, 20 agents x1, 20 agents x2, 30 agents x0, 30 agents x0.5)
- nsga2_pairwise, B=100: W 1, L 1 (losses: 30 agents x0)
- nsga2_pairwise, B=200: W 5, L 1 (losses: 30 agents x0)
- nsga2_active, B=50: W 7, L 6 (losses: 15 agents x0, 20 agents x0, 20 agents x0.5, 30 agents x0, 30 agents x0.5, 30 agents x1)
- nsga2_active, B=100: W 14, L 1 (losses: 30 agents x0)
- nsga2_active, B=200: W 16, L 0

## Mean HV ratio by budget and interaction scale (averaged over 10-30 agents)

| B | scale | abacus | abacus_nextbest | greedy_uv | nsga2_active | nsga2_independence | nsga2_pairwise | random |
|---|---|---|---|---|---|---|---|---|
| 50 | x0 | 0.966 | 0.970 | 0.949 | 0.946 | 0.946 | 0.957 | 0.696 |
| 50 | x0.5 | 0.917 | 0.921 | 0.898 | 0.915 | 0.900 | 0.913 | 0.663 |
| 50 | x1 | 0.872 | 0.875 | 0.847 | 0.887 | 0.856 | 0.869 | 0.641 |
| 50 | x2 | 0.826 | 0.826 | 0.794 | 0.858 | 0.812 | 0.823 | 0.627 |
| 50 | x4 | 0.812 | 0.809 | 0.771 | 0.857 | 0.801 | 0.817 | 0.642 |
| 100 | x0 | 0.970 | 0.975 | 0.949 | 0.970 | 0.950 | 0.965 | 0.726 |
| 100 | x0.5 | 0.925 | 0.928 | 0.898 | 0.945 | 0.908 | 0.924 | 0.697 |
| 100 | x1 | 0.886 | 0.885 | 0.847 | 0.926 | 0.867 | 0.884 | 0.678 |
| 100 | x2 | 0.849 | 0.842 | 0.794 | 0.905 | 0.830 | 0.848 | 0.668 |
| 100 | x4 | 0.851 | 0.831 | 0.771 | 0.917 | 0.828 | 0.848 | 0.688 |
| 200 | x0 | 0.972 | 0.979 | 0.949 | 0.984 | 0.955 | 0.969 | 0.752 |
| 200 | x0.5 | 0.929 | 0.936 | 0.898 | 0.968 | 0.918 | 0.932 | 0.726 |
| 200 | x1 | 0.897 | 0.897 | 0.847 | 0.951 | 0.883 | 0.898 | 0.708 |
| 200 | x2 | 0.873 | 0.859 | 0.794 | 0.940 | 0.852 | 0.872 | 0.701 |
| 200 | x4 | 0.886 | 0.857 | 0.771 | 0.954 | 0.859 | 0.884 | 0.722 |

## Next-best fill: estimate layers needed to fill B (layered Pareto DP)

| agents | B | mean layers | max layers | mean time (s) |
|---|---|---|---|---|
| 10 | 50 | 1.9 | 3 | 0.008 |
| 10 | 100 | 3.0 | 5 | 0.024 |
| 10 | 200 | 4.8 | 8 | 0.058 |
| 15 | 50 | 1.4 | 2 | 0.009 |
| 15 | 100 | 2.2 | 3 | 0.023 |
| 15 | 200 | 3.3 | 5 | 0.045 |
| 20 | 50 | 1.0 | 2 | 0.010 |
| 20 | 100 | 1.5 | 2 | 0.017 |
| 20 | 200 | 2.3 | 4 | 0.030 |
| 30 | 50 | 1.0 | 1 | 0.010 |
| 30 | 100 | 1.0 | 1 | 0.010 |
| 30 | 200 | 1.6 | 2 | 0.022 |

## How Abacus-style scales

Abacus-style never enumerates the 3^n plans. With additive (independence) estimates of cost and accuracy,
the estimated Pareto front can be built agent by agent: keep only the non-dominated partial plans (cost,
estimated accuracy), extend each by the 3 tiers of the next agent, prune again. Work is about n x 3|F|
dominance checks per step, where |F| is the size of the estimated front, not 3^n:

| agents | plans (3^n) | mean estimated-front size | max | mean DP time (s) |
|---|---|---|---|---|
| 10 | 5.90e+04 | 34 | 60 | 0.001 |
| 15 | 1.43e+07 | 57 | 103 | 0.005 |
| 20 | 3.49e+09 | 100 | 183 | 0.010 |
| 30 | 2.06e+14 | 203 | 338 | 0.014 |

The pruning is exact only for the independence estimate. When true pair interactions are strong, the
true front contains plans the additive estimate ranks as dominated, and Abacus-style can only reach
them by its budget-filling picks; that is the regime where the interaction-aware searches can win.
Budget filling: Abacus-style verifies its estimated front spread along cost; when the front is smaller than
B (typical at 10-15 agents, e.g. 34 plans at 10 agents vs B = 50-200) the rest of B is filled with random
plans (logged choice), so at small n its extra budget is effectively random search.

