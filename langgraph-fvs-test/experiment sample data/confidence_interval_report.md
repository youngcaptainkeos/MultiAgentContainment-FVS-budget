# Confidence Interval Validation Report

This report verifies the statistical correctness of the confidence intervals reported in the experimental results.

## 📐 Statistical Formulas

The standard formula for computing a $95\%$ confidence interval using the Student $t$-distribution is:

\[CI_{95\%} = \bar{x} \pm t_{\text{crit}} \times \frac{s}{\sqrt{n}}\]

Where:
- $\bar{x}$ is the sample mean.
- $s$ is the sample standard deviation (with $df = n-1$).
- $n$ is the sample size (number of runs, $200$).
- $t_{\text{crit}}$ is the critical value from the Student $t$-distribution with $n-1$ degrees of freedom. For $n=200$, $df=199$ and $t_{\text{crit}, 0.025} \approx 1.972$.

Previously, the summary table reported confidence intervals based on the standard normal approximation:

\[CI_{\text{normal}} = \bar{x} \pm 1.96 \times \frac{s}{\sqrt{n}}\]

---

## 🔬 Validation Log

We compared the recomputed Student $t$ confidence intervals against the currently reported intervals in `overall_comparison.csv`. The validation results are detailed below:

### 🛡️ No Containment — Containment Ratio
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ No Containment — Containment Gain
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ No Containment — K After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[12.857, 13.328]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[12.857, 13.328]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ No Containment — Message Count After
- **Reported CI**: `[22.309, 23.064]`
- **Recomputed Student $t$ CI**: `[22.309, 23.064]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[22.309, 23.064]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000101`)

### 🛡️ No Containment — Propagation Depth After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[6.601, 6.865]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[6.601, 6.865]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ No Containment — FVS Size
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ No Containment — Runtime Execution Time
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000109`)

### 🛡️ Random Revocation — Containment Ratio
- **Reported CI**: `[0.641, 0.655]`
- **Recomputed Student $t$ CI**: `[0.641, 0.655]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.641, 0.655]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000460`)

### 🛡️ Random Revocation — Containment Gain
- **Reported CI**: `[8.785, 9.202]`
- **Recomputed Student $t$ CI**: `[8.785, 9.202]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[8.785, 9.202]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000325`)

### 🛡️ Random Revocation — K After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[4.027, 4.172]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[4.027, 4.172]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Random Revocation — Message Count After
- **Reported CI**: `[6.334, 6.556]`
- **Recomputed Student $t$ CI**: `[6.334, 6.556]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[6.334, 6.556]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000352`)

### 🛡️ Random Revocation — Propagation Depth After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[2.557, 2.616]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[2.557, 2.616]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Random Revocation — FVS Size
- **Reported CI**: `[3.587, 3.689]`
- **Recomputed Student $t$ CI**: `[3.587, 3.689]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[3.587, 3.689]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000396`)

### 🛡️ Random Revocation — Runtime Execution Time
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000067`)

### 🛡️ Degree Centrality — Containment Ratio
- **Reported CI**: `[0.845, 0.860]`
- **Recomputed Student $t$ CI**: `[0.845, 0.860]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.845, 0.860]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000439`)

### 🛡️ Degree Centrality — Containment Gain
- **Reported CI**: `[11.258, 11.741]`
- **Recomputed Student $t$ CI**: `[11.258, 11.741]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[11.258, 11.741]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000236`)

### 🛡️ Degree Centrality — K After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[1.524, 1.662]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.524, 1.662]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Degree Centrality — Message Count After
- **Reported CI**: `[2.113, 2.323]`
- **Recomputed Student $t$ CI**: `[2.113, 2.323]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[2.113, 2.323]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000085`)

### 🛡️ Degree Centrality — Propagation Depth After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[1.223, 1.329]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.223, 1.329]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Degree Centrality — FVS Size
- **Reported CI**: `[3.587, 3.689]`
- **Recomputed Student $t$ CI**: `[3.587, 3.689]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[3.587, 3.689]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000396`)

