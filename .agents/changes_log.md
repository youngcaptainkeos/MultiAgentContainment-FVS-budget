# MAS Simulator Changes Log

This file records all architectural, logic, and visualization changes implemented in the Runtime Trust Graph Containment Framework.

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

## 3. Publication-Ready Figure Exports & Visual Improvements
- **File**: [experiment_runner.py](file:///c:/PDocuments/ccbd/langchain%20internals/langgraph-fvs-test/experiment_runner.py)
- **Unified Color Palette**: Applied consistently across all figures.
- **Visual Emphasis on Runtime FVS**: Bar charts and boxplots emphasize Runtime FVS with thicker borders (`2.8` line width), darker outlines, and higher drawing order (`zorder=5`).
- **Statistical Significance Brackets**: Added bracket markers for major comparisons (`Runtime FVS vs. Random, Degree, Static FVS, PageRank`) using standard significance stars (`*`, `**`, `***`, `****`, or `ns`) calculated dynamically.
- **Boxplot Enhancements**: Thicker median lines (`1.8` or `3.0` for Runtime FVS), lighter fills (`alpha=0.5`), and thinner whiskers (`0.8`).
- **Pareto Frontier Upgrade**: Dominated region shaded (`alpha=0.18`), frontier line thickened (`3.5`), scatter points styled by baseline color scheme, and label text manually offset to eliminate overlaps.
- **Logarithmic Runtime Chart**: Displays logarithmic overhead comparisons with text-based millisecond and microsecond annotations on top of each bar.
- **Theorem Graph Layout Spacing**: Increased department centers spacing (Research, Engineering, Executive, Security, Operations), enlarged department labels (`fontsize=16`), thickened path connections (`2.8` internal, `3.2` cross), and faded inactive nodes and edges (`alpha=0.08`).
- **NetworkX zorder Parameter Fix**: Resolved a compatibility `TypeError` by programmatically setting `zorder` on the matplotlib collections returned by `nx.draw_networkx_nodes` instead of passing it as a keyword argument.
