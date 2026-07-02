# Baseline Significance and Effect Size Report

This report statistically validates the performance of **Runtime FVS** containment against alternative baselines. We evaluate paired observations across 200 simulation runs. Shapiro-Wilk test determines the normality of paired differences, paired t-tests or Wilcoxon signed-rank tests assess statistical significance, and Benjamini-Hochberg FDR adjustments correct for multiple hypothesis testing.

---

## 🔬 Per-Baseline Comparison Summaries

### 🛡️ Runtime FVS vs. No Containment

- **K After**:
  - Mean: 0.833 (Runtime FVS) vs. 13.092 (No Containment) [Diff: -12.259]
  - Relative Improvement: **93.6%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -1.000 (Large Effect)

- **Containment Ratio**:
  - Mean: 0.932 (Runtime FVS) vs. 0.000 (No Containment) [Diff: 0.932]
  - Relative Improvement: **100.0%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 1.000 (Large Effect)

- **Containment Gain**:
  - Mean: 12.259 (Runtime FVS) vs. 0.000 (No Containment) [Diff: 12.259]
  - Relative Improvement: **100.0%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 1.000 (Large Effect)

- **Message Count After**:
  - Mean: 0.889 (Runtime FVS) vs. 22.686 (No Containment) [Diff: -21.797]
  - Relative Improvement: **96.1%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -1.000 (Large Effect)

- **Propagation Depth After**:
  - Mean: 0.661 (Runtime FVS) vs. 6.733 (No Containment) [Diff: -6.072]
  - Relative Improvement: **90.2%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -1.000 (Large Effect)

**Conclusion**: Runtime FVS significantly outperformed No Containment in containment effectiveness.

---

### 🛡️ Runtime FVS vs. Random Revocation

- **K After**:
  - Mean: 0.833 (Runtime FVS) vs. 4.099 (Random Revocation) [Diff: -3.266]
  - Relative Improvement: **79.7%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.980 (Large Effect)

- **Containment Ratio**:
  - Mean: 0.932 (Runtime FVS) vs. 0.648 (Random Revocation) [Diff: 0.284]
  - Relative Improvement: **43.8%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.981 (Large Effect)

- **Containment Gain**:
  - Mean: 12.259 (Runtime FVS) vs. 8.993 (Random Revocation) [Diff: 3.266]
  - Relative Improvement: **36.3%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.980 (Large Effect)

- **Message Count After**:
  - Mean: 0.889 (Runtime FVS) vs. 6.445 (Random Revocation) [Diff: -5.555]
  - Relative Improvement: **86.2%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.997 (Large Effect)

- **Propagation Depth After**:
  - Mean: 0.661 (Runtime FVS) vs. 2.586 (Random Revocation) [Diff: -1.925]
  - Relative Improvement: **74.4%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.965 (Large Effect)

**Conclusion**: Runtime FVS significantly outperformed Random Revocation in containment effectiveness.

---

### 🛡️ Runtime FVS vs. Degree Centrality

- **K After**:
  - Mean: 0.833 (Runtime FVS) vs. 1.593 (Degree Centrality) [Diff: -0.760]
  - Relative Improvement: **47.7%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.659 (Large Effect)

- **Containment Ratio**:
  - Mean: 0.932 (Runtime FVS) vs. 0.852 (Degree Centrality) [Diff: 0.080]
  - Relative Improvement: **9.3%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.675 (Large Effect)

- **Containment Gain**:
  - Mean: 12.259 (Runtime FVS) vs. 11.499 (Degree Centrality) [Diff: 0.760]
  - Relative Improvement: **6.6%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.659 (Large Effect)

- **Message Count After**:
  - Mean: 0.889 (Runtime FVS) vs. 2.218 (Degree Centrality) [Diff: -1.329]
  - Relative Improvement: **59.9%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.756 (Large Effect)

- **Propagation Depth After**:
  - Mean: 0.661 (Runtime FVS) vs. 1.276 (Degree Centrality) [Diff: -0.615]
  - Relative Improvement: **48.2%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.696 (Large Effect)

**Conclusion**: Runtime FVS significantly outperformed Degree Centrality in containment effectiveness.

---

### 🛡️ Runtime FVS vs. Betweenness Centrality

- **K After**:
  - Mean: 0.833 (Runtime FVS) vs. 1.655 (Betweenness Centrality) [Diff: -0.823]
  - Relative Improvement: **49.7%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.636 (Large Effect)

- **Containment Ratio**:
  - Mean: 0.932 (Runtime FVS) vs. 0.820 (Betweenness Centrality) [Diff: 0.112]
  - Relative Improvement: **13.7%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.669 (Large Effect)