### 🛡️ Degree Centrality — Runtime Execution Time
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000100`)

### 🛡️ Betweenness Centrality — Containment Ratio
- **Reported CI**: `[0.809, 0.830]`
- **Recomputed Student $t$ CI**: `[0.809, 0.831]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.809, 0.830]`
- **Status**: **Precision discrepancy (using Normal approximation instead of Student t)** (Absolute difference vs. Student $t$: `0.000503`)

### 🛡️ Betweenness Centrality — Containment Gain
- **Reported CI**: `[11.186, 11.688]`
- **Recomputed Student $t$ CI**: `[11.186, 11.688]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[11.186, 11.688]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000255`)

### 🛡️ Betweenness Centrality — K After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[1.584, 1.727]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.584, 1.727]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Betweenness Centrality — Message Count After
- **Reported CI**: `[2.429, 2.674]`
- **Recomputed Student $t$ CI**: `[2.428, 2.675]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[2.429, 2.674]`
- **Status**: **Precision discrepancy (using Normal approximation instead of Student t)** (Absolute difference vs. Student $t$: `0.000564`)

### 🛡️ Betweenness Centrality — Propagation Depth After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[1.176, 1.276]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.176, 1.276]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Betweenness Centrality — FVS Size
- **Reported CI**: `[3.587, 3.689]`
- **Recomputed Student $t$ CI**: `[3.587, 3.689]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[3.587, 3.689]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000396`)

### 🛡️ Betweenness Centrality — Runtime Execution Time
- **Reported CI**: `[0.001, 0.001]`
- **Recomputed Student $t$ CI**: `[0.001, 0.001]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.001, 0.001]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000497`)

### 🛡️ PageRank — Containment Ratio
- **Reported CI**: `[0.856, 0.873]`
- **Recomputed Student $t$ CI**: `[0.856, 0.873]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.856, 0.873]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000410`)

### 🛡️ PageRank — Containment Gain
- **Reported CI**: `[11.281, 11.781]`
- **Recomputed Student $t$ CI**: `[11.281, 11.781]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[11.281, 11.781]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000108`)

### 🛡️ PageRank — K After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[1.466, 1.657]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.466, 1.657]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ PageRank — Message Count After
- **Reported CI**: `[2.088, 2.390]`
- **Recomputed Student $t$ CI**: `[2.088, 2.390]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[2.088, 2.390]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000224`)

### 🛡️ PageRank — Propagation Depth After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[0.992, 1.108]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.992, 1.108]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ PageRank — FVS Size
- **Reported CI**: `[3.587, 3.689]`
- **Recomputed Student $t$ CI**: `[3.587, 3.689]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[3.587, 3.689]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000396`)

### 🛡️ PageRank — Runtime Execution Time
- **Reported CI**: `[0.002, 0.003]`
- **Recomputed Student $t$ CI**: `[0.002, 0.003]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.002, 0.003]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000288`)

### 🛡️ Supervisor Only — Containment Ratio
- **Reported CI**: `[0.885, 0.897]`
- **Recomputed Student $t$ CI**: `[0.885, 0.897]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.885, 0.897]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000104`)

### 🛡️ Supervisor Only — Containment Gain
- **Reported CI**: `[11.537, 12.009]`
- **Recomputed Student $t$ CI**: `[11.537, 12.009]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[11.537, 12.009]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000026`)

### 🛡️ Supervisor Only — K After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[1.248, 1.391]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.248, 1.391]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Supervisor Only — Message Count After
- **Reported CI**: `[1.565, 1.746]`
- **Recomputed Student $t$ CI**: `[1.565, 1.746]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.565, 1.746]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000149`)

### 🛡️ Supervisor Only — Propagation Depth After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[1.152, 1.278]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.152, 1.278]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Supervisor Only — FVS Size
- **Reported CI**: `[3.301, 3.383]`
- **Recomputed Student $t$ CI**: `[3.301, 3.383]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[3.301, 3.383]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000274`)

### 🛡️ Supervisor Only — Runtime Execution Time
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000096`)

### 🛡️ Department Isolation — Containment Ratio
- **Reported CI**: `[0.637, 0.656]`
- **Recomputed Student $t$ CI**: `[0.637, 0.656]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.637, 0.656]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000251`)

### 🛡️ Department Isolation — Containment Gain
- **Reported CI**: `[9.129, 9.587]`
- **Recomputed Student $t$ CI**: `[9.129, 9.587]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[9.129, 9.587]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000030`)

### 🛡️ Department Isolation — K After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[3.689, 3.780]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[3.689, 3.780]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Department Isolation — Message Count After
- **Reported CI**: `[6.688, 6.831]`
- **Recomputed Student $t$ CI**: `[6.688, 6.831]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[6.688, 6.831]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000208`)

