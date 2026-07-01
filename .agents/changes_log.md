# MAS Simulator Changes Log

This file records all architectural and logic changes implemented in the Runtime Trust Graph Containment Framework to extend department collaboration, run before/after evaluations, track comparative containment metrics, build a reproducible large-scale experimental pipeline, and support publication-quality visualization.

---

## 1. Baseline Containment Policy Evaluation Suite
- **File**: [experiment_runner.py](file:///c:/PDocuments/ccbd/langchain%20internals/langgraph-fvs-test/experiment_runner.py)
- **Change**: Added evaluation of 10 different containment policies for each of the 200 simulation runs. Every policy runs under identical seed, workflow path, compromised node, and propagation configurations.
- **Implemented Baselines**:
  1. **No Containment**: Baseline with no revocation.
  2. **Random Revocation**: Revokes exactly $τ_{FVS}$ nodes randomly (averaged over 100 trials).
  3. **Degree Centrality**: Revokes top $τ_{FVS}$ nodes by degree centrality.
  4. **Betweenness Centrality**: Revokes top $τ_{FVS}$ nodes by betweenness centrality.
  5. **PageRank**: Revokes top $τ_{FVS}$ nodes by PageRank.
  6. **Supervisor-only Revocation**: Revokes only active department supervisor agents.
  7. **Department Isolation**: Disconnects inter-department edges connected to the compromised department without revoking agents.
  8. **Static Enterprise FVS**: Revokes the complete static FVS set of the full enterprise graph.
  9. **Compromised Node Only**: Revokes only the initially compromised node.
  10. **Runtime FVS**: The reference feedback vertex set containment algorithm (existing).

---

## 2. Statistical Analysis and Significance Verification
- **File**: [experiment_runner.py](file:///c:/PDocuments/ccbd/langchain%20internals/langgraph-fvs-test/experiment_runner.py)
- **Significance Tests**: Computes means, medians, standard deviations, and 95% confidence intervals for all policies. Runs paired t-tests (where normality assumptions hold via Shapiro-Wilk) and Wilcoxon signed-rank tests, along with Cohen's d effect sizes.
- **Outputs**:
  - Saved individual summary CSVs for each baseline: `policy_{name}_summary.csv`.
  - Saved overall comparison table: `overall_comparison.csv`.
  - Saved pairwise statistical results: `pairwise_statistical_comparison.csv`.

---

## 3. Publication-Ready Figure Exports
- **File**: [experiment_runner.py](file:///c:/PDocuments/ccbd/langchain%20internals/langgraph-fvs-test/experiment_runner.py)
- **Change**: Added 8 comparative visualization figures exported in both 600 DPI PNG and vector PDF format:
  1. `baseline_containment_ratio.png`/`.pdf`: Average Containment Ratio with 95% confidence intervals.
  2. `baseline_k_footprint.png`/`.pdf`: Boxplot comparing K_before vs K_after for all baselines.
  3. `baseline_propagation_depth.png`/`.pdf`: Boxplot comparing propagation depth after containment.
  4. `baseline_message_reduction.png`/`.pdf`: Bar chart of message count reduction.
  5. `baseline_revocation_cost.png`/`.pdf`: Operational cost comparison (FVS size).
  6. `baseline_runtime_comparison.png`/`.pdf`: Computational execution overhead (log scale).
  7. `baseline_pareto_frontier.png`/`.pdf`: Scatter plot of Containment Ratio vs Operational Cost with highlighted Pareto frontier.
  8. `baseline_tau_distribution.png`/`.pdf`: Distribution of revocation size by policy.
