"""
Report generation for experiments.

Generates summary reports and figures for H1, H2, H3 experiments.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json

import numpy as np


def generate_h1_report(
    analysis: Dict[str, Any],
    output_dir: Optional[Path] = None,
) -> str:
    """Generate H1 experiment report.
    
    H1: Downstream importance varies across nodes.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("H1 EXPERIMENT REPORT: Epistemic Criticality Distribution")
    lines.append("=" * 60)
    lines.append("")
    
    # Hypothesis result
    h1_holds = analysis.get("h1_holds", False)
    lines.append(f"H1 HOLDS: {'YES ✓' if h1_holds else 'NO ✗'}")
    lines.append("")
    
    # Evidence
    evidence = analysis.get("h1_evidence", {})
    lines.append("Evidence:")
    lines.append(f"  - Consequence range: {evidence.get('range_actual', 0):.4f}")
    lines.append(f"    (threshold: {evidence.get('range_threshold', 0):.4f})")
    lines.append(f"  - Coefficient of variation: {evidence.get('cv_actual', 0):.4f}")
    lines.append(f"    (threshold: {evidence.get('cv_threshold', 0):.4f})")
    lines.append("")
    
    # Distribution statistics
    stats = analysis.get("statistics", {})
    lines.append("Consequence Distribution Statistics:")
    lines.append(f"  - Mean: {stats.get('mean', 0):.4f}")
    lines.append(f"  - Std: {stats.get('std', 0):.4f}")
    lines.append(f"  - Min: {stats.get('min', 0):.4f}")
    lines.append(f"  - Max: {stats.get('max', 0):.4f}")
    lines.append("")
    
    # Correlations
    corrs = analysis.get("correlations", {})
    lines.append("Correlations with Structural Features:")
    lines.append(f"  - Depth: {corrs.get('depth', 0):.4f}")
    lines.append(f"  - Fan-out: {corrs.get('fan_out', 0):.4f}")
    lines.append(f"  - Downstream reach: {corrs.get('downstream_reach', 0):.4f}")
    lines.append("")
    
    # Node ranking
    lines.append("High Criticality Nodes:")
    for node_id in analysis.get("high_criticality_nodes", [])[:5]:
        lines.append(f"  - {node_id}")
    lines.append("")
    
    lines.append("Low Criticality Nodes:")
    for node_id in analysis.get("low_criticality_nodes", [])[:5]:
        lines.append(f"  - {node_id}")
    lines.append("")
    
    lines.append("=" * 60)
    
    report = "\n".join(lines)
    
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "h1_report.txt", "w") as f:
            f.write(report)
        with open(output_dir / "h1_analysis.json", "w") as f:
            # Filter out non-serializable parts
            serializable = {k: v for k, v in analysis.items() 
                          if k != "node_ranking"}
            json.dump(serializable, f, indent=2, default=str)
    
    return report