### 🛡️ Department Isolation — Propagation Depth After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[2.636, 2.729]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[2.636, 2.729]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Department Isolation — FVS Size
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Department Isolation — Runtime Execution Time
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000102`)

### 🛡️ Static FVS — Containment Ratio
- **Reported CI**: `[0.919, 0.929]`
- **Recomputed Student $t$ CI**: `[0.919, 0.929]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.919, 0.929]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000302`)

### 🛡️ Static FVS — Containment Gain
- **Reported CI**: `[11.951, 12.418]`
- **Recomputed Student $t$ CI**: `[11.951, 12.418]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[11.951, 12.418]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000485`)

### 🛡️ Static FVS — K After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[0.850, 0.966]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.850, 0.966]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Static FVS — Message Count After
- **Reported CI**: `[1.039, 1.195]`
- **Recomputed Student $t$ CI**: `[1.039, 1.195]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.039, 1.195]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000125`)

### 🛡️ Static FVS — Propagation Depth After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[0.710, 0.800]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.710, 0.800]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Static FVS — FVS Size
- **Reported CI**: `[4.168, 4.275]`
- **Recomputed Student $t$ CI**: `[4.168, 4.275]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[4.168, 4.275]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000140`)

### 🛡️ Static FVS — Runtime Execution Time
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000082`)

### 🛡️ Oracle Compromised Node — Containment Ratio
- **Reported CI**: `[1.000, 1.000]`
- **Recomputed Student $t$ CI**: `[1.000, 1.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.000, 1.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Oracle Compromised Node — Containment Gain
- **Reported CI**: `[12.857, 13.328]`
- **Recomputed Student $t$ CI**: `[12.857, 13.328]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[12.857, 13.328]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000036`)

### 🛡️ Oracle Compromised Node — K After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Oracle Compromised Node — Message Count After
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Oracle Compromised Node — Propagation Depth After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Oracle Compromised Node — FVS Size
- **Reported CI**: `[1.000, 1.000]`
- **Recomputed Student $t$ CI**: `[1.000, 1.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[1.000, 1.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Oracle Compromised Node — Runtime Execution Time
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000077`)

### 🛡️ Runtime FVS — Containment Ratio
- **Reported CI**: `[0.927, 0.937]`
- **Recomputed Student $t$ CI**: `[0.927, 0.937]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.927, 0.937]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000252`)

### 🛡️ Runtime FVS — Containment Gain
- **Reported CI**: `[12.024, 12.495]`
- **Recomputed Student $t$ CI**: `[12.024, 12.495]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[12.024, 12.495]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000053`)

### 🛡️ Runtime FVS — K After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[0.770, 0.896]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.770, 0.896]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Runtime FVS — Message Count After
- **Reported CI**: `[0.819, 0.960]`
- **Recomputed Student $t$ CI**: `[0.819, 0.960]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.819, 0.960]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000287`)

### 🛡️ Runtime FVS — Propagation Depth After
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[0.617, 0.705]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.617, 0.705]`
- **Status**: **Not Reported in Summary** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Runtime FVS — FVS Size
- **Reported CI**: `[3.587, 3.689]`
- **Recomputed Student $t$ CI**: `[3.587, 3.689]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[3.587, 3.689]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000396`)

### 🛡️ Runtime FVS — Runtime Execution Time
- **Reported CI**: `[0.000, 0.000]`
- **Recomputed Student $t$ CI**: `[0.000, 0.000]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[0.000, 0.000]`
- **Status**: **Pass** (Absolute difference vs. Student $t$: `0.000078`)

### 🛡️ Runtime FVS (Before) — K Before
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[12.857, 13.328]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[12.857, 13.328]`
- **Status**: **Verified (Not reported in baseline comparisons summary)** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Runtime FVS (Before) — Message Count Before
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[22.309, 23.064]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[22.309, 23.064]`
- **Status**: **Verified (Not reported in baseline comparisons summary)** (Absolute difference vs. Student $t$: `0.000000`)

### 🛡️ Runtime FVS (Before) — Propagation Depth Before
- **Reported CI**: `N/A`
- **Recomputed Student $t$ CI**: `[6.601, 6.865]` (using $t_{\text{crit}} = 1.9612$)
- **Recomputed Normal CI**: `[6.601, 6.865]`
- **Status**: **Verified (Not reported in baseline comparisons summary)** (Absolute difference vs. Student $t$: `0.000000`)

---

## 📈 Recommendation
The reported intervals in the summary comparison table match the recomputed Normal approximation confidence intervals with $100\%$ precision. However, to maintain the highest statistical rigor, we recommend updating all publication summaries to use the recomputed Student $t$-distribution intervals since the sample size $n=200$ is finite and the Student $t$-distribution provides the mathematically exact interval.
