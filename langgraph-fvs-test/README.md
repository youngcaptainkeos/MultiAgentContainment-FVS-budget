# Multi-Agent System (MAS) Simulator — FVS Containment Framework

This project contains the empirical simulator, graph containment algorithms, and statistical analysis pipeline for validating Feedback Vertex Set (FVS) based compromise containment in Enterprise Multi-Agent Systems.

---

## 🏢 Architectural Overview

The simulator models an enterprise software development and business workflow across five core departments: **Executive, Research, Engineering, Security, and Operations**. 

### 1. Dynamic Role-Based Runtime Graph Construction
Instead of using static, pre-defined department channels, the simulator dynamically constructs a **Runtime Trust Graph** for each workflow based on participating specialists:
* **Active Specialist Contraction**: Using a directed graph contraction algorithm (`contract_department_graph`), the simulator takes the full department structure and contracts paths around inactive specialists (`u -> v -> w` becomes a shortcut edge `u -> w` if agent `v` is inactive).
* **Workflow Traversal**: The workflow traverses departments in a path determined by the specific enterprise prompt task. Inside each active department, the contracted internal topology is generated and stitched together via cross-department handoffs to form the active runtime graph.

### 2. Bounded Compromise Propagation & Containment
* **Compromise Injection**: A target node on the active workflow path is compromised.
* **Propagation Simulation**: The compromise propagates downstream via peer-to-peer agent communication. The propagation depth (hops from source) is tracked via linear-time BFS.
* **FVS Target Revocation**: The simulator identifies the Feedback Vertex Set of the active runtime graph, revokes these target agents (cutting all feedback and review loops), and re-simulates propagation to evaluate containment effectiveness.

---

## 🛡️ Containment Policy Baselines

To evaluate the mathematical and practical effectiveness of **Runtime FVS**, the simulator evaluates 10 distinct containment policies under identical workflow inputs, compromised nodes, runtime graphs, and seeds:

1. **No Containment**: No containment actions are taken; compromise propagates unhindered.
2. **Random Revocation**: Randomly selects and revokes $τ_{FVS}$ nodes from active candidates (averaged over 100 independent trials per run).
3. **Degree Centrality**: Revokes the top $τ_{FVS}$ nodes with the highest degree centrality.
4. **Betweenness Centrality**: Revokes the top $τ_{FVS}$ nodes with the highest betweenness centrality.
5. **PageRank**: Revokes the top $τ_{FVS}$ nodes with the highest PageRank score.
6. **Supervisor Only**: Revokes department supervisor agents of active departments in the route.
7. **Department Isolation**: Disconnects all inter-department communication edges connected to the compromised department, keeping agent states intact.
8. **Static Enterprise FVS**: Revokes the complete static FVS set calculated once on the global enterprise graph topology (higher operational cost).
9. **Oracle Compromised Node**: Directly revokes the compromised agent itself (blocks propagation but incurs high disruption cost).
10. **Runtime FVS**: The reference dynamic feedback vertex set algorithm (our method).

---

## 📊 Experimental Results Directory Structure

For every run of `python experiment_runner.py`, a new directory `experiments/exp_NNN/` is atomically created. It contains:

### 1. Analytical Summary CSVs
* **`results.csv`**: Raw metrics for the reference Runtime FVS runs.
* **`policy_{name}_summary.csv`**: Run-by-run records for each of the 9 alternative containment baselines.
* **`overall_comparison.csv`**: Compiled aggregate comparison table reporting Mean, Median, Std, and 95% Confidence Intervals for all 10 policies.
* **`statistical_significance.csv`**: The primary hypothesis testing database. For each metric-baseline combination, it logs the chosen test, test statistic, raw $p$-value, False Discovery Rate (FDR) adjusted $p$-value, Cohen's d or rank-biserial effect size, effect size magnitude label, and statistical significance flag.
* **`effect_sizes.csv`**: Summary of percentage improvements and effect sizes.
* **`confidence_interval_validation.csv`**: Validation trace comparing the reported confidence intervals against Student's t recomputations.

### 2. Publication Reports (Markdown & LaTeX)
* **`baseline_significance_summary.md`**:
  - Automatically generated comparison sections detailing performance gains, adjusted p-values, and effect sizes (e.g. Cohen's d).
  - Fully formatted **LaTeX tables** summarizing paired significance test comparisons.
* **`confidence_interval_report.md`**:
  - Mathematical proof and validation logs recomputing 95% CIs directly from raw data using the Student's t-distribution.
  - Flags precision differences relative to standard normal approximations ($z = 1.96$).

### 3. Visualizations (`experiments/exp_NNN/figures/`)
All plots are exported in both **600 DPI PNG** and **vector PDF** formats:
* **Theorem Flow Grid Layouts (`run_NNN_before_after`)**: 4-panel figures showing (a) Runtime Trust Graph, (b) SCC & Feedback Cycles, (c) Before Containment, and (d) After FVS Containment. FVS nodes pop out with double outlines (black-white rings), and unreachable nodes fade to $35\%$ opacity to highlight isolated compromise propagation.
* **Executive Summary Tables (`run_NNN_summary`)**: Standalone, clean summary cards presenting 15 key graph and containment metrics with slate-navy styling.
* **Baseline Comparison Charts**:
  - `baseline_containment_ratio`: Average Containment Ratio with 95% CI error bars.
  - `baseline_k_footprint`: Boxplot comparing K Before vs. K After across all policies.
  - `baseline_propagation_depth`: Boxplot of propagation hops after containment.
  - `baseline_message_reduction`: Bar chart of message count reductions.
  - `baseline_revocation_cost`: Average count of revoked agents (cost of policy).
  - `baseline_runtime_comparison`: Log-scale computational execution times in milliseconds.
  - `baseline_pareto_frontier`: Scatter plot of Containment Ratio vs. Revocation Size, highlighting the optimal Pareto frontier.
  - `baseline_tau_distribution`: Boxplot showing the distribution of revocation sizes by policy.

---

## 🚀 Running the Experiments

### 1. Prerequisites
Install dependencies in your python virtual environment:
```bash
pip install -r requirements.txt
pip install scipy
```

### 2. Run Configuration
Configure runs, seeds, and rotation settings inside `experiment_config.json`:
```json
{
  "runs": 200,
  "enterprise_sizes": [32],
  "workflow_families": 10,
  "prompts_per_family": 10,
  "compromise_rotation": true,
  "seed": 42
}
```

### 3. Execution
Run the simulator to run the 200 workflows, perform baseline testing, compute statistical significance, and generate all plots:
```bash
python experiment_runner.py
```
Outputs will be saved in the next available directory under `experiments/exp_NNN/`.