- **Containment Gain**:
  - Mean: 12.259 (Runtime FVS) vs. 11.437 (Betweenness Centrality) [Diff: 0.822]
  - Relative Improvement: **7.2%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.636 (Large Effect)

- **Message Count After**:
  - Mean: 0.889 (Runtime FVS) vs. 2.551 (Betweenness Centrality) [Diff: -1.662]
  - Relative Improvement: **65.1%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.773 (Large Effect)

- **Propagation Depth After**:
  - Mean: 0.661 (Runtime FVS) vs. 1.226 (Betweenness Centrality) [Diff: -0.565]
  - Relative Improvement: **46.1%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.652 (Large Effect)

**Conclusion**: Runtime FVS significantly outperformed Betweenness Centrality in containment effectiveness.

---

### 🛡️ Runtime FVS vs. PageRank

- **K After**:
  - Mean: 0.833 (Runtime FVS) vs. 1.562 (PageRank) [Diff: -0.729]
  - Relative Improvement: **46.7%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.607 (Large Effect)

- **Containment Ratio**:
  - Mean: 0.932 (Runtime FVS) vs. 0.865 (PageRank) [Diff: 0.067]
  - Relative Improvement: **7.8%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.586 (Large Effect)

- **Containment Gain**:
  - Mean: 12.259 (Runtime FVS) vs. 11.531 (PageRank) [Diff: 0.728]
  - Relative Improvement: **6.3%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.607 (Large Effect)

- **Message Count After**:
  - Mean: 0.889 (Runtime FVS) vs. 2.239 (PageRank) [Diff: -1.349]
  - Relative Improvement: **60.3%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.700 (Large Effect)

- **Propagation Depth After**:
  - Mean: 0.661 (Runtime FVS) vs. 1.050 (PageRank) [Diff: -0.389]
  - Relative Improvement: **37.0%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.546 (Large Effect)

**Conclusion**: Runtime FVS significantly outperformed PageRank in containment effectiveness.

---

### 🛡️ Runtime FVS vs. Supervisor Only

- **K After**:
  - Mean: 0.833 (Runtime FVS) vs. 1.319 (Supervisor Only) [Diff: -0.486]
  - Relative Improvement: **36.9%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.423 (Medium Effect)

- **Containment Ratio**:
  - Mean: 0.932 (Runtime FVS) vs. 0.891 (Supervisor Only) [Diff: 0.041]
  - Relative Improvement: **4.6%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.448 (Medium Effect)

- **Containment Gain**:
  - Mean: 12.259 (Runtime FVS) vs. 11.773 (Supervisor Only) [Diff: 0.486]
  - Relative Improvement: **4.1%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.423 (Medium Effect)

- **Message Count After**:
  - Mean: 0.889 (Runtime FVS) vs. 1.655 (Supervisor Only) [Diff: -0.766]
  - Relative Improvement: **46.3%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.546 (Large Effect)

- **Propagation Depth After**:
  - Mean: 0.661 (Runtime FVS) vs. 1.215 (Supervisor Only) [Diff: -0.554]
  - Relative Improvement: **45.6%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.619 (Large Effect)

**Conclusion**: Runtime FVS significantly outperformed Supervisor Only in containment effectiveness.

---

### 🛡️ Runtime FVS vs. Department Isolation

- **K After**:
  - Mean: 0.833 (Runtime FVS) vs. 3.735 (Department Isolation) [Diff: -2.902]
  - Relative Improvement: **77.7%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.971 (Large Effect)

- **Containment Ratio**:
  - Mean: 0.932 (Runtime FVS) vs. 0.647 (Department Isolation) [Diff: 0.285]
  - Relative Improvement: **44.1%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.977 (Large Effect)

- **Containment Gain**:
  - Mean: 12.259 (Runtime FVS) vs. 9.358 (Department Isolation) [Diff: 2.901]
  - Relative Improvement: **31.0%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.971 (Large Effect)

- **Message Count After**:
  - Mean: 0.889 (Runtime FVS) vs. 6.760 (Department Isolation) [Diff: -5.870]
  - Relative Improvement: **86.8%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.998 (Large Effect)

- **Propagation Depth After**:
  - Mean: 0.661 (Runtime FVS) vs. 2.683 (Department Isolation) [Diff: -2.022]
  - Relative Improvement: **75.4%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.976 (Large Effect)

**Conclusion**: Runtime FVS significantly outperformed Department Isolation in containment effectiveness.

---

### 🛡️ Runtime FVS vs. Static FVS

