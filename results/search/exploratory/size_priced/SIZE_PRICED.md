# Size-priced settings (exploratory: size-priced; not registered)

Tier pricing (registered, and used for every result outside this section) charges each tier the main
price table's rate by tier NAME. In X3 the tiers are different model families (small = Qwen2.5-7B, large =
Granite-3.1-8B, xl = Phi-4 14B), so tier pricing makes Granite 20x Qwen 7B. Size pricing charges each call
from its token counts at a per-model rate proportional to parameter count, anchored at Qwen 7B = the main
table's large rate (2.00 / 10.00 USD per M input / output tokens). The same rule prices the label runs, so
the surrogates' cost terms change with it. X6 (7B vs 32B) and X7 (Coder 1.5B vs 7B) are a sensitivity check.
Accuracy is unchanged; only cost, hence the fronts, budgets' targets and HV, change.

## Pricing and true fronts

| setting | tier: model (rate x large) | all-top / all-small cost, tier -> size | true front plans, tier -> size | shared |
|---|---|---|---|---|
| x3_cross_family | small: Qwen2.5-7B-Instruct (1); large: granite-3.1-8b-instruct (1.14); xl: phi-4 (2) | 61.9 -> 3.09 | 11 -> 10 | 9 |
| math_q7_32 | small: Qwen2.5-7B-Instruct (1); large: Qwen2.5-32B-Instruct (4.57) | 23.4 -> 5.35 | 7 -> 6 | 6 |
| math500_q7_32 | small: Qwen2.5-7B-Instruct (1); large: Qwen2.5-32B-Instruct (4.57) | 21.7 -> 4.95 | 10 -> 11 | 10 |
| hotpot_q7_32 | small: Qwen2.5-7B-Instruct (1); large: Qwen2.5-32B-Instruct (4.57) | 20.6 -> 4.71 | 3 -> 3 | 3 |
| code_c15_7 | small: Qwen2.5-Coder-1.5B-Instruct (0.214); large: Qwen2.5-Coder-7B-Instruct (1) | 18.5 -> 4.33 | 7 -> 7 | 7 |

## Mean HV ratio, tier-priced -> size-priced (30 seeds; each distinct budget once)

### x3_cross_family

| method | B=7 | B=15 | B=36 | B=73 | B=146 |
|---|---|---|---|---|---|
| nsga2_pairwise_m3 | 0.970 -> 0.960 | 0.983 -> 0.983 | 0.988 -> 0.986 | 0.988 -> 0.987 | 0.988 -> 0.991 |
| nsga2_pairwise_m5 | 0.970 -> 0.960 | 0.986 -> 0.983 | 0.986 -> 0.983 | 0.988 -> 0.987 | 0.999 -> 1.000 |
| nsga2_indep_add | 0.979 -> 0.974 | 0.979 -> 0.980 | 0.983 -> 0.980 | 0.986 -> 0.984 | 0.989 -> 0.989 |
| nsga2_indep_mult | 0.979 -> 0.974 | 0.979 -> 0.980 | 0.983 -> 0.983 | 0.986 -> 0.984 | 0.990 -> 0.989 |
| nsga2_logit_add | 0.970 -> 0.960 | 0.979 -> 0.980 | 0.982 -> 0.980 | 0.984 -> 0.984 | 0.989 -> 0.989 |
| mopso_pairwise_m3 | 0.970 -> 0.960 | 0.983 -> 0.983 | 0.988 -> 0.986 | 0.988 -> 0.987 | 0.990 -> 0.991 |
| gde3_pairwise_m3 | 0.971 -> 0.965 | 0.983 -> 0.983 | 0.986 -> 0.984 | 0.987 -> 0.987 | 0.993 -> 0.993 |
| nsga2_active_m3 | 0.964 -> 0.962 | 0.985 -> 0.985 | 0.988 -> 0.986 | 0.988 -> 0.990 | 0.995 -> 1.000 |
| abacus | 0.979 -> 0.974 | 0.979 -> 0.980 | 0.983 -> 0.980 | 0.986 -> 0.984 | 0.989 -> 0.990 |
| random | 0.744 -> 0.790 | 0.801 -> 0.839 | 0.846 -> 0.889 | 0.898 -> 0.925 | 0.930 -> 0.959 |
| greedy_uv | 0.941 -> 0.920 | 0.942 -> 0.924 | 0.942 -> 0.924 | 0.942 -> 0.924 | 0.942 -> 0.924 |
| rule_structural | 0.935 -> 0.918 | 0.940 -> 0.923 | 0.940 -> 0.923 | 0.940 -> 0.923 | 0.940 -> 0.923 |
| rule_output | 0.950 -> 0.935 | 0.974 -> 0.974 | 0.974 -> 0.974 | 0.974 -> 0.974 | 0.974 -> 0.974 |
| rule_confident_uv | 0.949 -> 0.933 | 0.968 -> 0.948 | 0.968 -> 0.948 | 0.968 -> 0.948 | 0.968 -> 0.948 |

nsga2_pairwise_m3 minus comparator, W/T/L over the distinct budgets (tau = 0.0134), tier -> size:

| comparator | tier | size |
|---|---|---|
| (a) nsga2_indep_add | 0/5/0 | 0/4/1 |
| (b) abacus | 0/5/0 | 0/4/1 |
| (c) random | 5/0/0 | 5/0/0 |
| (d) greedy_uv | 5/0/0 | 5/0/0 |
| (e) rule_structural | 5/0/0 | 5/0/0 |
| (e) rule_output | 4/1/0 | 2/3/0 |
| (e) rule_confident_uv | 5/0/0 | 5/0/0 |

### math_q7_32

| method | B=4 | B=6 | B=13 |
|---|---|---|---|
| nsga2_pairwise_m3 | 0.985 -> 0.984 | 0.990 -> 0.990 | 0.995 -> 0.995 |
| nsga2_pairwise_m5 | 0.985 -> 0.984 | 0.990 -> 0.990 | 0.995 -> 0.995 |
| nsga2_indep_add | 0.985 -> 0.984 | 0.995 -> 0.995 | 0.999 -> 0.999 |
| nsga2_indep_mult | 0.985 -> 0.984 | 0.995 -> 0.995 | 0.999 -> 0.999 |
| nsga2_logit_add | 0.985 -> 0.984 | 0.995 -> 0.995 | 0.999 -> 0.999 |
| mopso_pairwise_m3 | 0.985 -> 0.984 | 0.990 -> 0.990 | 0.995 -> 0.995 |
| gde3_pairwise_m3 | 0.985 -> 0.984 | 0.990 -> 0.990 | 0.995 -> 0.995 |
| nsga2_active_m3 | 0.963 -> 0.963 | 0.974 -> 0.973 | 0.990 -> 0.990 |
| abacus | 0.985 -> 0.984 | 0.995 -> 0.995 | 0.999 -> 0.999 |
| random | 0.683 -> 0.683 | 0.723 -> 0.725 | 0.874 -> 0.874 |
| greedy_uv | 0.986 -> 0.986 | 0.988 -> 0.987 | 0.988 -> 0.987 |
| rule_structural | 0.925 -> 0.922 | 0.925 -> 0.922 | 0.929 -> 0.926 |
| rule_output | 0.982 -> 0.983 | 0.995 -> 0.995 | 0.999 -> 0.999 |
| rule_confident_uv | 0.965 -> 0.964 | 0.987 -> 0.986 | 0.987 -> 0.986 |

nsga2_pairwise_m3 minus comparator, W/T/L over the distinct budgets (tau = 0.0134), tier -> size:

| comparator | tier | size |
|---|---|---|
| (a) nsga2_indep_add | 0/3/0 | 0/3/0 |
| (b) abacus | 0/3/0 | 0/3/0 |
| (c) random | 3/0/0 | 3/0/0 |
| (d) greedy_uv | 0/3/0 | 0/3/0 |
| (e) rule_structural | 3/0/0 | 3/0/0 |
| (e) rule_output | 0/3/0 | 0/3/0 |
| (e) rule_confident_uv | 1/2/0 | 1/2/0 |

### math500_q7_32

| method | B=4 | B=6 | B=13 |
|---|---|---|---|
| nsga2_pairwise_m3 | 0.962 -> 0.963 | 0.962 -> 0.963 | 0.980 -> 0.980 |
| nsga2_pairwise_m5 | 0.962 -> 0.963 | 0.962 -> 0.963 | 0.969 -> 0.970 |
| nsga2_indep_add | 0.934 -> 0.933 | 0.957 -> 0.956 | 0.961 -> 0.959 |
| nsga2_indep_mult | 0.934 -> 0.933 | 0.957 -> 0.956 | 0.961 -> 0.959 |
| nsga2_logit_add | 0.934 -> 0.933 | 0.957 -> 0.956 | 0.961 -> 0.959 |
| mopso_pairwise_m3 | 0.962 -> 0.963 | 0.962 -> 0.963 | 0.980 -> 0.980 |
| gde3_pairwise_m3 | 0.962 -> 0.963 | 0.962 -> 0.963 | 0.980 -> 0.980 |
| nsga2_active_m3 | 0.949 -> 0.948 | 0.949 -> 0.948 | 0.977 -> 0.977 |
| abacus | 0.934 -> 0.933 | 0.957 -> 0.956 | 0.961 -> 0.959 |
| random | 0.714 -> 0.715 | 0.744 -> 0.748 | 0.871 -> 0.874 |
| greedy_uv | 0.964 -> 0.965 | 0.969 -> 0.971 | 0.969 -> 0.971 |
| rule_structural | 0.914 -> 0.912 | 0.948 -> 0.947 | 0.949 -> 0.948 |
| rule_output | 0.958 -> 0.960 | 0.967 -> 0.968 | 0.973 -> 0.974 |
| rule_confident_uv | 0.914 -> 0.912 | 0.948 -> 0.947 | 0.949 -> 0.948 |

nsga2_pairwise_m3 minus comparator, W/T/L over the distinct budgets (tau = 0.0134), tier -> size:

