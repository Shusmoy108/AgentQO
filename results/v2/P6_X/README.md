# P6_X: API cost for the exploratory settings

scripts/v2/cost_report.py (tag code) run on the Mac at FINAL prep on each X setting's own h3_calls.csv, with the
registered tier price table (configs/v2_prices.yaml: small/large/xl). No model calls. Used only by
P6/search_ground_truth.md (exploratory section). Tier prices are per tier, not per model: within a setting the
ratio large/small is what matters.
