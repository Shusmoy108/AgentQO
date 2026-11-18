## S5d: PARTIAL

nsga2_pairwise_m3 at 10% budget, mean over 30 seeds (decision; docs/search_prereg_s5d.md). Retention = HV of the verified
front's plans with X11 accuracy / with eval accuracy (eval API cost).

| setting | held-out file | B | retention | X11 HV / best X11 front HV | front plans | missing in X11 |
|---|---|---|---|---|---|---|
| math500_q15_7 | results/v2/X11/math500_q15_7/plans/h3_plans.csv | 6 | 0.9702 | 0.9517 | 5.0 | 0 |
| code_c15_7 | results/v2/X11/code_c15_7/plans/h3_plans.csv | 4 | 0.8808 | 0.9192 | 4.0 | 0 |

All registered methods and budgets (reported, not in the decision):

| setting | method | budget | B | retention | X11 HV / best X11 front HV |
|---|---|---|---|---|---|
| code_c15_7 | abacus | 1% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | abacus | 2% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | abacus | 5% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | abacus | 10% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | abacus | 20% | 6 | 0.8992 | 0.9549 |
| code_c15_7 | gde3_pairwise_m3 | 1% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | gde3_pairwise_m3 | 2% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | gde3_pairwise_m3 | 5% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | gde3_pairwise_m3 | 10% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | gde3_pairwise_m3 | 20% | 6 | 0.8701 | 0.9269 |
| code_c15_7 | greedy_uv | 1% | 4 | 0.9013 | 0.9729 |
| code_c15_7 | greedy_uv | 2% | 4 | 0.9013 | 0.9729 |
| code_c15_7 | greedy_uv | 5% | 4 | 0.9013 | 0.9729 |
| code_c15_7 | greedy_uv | 10% | 4 | 0.9013 | 0.9729 |
| code_c15_7 | greedy_uv | 20% | 6 | 0.9038 | 0.9769 |
| code_c15_7 | mopso_pairwise_m3 | 1% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | mopso_pairwise_m3 | 2% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | mopso_pairwise_m3 | 5% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | mopso_pairwise_m3 | 10% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | mopso_pairwise_m3 | 20% | 6 | 0.8701 | 0.9269 |
| code_c15_7 | nsga2_active_m3 | 1% | 4 | 0.8977 | 0.9649 |
| code_c15_7 | nsga2_active_m3 | 2% | 4 | 0.8977 | 0.9649 |
| code_c15_7 | nsga2_active_m3 | 5% | 4 | 0.8977 | 0.9649 |
| code_c15_7 | nsga2_active_m3 | 10% | 4 | 0.8977 | 0.9649 |
| code_c15_7 | nsga2_active_m3 | 20% | 6 | 0.8977 | 0.9649 |
| code_c15_7 | nsga2_indep_add | 1% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_indep_add | 2% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_indep_add | 5% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_indep_add | 10% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_indep_add | 20% | 6 | 0.8992 | 0.9549 |
| code_c15_7 | nsga2_indep_mult | 1% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_indep_mult | 2% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_indep_mult | 5% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_indep_mult | 10% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_indep_mult | 20% | 6 | 0.8992 | 0.9549 |
| code_c15_7 | nsga2_logit_add | 1% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_logit_add | 2% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_logit_add | 5% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_logit_add | 10% | 4 | 0.8979 | 0.8951 |
| code_c15_7 | nsga2_logit_add | 20% | 6 | 0.8992 | 0.9549 |
| code_c15_7 | nsga2_pairwise_m3 | 1% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | nsga2_pairwise_m3 | 2% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | nsga2_pairwise_m3 | 5% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | nsga2_pairwise_m3 | 10% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | nsga2_pairwise_m3 | 20% | 6 | 0.8701 | 0.9269 |
| code_c15_7 | nsga2_pairwise_m5 | 1% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | nsga2_pairwise_m5 | 2% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | nsga2_pairwise_m5 | 5% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | nsga2_pairwise_m5 | 10% | 4 | 0.8808 | 0.9192 |
| code_c15_7 | nsga2_pairwise_m5 | 20% | 6 | 0.8701 | 0.9269 |
| code_c15_7 | random | 1% | 4 | 0.9010 | 0.7492 |
| code_c15_7 | random | 2% | 4 | 0.9010 | 0.7492 |
| code_c15_7 | random | 5% | 4 | 0.9010 | 0.7492 |
| code_c15_7 | random | 10% | 4 | 0.9010 | 0.7492 |
| code_c15_7 | random | 20% | 6 | 0.9042 | 0.8128 |
| math500_q15_7 | abacus | 1% | 4 | 0.9941 | 0.9128 |
| math500_q15_7 | abacus | 2% | 4 | 0.9941 | 0.9128 |
| math500_q15_7 | abacus | 5% | 4 | 0.9941 | 0.9128 |
| math500_q15_7 | abacus | 10% | 6 | 0.9652 | 0.9770 |
| math500_q15_7 | abacus | 20% | 13 | 0.9633 | 0.9818 |
| math500_q15_7 | gde3_pairwise_m3 | 1% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | gde3_pairwise_m3 | 2% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | gde3_pairwise_m3 | 5% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | gde3_pairwise_m3 | 10% | 6 | 0.9700 | 0.9516 |
| math500_q15_7 | gde3_pairwise_m3 | 20% | 13 | 0.9619 | 0.9804 |
| math500_q15_7 | greedy_uv | 1% | 4 | 0.9742 | 0.9404 |
| math500_q15_7 | greedy_uv | 2% | 4 | 0.9742 | 0.9404 |
| math500_q15_7 | greedy_uv | 5% | 4 | 0.9742 | 0.9404 |
| math500_q15_7 | greedy_uv | 10% | 6 | 0.9678 | 0.9426 |
| math500_q15_7 | greedy_uv | 20% | 13 | 0.9678 | 0.9426 |
| math500_q15_7 | mopso_pairwise_m3 | 1% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | mopso_pairwise_m3 | 2% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | mopso_pairwise_m3 | 5% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | mopso_pairwise_m3 | 10% | 6 | 0.9702 | 0.9517 |
| math500_q15_7 | mopso_pairwise_m3 | 20% | 13 | 0.9619 | 0.9804 |
| math500_q15_7 | nsga2_active_m3 | 1% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | nsga2_active_m3 | 2% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | nsga2_active_m3 | 5% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | nsga2_active_m3 | 10% | 6 | 0.9644 | 0.9207 |
| math500_q15_7 | nsga2_active_m3 | 20% | 13 | 0.9738 | 0.9634 |
| math500_q15_7 | nsga2_indep_add | 1% | 4 | 0.9941 | 0.9128 |
| math500_q15_7 | nsga2_indep_add | 2% | 4 | 0.9941 | 0.9128 |
| math500_q15_7 | nsga2_indep_add | 5% | 4 | 0.9941 | 0.9128 |
| math500_q15_7 | nsga2_indep_add | 10% | 6 | 0.9652 | 0.9770 |
| math500_q15_7 | nsga2_indep_add | 20% | 13 | 0.9633 | 0.9818 |
| math500_q15_7 | nsga2_indep_mult | 1% | 4 | 0.9763 | 0.9216 |
| math500_q15_7 | nsga2_indep_mult | 2% | 4 | 0.9763 | 0.9216 |
| math500_q15_7 | nsga2_indep_mult | 5% | 4 | 0.9763 | 0.9216 |
| math500_q15_7 | nsga2_indep_mult | 10% | 6 | 0.9871 | 0.9851 |
| math500_q15_7 | nsga2_indep_mult | 20% | 13 | 0.9633 | 0.9818 |
| math500_q15_7 | nsga2_logit_add | 1% | 4 | 0.9941 | 0.9128 |
| math500_q15_7 | nsga2_logit_add | 2% | 4 | 0.9941 | 0.9128 |
| math500_q15_7 | nsga2_logit_add | 5% | 4 | 0.9941 | 0.9128 |
| math500_q15_7 | nsga2_logit_add | 10% | 6 | 0.9652 | 0.9770 |
| math500_q15_7 | nsga2_logit_add | 20% | 13 | 0.9633 | 0.9818 |
| math500_q15_7 | nsga2_pairwise_m3 | 1% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | nsga2_pairwise_m3 | 2% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | nsga2_pairwise_m3 | 5% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | nsga2_pairwise_m3 | 10% | 6 | 0.9702 | 0.9517 |
| math500_q15_7 | nsga2_pairwise_m3 | 20% | 13 | 0.9619 | 0.9804 |
| math500_q15_7 | nsga2_pairwise_m5 | 1% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | nsga2_pairwise_m5 | 2% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | nsga2_pairwise_m5 | 5% | 4 | 0.9569 | 0.8800 |
| math500_q15_7 | nsga2_pairwise_m5 | 10% | 6 | 0.9702 | 0.9517 |
| math500_q15_7 | nsga2_pairwise_m5 | 20% | 13 | 0.9700 | 0.9804 |
| math500_q15_7 | random | 1% | 4 | 0.9731 | 0.6671 |
| math500_q15_7 | random | 2% | 4 | 0.9731 | 0.6671 |
| math500_q15_7 | random | 5% | 4 | 0.9731 | 0.6671 |
| math500_q15_7 | random | 10% | 6 | 0.9742 | 0.7048 |
| math500_q15_7 | random | 20% | 13 | 0.9710 | 0.8430 |
| math500_q15_7 | rule_confident_uv | 1% | 4 | 0.9559 | 0.8635 |
| math500_q15_7 | rule_confident_uv | 2% | 4 | 0.9559 | 0.8635 |
| math500_q15_7 | rule_confident_uv | 5% | 4 | 0.9559 | 0.8635 |
| math500_q15_7 | rule_confident_uv | 10% | 6 | 0.9678 | 0.9426 |
| math500_q15_7 | rule_confident_uv | 20% | 13 | 0.9678 | 0.9426 |
| math500_q15_7 | rule_output | 1% | 4 | 0.9627 | 0.8613 |
| math500_q15_7 | rule_output | 2% | 4 | 0.9627 | 0.8613 |
| math500_q15_7 | rule_output | 5% | 4 | 0.9627 | 0.8613 |
| math500_q15_7 | rule_output | 10% | 6 | 0.9742 | 0.9404 |
| math500_q15_7 | rule_output | 20% | 13 | 0.9742 | 0.9404 |
| math500_q15_7 | rule_structural | 1% | 4 | 0.9540 | 0.7102 |
| math500_q15_7 | rule_structural | 2% | 4 | 0.9540 | 0.7102 |
| math500_q15_7 | rule_structural | 5% | 4 | 0.9540 | 0.7102 |
| math500_q15_7 | rule_structural | 10% | 6 | 0.9472 | 0.7750 |
| math500_q15_7 | rule_structural | 20% | 13 | 0.9472 | 0.7750 |