| comparator | tier | size |
|---|---|---|
| (a) nsga2_indep_add | 2/1/0 | 2/1/0 |
| (b) abacus | 2/1/0 | 2/1/0 |
| (c) random | 3/0/0 | 3/0/0 |
| (d) greedy_uv | 0/3/0 | 0/3/0 |
| (e) rule_structural | 3/0/0 | 3/0/0 |
| (e) rule_output | 0/3/0 | 0/3/0 |
| (e) rule_confident_uv | 3/0/0 | 3/0/0 |

### hotpot_q7_32

| method | B=4 | B=6 |
|---|---|---|
| nsga2_pairwise_m3 | 0.988 -> 0.988 | 0.988 -> 0.988 |
| nsga2_pairwise_m5 | 0.988 -> 0.988 | 0.988 -> 0.988 |
| nsga2_indep_add | 0.953 -> 0.979 | 0.980 -> 0.980 |
| nsga2_indep_mult | 0.953 -> 0.979 | 0.980 -> 0.980 |
| nsga2_logit_add | 0.953 -> 0.952 | 0.953 -> 0.988 |
| mopso_pairwise_m3 | 0.988 -> 0.988 | 0.988 -> 0.988 |
| gde3_pairwise_m3 | 0.988 -> 0.988 | 0.988 -> 0.988 |
| nsga2_active_m3 | 0.988 -> 0.988 | 0.988 -> 0.988 |
| abacus | 0.953 -> 0.979 | 0.980 -> 0.980 |
| random | 0.756 -> 0.755 | 0.825 -> 0.825 |
| greedy_uv | 0.980 -> 0.979 | 0.980 -> 0.979 |
| rule_structural | 0.955 -> 0.955 | 0.962 -> 0.962 |
| rule_output | 0.976 -> 0.976 | 0.988 -> 0.988 |
| rule_confident_uv | 0.950 -> 0.949 | 0.980 -> 0.979 |

nsga2_pairwise_m3 minus comparator, W/T/L over the distinct budgets (tau = 0.0134), tier -> size:

| comparator | tier | size |
|---|---|---|
| (a) nsga2_indep_add | 1/1/0 | 0/2/0 |
| (b) abacus | 1/1/0 | 0/2/0 |
| (c) random | 2/0/0 | 2/0/0 |
| (d) greedy_uv | 0/2/0 | 0/2/0 |
| (e) rule_structural | 2/0/0 | 2/0/0 |
| (e) rule_output | 0/2/0 | 0/2/0 |
| (e) rule_confident_uv | 1/1/0 | 1/1/0 |

### code_c15_7

| method | B=4 | B=6 |
|---|---|---|
| nsga2_pairwise_m3 | 0.946 -> 0.974 | 0.965 -> 0.994 |
| nsga2_pairwise_m5 | 0.946 -> 0.974 | 0.965 -> 0.994 |
| nsga2_indep_add | 0.903 -> 0.902 | 0.962 -> 0.952 |
| nsga2_indep_mult | 0.903 -> 0.902 | 0.962 -> 0.952 |
| nsga2_logit_add | 0.903 -> 0.902 | 0.962 -> 0.952 |
| mopso_pairwise_m3 | 0.946 -> 0.974 | 0.965 -> 0.994 |
| gde3_pairwise_m3 | 0.946 -> 0.974 | 0.965 -> 0.994 |
| nsga2_active_m3 | 0.974 -> 0.975 | 0.974 -> 0.975 |
| abacus | 0.903 -> 0.902 | 0.962 -> 0.952 |
| random | 0.754 -> 0.753 | 0.815 -> 0.814 |
| greedy_uv | 0.978 -> 0.980 | 0.979 -> 0.981 |

nsga2_pairwise_m3 minus comparator, W/T/L over the distinct budgets (tau = 0.0134), tier -> size:

| comparator | tier | size |
|---|---|---|
| (a) nsga2_indep_add | 1/1/0 | 2/0/0 |
| (b) abacus | 1/1/0 | 2/0/0 |
| (c) random | 2/0/0 | 2/0/0 |
| (d) greedy_uv | 0/0/2 | 0/2/0 |

## S6(a) procedure under size pricing (exploratory: size-priced; the registered S6(a) stays FAILED)

Same frozen code, seeds, budgets and decision rule (PASS if the paired 95% CI lower bound of active minus
abacus_nextbest > tau = 0.0134); only the cost model differs. Size-priced result: FAILED.

| B | tier: active / abacus_nextbest / diff / decision | size: active / abacus_nextbest / diff [CI] / decision | size strict diff |
|---|---|---|---|
| 15 | 0.9849 / 0.9788 / +0.0062 / fail | 0.9855 / 0.9796 / +0.0058 [+0.0058, +0.0058] / fail | +0.0704 |
| 36 | 0.9881 / 0.9826 / +0.0056 / fail | 0.9855 / 0.9796 / +0.0059 [+0.0058, +0.0059] / fail | +0.0709 |
| 73 | 0.9884 / 0.9857 / +0.0027 / fail | 0.9898 / 0.9845 / +0.0053 [+0.0050, +0.0056] / fail | +0.0636 |