def generate_h2_report(
    analysis: Dict[str, Any],
    output_dir: Optional[Path] = None,
) -> str:
    """Generate H2 experiment report.
    
    H2: EC can be predicted better than baselines.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("H2 EXPERIMENT REPORT: EC Prediction")
    lines.append("=" * 60)
    lines.append("")
    
    # Hypothesis result
    h2_holds = analysis.get("h2_holds", False)
    lines.append(f"H2 HOLDS: {'YES ✓' if h2_holds else 'NO ✗'}")
    lines.append("")
    
    # Best model
    lines.append(f"Best Model: {analysis.get('best_model', 'N/A')}")
    lines.append(f"Spearman Correlation: {analysis.get('spearman_correlation', 0):.4f}")
    lines.append(f"Prediction Overhead: {analysis.get('overhead_ms', 0):.2f} ms")
    lines.append("")
    
    # Comparison with baselines
    lines.append("Comparison with Baselines:")
    lines.append(f"  - Beats Confidence-Only: {'YES' if analysis.get('beats_confidence') else 'NO'}")
    lines.append(f"    (margin: {analysis.get('confidence_margin', 0):.4f})")
    lines.append(f"  - At least Structure-Only: {'YES' if analysis.get('at_least_structure') else 'NO'}")
    lines.append(f"    (margin: {analysis.get('structure_margin', 0):.4f})")
    lines.append("")
    
    # Detailed metrics per model
    detailed = analysis.get("detailed_metrics", {})
    if detailed:
        lines.append("Detailed Metrics by Model:")
        lines.append("-" * 50)
        header = f"{'Model':<20} {'Spearman':>10} {'MAE':>10} {'RMSE':>10}"
        lines.append(header)
        lines.append("-" * 50)
        
        for model_name, metrics in detailed.items():
            row = f"{model_name:<20} {metrics.get('spearman_corr', 0):>10.4f} "
            row += f"{metrics.get('mae', 0):>10.4f} {metrics.get('rmse', 0):>10.4f}"
            lines.append(row)
        lines.append("-" * 50)
    
    lines.append("")
    lines.append("=" * 60)
    
    report = "\n".join(lines)
    
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "h2_report.txt", "w") as f:
            f.write(report)
        with open(output_dir / "h2_analysis.json", "w") as f:
            json.dump(analysis, f, indent=2, default=str)
    
    return report


def generate_h3_report(
    analysis: Dict[str, Any],
    output_dir: Optional[Path] = None,
) -> str:
    """Generate H3 experiment report.
    
    H3: EC-based allocation beats baselines.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("H3 EXPERIMENT REPORT: Value-Aware Allocation")
    lines.append("=" * 60)
    lines.append("")
    
    # Hypothesis result
    h3_holds = analysis.get("h3_holds", False)
    lines.append(f"H3 HOLDS: {'YES ✓' if h3_holds else 'NO ✗'}")
    lines.append("")
    
    # Summary statistics
    lines.append("Comparison Summary:")
    lines.append(f"  - Beats Confidence at {analysis.get('beats_confidence_fraction', 0)*100:.1f}% of cost levels")
    lines.append(f"  - Beats Uniform at {analysis.get('beats_uniform_fraction', 0)*100:.1f}% of cost levels")
    lines.append("")
    
    # AUC comparison
    lines.append("Area Under Curve (AUC):")
    lines.append(f"  - AgentQO: {analysis.get('auc_agentqo', 0):.4f}")
    lines.append(f"  - Confidence: {analysis.get('auc_confidence', 0):.4f}")
    lines.append(f"  - Uniform: {analysis.get('auc_uniform', 0):.4f}")
    lines.append("")
    
    lines.append("AUC Improvement:")
    lines.append(f"  - vs Confidence: {analysis.get('auc_improvement_vs_confidence', 0)*100:.2f}%")
    lines.append(f"  - vs Uniform: {analysis.get('auc_improvement_vs_uniform', 0)*100:.2f}%")
    lines.append("")
    
    # Point-by-point comparison
    comparisons = analysis.get("point_comparisons", [])
    if comparisons:
        lines.append("Quality at Each Cost Level:")
        lines.append("-" * 60)
        header = f"{'Cost':>8} {'AgentQO':>10} {'Confidence':>10} {'Uniform':>10} {'Winner':>10}"
        lines.append(header)
        lines.append("-" * 60)
        
        for comp in comparisons:
            aq = comp["agentqo_quality"]
            cq = comp["confidence_quality"]
            uq = comp["uniform_quality"]
            winner = "AgentQO" if comp["beats_confidence"] and comp["beats_uniform"] else ""
            
            row = f"{comp['cost']:>8.2f} {aq:>10.4f} {cq:>10.4f} {uq:>10.4f} {winner:>10}"
            lines.append(row)
        lines.append("-" * 60)
    
    lines.append("")
    lines.append("=" * 60)
    
    report = "\n".join(lines)
    
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "h3_report.txt", "w") as f:
            f.write(report)
        
        # Save analysis without curves (too large)
        analysis_copy = {k: v for k, v in analysis.items() if k != "curves"}
        with open(output_dir / "h3_analysis.json", "w") as f:
            json.dump(analysis_copy, f, indent=2, default=str)
    
    return report


def generate_full_report(
    h1_analysis: Dict[str, Any],
    h2_analysis: Dict[str, Any],
    h3_analysis: Dict[str, Any],
    output_dir: Optional[Path] = None,
) -> str:
    """Generate comprehensive report for all hypotheses."""
    lines = []
    lines.append("=" * 70)
    lines.append("AgentQO PROTOTYPE: FULL EXPERIMENT REPORT")
    lines.append("=" * 70)
    lines.append("")
    
    # Summary
    h1_holds = h1_analysis.get("h1_holds", False)
    h2_holds = h2_analysis.get("h2_holds", False)
    h3_holds = h3_analysis.get("h3_holds", False)
    
    lines.append("SUMMARY")
    lines.append("-" * 70)
    lines.append(f"H1 (EC varies across nodes):        {'PASS ✓' if h1_holds else 'FAIL ✗'}")
    lines.append(f"H2 (EC predictable from embeddings): {'PASS ✓' if h2_holds else 'FAIL ✗'}")
    lines.append(f"H3 (EC allocation beats baselines):  {'PASS ✓' if h3_holds else 'FAIL ✗'}")
    lines.append("")
    
    all_pass = h1_holds and h2_holds and h3_holds
    lines.append(f"OVERALL: {'ALL HYPOTHESES SUPPORTED ✓' if all_pass else 'SOME HYPOTHESES NOT SUPPORTED'}")
    lines.append("")
    
    # Individual reports
    lines.append("")
    lines.append(generate_h1_report(h1_analysis))
    lines.append("")
    lines.append(generate_h2_report(h2_analysis))
    lines.append("")
    lines.append(generate_h3_report(h3_analysis))
    
    report = "\n".join(lines)
    
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "full_report.txt", "w") as f:
            f.write(report)
    
    return report