- **K After**:
  - Mean: 0.833 (Runtime FVS) vs. 0.908 (Static FVS) [Diff: -0.075]
  - Relative Improvement: **8.3%**
  - Test: Wilcoxon signed-rank (adjusted $p$ = 0.0013, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.155 (Small Effect)

- **Containment Ratio**:
  - Mean: 0.932 (Runtime FVS) vs. 0.924 (Static FVS) [Diff: 0.008]
  - Relative Improvement: **0.9%**
  - Test: Wilcoxon signed-rank (adjusted $p$ = 0.0040, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.140 (Small Effect)

- **Containment Gain**:
  - Mean: 12.259 (Runtime FVS) vs. 12.184 (Static FVS) [Diff: 0.075]
  - Relative Improvement: **0.6%**
  - Test: Wilcoxon signed-rank (adjusted $p$ = 0.0013, Significant: **Yes**)
  - Effect Size (Rank-biserial): 0.155 (Small Effect)

- **Message Count After**:
  - Mean: 0.889 (Runtime FVS) vs. 1.117 (Static FVS) [Diff: -0.228]
  - Relative Improvement: **20.4%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.292 (Small Effect)

- **Propagation Depth After**:
  - Mean: 0.661 (Runtime FVS) vs. 0.755 (Static FVS) [Diff: -0.094]
  - Relative Improvement: **12.5%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -0.265 (Small Effect)

**Conclusion**: Runtime FVS significantly outperformed Static FVS in containment effectiveness.

---

### 🛡️ Runtime FVS vs. Oracle Compromised Node

- **K After**:
  - Mean: 0.833 (Runtime FVS) vs. 0.000 (Oracle Compromised Node) [Diff: 0.833]
  - Relative Improvement: **-inf%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 1.000 (Large Effect)

- **Containment Ratio**:
  - Mean: 0.932 (Runtime FVS) vs. 1.000 (Oracle Compromised Node) [Diff: -0.068]
  - Relative Improvement: **-6.8%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -1.000 (Large Effect)

- **Containment Gain**:
  - Mean: 12.259 (Runtime FVS) vs. 13.092 (Oracle Compromised Node) [Diff: -0.833]
  - Relative Improvement: **-6.4%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): -1.000 (Large Effect)

- **Message Count After**:
  - Mean: 0.889 (Runtime FVS) vs. 0.000 (Oracle Compromised Node) [Diff: 0.889]
  - Relative Improvement: **-inf%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 1.000 (Large Effect)

- **Propagation Depth After**:
  - Mean: 0.661 (Runtime FVS) vs. 0.000 (Oracle Compromised Node) [Diff: 0.661]
  - Relative Improvement: **-inf%**
  - Test: Wilcoxon signed-rank (adjusted $p$ < 0.001, Significant: **Yes**)
  - Effect Size (Rank-biserial): 1.000 (Large Effect)

**Conclusion**: Oracle Compromised Node achieved significantly different containment levels (e.g. oracle compromised node isolation).

---

## 📊 LaTeX Publication Tables

### LaTeX Table: Statistical Significance and Effect Sizes
```latex
\begin{table}[ht]
\centering
\caption{Paired Statistical Significance Comparisons of Runtime FVS against Baselines}
\begin{tabular}{llrrrrrc}
\hline
Baseline & Metric & FVS Mean & Base Mean & Mean Diff & adj. $p$-val & Effect Size & Sig. \\
\hline
No Containment & K After & 0.833 & 13.092 & -12.259 & $< 0.001$ & -1.000 (large) & Yes \\
No Containment & Containment Ratio & 0.932 & 0.000 & 0.932 & $< 0.001$ & 1.000 (large) & Yes \\
No Containment & Containment Gain & 12.259 & 0.000 & 12.259 & $< 0.001$ & 1.000 (large) & Yes \\
No Containment & Message Count After & 0.889 & 22.686 & -21.797 & $< 0.001$ & -1.000 (large) & Yes \\
No Containment & Propagation Depth After & 0.661 & 6.733 & -6.072 & $< 0.001$ & -1.000 (large) & Yes \\
Random Revocation & K After & 0.833 & 4.099 & -3.266 & $< 0.001$ & -0.980 (large) & Yes \\
Random Revocation & Containment Ratio & 0.932 & 0.648 & 0.284 & $< 0.001$ & 0.981 (large) & Yes \\
Random Revocation & Containment Gain & 12.259 & 8.993 & 3.266 & $< 0.001$ & 0.980 (large) & Yes \\
Random Revocation & Message Count After & 0.889 & 6.445 & -5.555 & $< 0.001$ & -0.997 (large) & Yes \\
Random Revocation & Propagation Depth After & 0.661 & 2.586 & -1.925 & $< 0.001$ & -0.965 (large) & Yes \\
Degree Centrality & K After & 0.833 & 1.593 & -0.760 & $< 0.001$ & -0.659 (large) & Yes \\
Degree Centrality & Containment Ratio & 0.932 & 0.852 & 0.080 & $< 0.001$ & 0.675 (large) & Yes \\
Degree Centrality & Containment Gain & 12.259 & 11.499 & 0.760 & $< 0.001$ & 0.659 (large) & Yes \\
Degree Centrality & Message Count After & 0.889 & 2.218 & -1.329 & $< 0.001$ & -0.756 (large) & Yes \\
Degree Centrality & Propagation Depth After & 0.661 & 1.276 & -0.615 & $< 0.001$ & -0.696 (large) & Yes \\
Betweenness Centrality & K After & 0.833 & 1.655 & -0.823 & $< 0.001$ & -0.636 (large) & Yes \\
Betweenness Centrality & Containment Ratio & 0.932 & 0.820 & 0.112 & $< 0.001$ & 0.669 (large) & Yes \\
Betweenness Centrality & Containment Gain & 12.259 & 11.437 & 0.822 & $< 0.001$ & 0.636 (large) & Yes \\
Betweenness Centrality & Message Count After & 0.889 & 2.551 & -1.662 & $< 0.001$ & -0.773 (large) & Yes \\
Betweenness Centrality & Propagation Depth After & 0.661 & 1.226 & -0.565 & $< 0.001$ & -0.652 (large) & Yes \\
PageRank & K After & 0.833 & 1.562 & -0.729 & $< 0.001$ & -0.607 (large) & Yes \\
PageRank & Containment Ratio & 0.932 & 0.865 & 0.067 & $< 0.001$ & 0.586 (large) & Yes \\
PageRank & Containment Gain & 12.259 & 11.531 & 0.728 & $< 0.001$ & 0.607 (large) & Yes \\
PageRank & Message Count After & 0.889 & 2.239 & -1.349 & $< 0.001$ & -0.700 (large) & Yes \\
PageRank & Propagation Depth After & 0.661 & 1.050 & -0.389 & $< 0.001$ & -0.546 (large) & Yes \\
Supervisor Only & K After & 0.833 & 1.319 & -0.486 & $< 0.001$ & -0.423 (medium) & Yes \\
Supervisor Only & Containment Ratio & 0.932 & 0.891 & 0.041 & $< 0.001$ & 0.448 (medium) & Yes \\
Supervisor Only & Containment Gain & 12.259 & 11.773 & 0.486 & $< 0.001$ & 0.423 (medium) & Yes \\
Supervisor Only & Message Count After & 0.889 & 1.655 & -0.766 & $< 0.001$ & -0.546 (large) & Yes \\
Supervisor Only & Propagation Depth After & 0.661 & 1.215 & -0.554 & $< 0.001$ & -0.619 (large) & Yes \\
Department Isolation & K After & 0.833 & 3.735 & -2.902 & $< 0.001$ & -0.971 (large) & Yes \\
Department Isolation & Containment Ratio & 0.932 & 0.647 & 0.285 & $< 0.001$ & 0.977 (large) & Yes \\
Department Isolation & Containment Gain & 12.259 & 9.358 & 2.901 & $< 0.001$ & 0.971 (large) & Yes \\
Department Isolation & Message Count After & 0.889 & 6.760 & -5.870 & $< 0.001$ & -0.998 (large) & Yes \\
Department Isolation & Propagation Depth After & 0.661 & 2.683 & -2.022 & $< 0.001$ & -0.976 (large) & Yes \\
Static FVS & K After & 0.833 & 0.908 & -0.075 & 0.0013 & -0.155 (small) & Yes \\
Static FVS & Containment Ratio & 0.932 & 0.924 & 0.008 & 0.0040 & 0.140 (small) & Yes \\
Static FVS & Containment Gain & 12.259 & 12.184 & 0.075 & 0.0013 & 0.155 (small) & Yes \\
Static FVS & Message Count After & 0.889 & 1.117 & -0.228 & $< 0.001$ & -0.292 (small) & Yes \\
Static FVS & Propagation Depth After & 0.661 & 0.755 & -0.094 & $< 0.001$ & -0.265 (small) & Yes \\
Oracle Compromised Node & K After & 0.833 & 0.000 & 0.833 & $< 0.001$ & 1.000 (large) & Yes \\
Oracle Compromised Node & Containment Ratio & 0.932 & 1.000 & -0.068 & $< 0.001$ & -1.000 (large) & Yes \\
Oracle Compromised Node & Containment Gain & 12.259 & 13.092 & -0.833 & $< 0.001$ & -1.000 (large) & Yes \\
Oracle Compromised Node & Message Count After & 0.889 & 0.000 & 0.889 & $< 0.001$ & 1.000 (large) & Yes \\
Oracle Compromised Node & Propagation Depth After & 0.661 & 0.000 & 0.661 & $< 0.001$ & 1.000 (large) & Yes \\
\hline
\end{tabular}
\label{tab:statistical_significance}
\end{table}
```
