# SCC Complexity Stratified Statistical Validation

This report contains hypothesis testing, variance analysis, and regression modelling 
to validate the theoretical FVS containment guarantees under varying topological complexities.

## Part 1: Kruskal-Wallis Analysis of Variance per SCC Count Bucket

### SCC Count Bucket: 1

- **Kruskal-Wallis H-test**: $H = 10091.0007$, $p = 0$

#### Tukey HSD Pairwise Comparisons (vs. Runtime FVS):

| Baseline | Mean Difference | p-value | Significant |
| --- | --- | --- | --- |
| No Containment | 0.9432 | 0 | Yes |
| Random Revocation | 0.2637 | 0 | Yes |
| Degree Centrality | 0.0657 | 0 | Yes |
| Betweenness Centrality | 0.0667 | 0 | Yes |
| Pagerank | 0.0503 | 0 | Yes |
| Supervisor Only | 0.0343 | 0 | Yes |
| Department Isolation | 0.2277 | 0 | Yes |
| Static Fvs | 0.0022 | 1 | No |
| Compromised Only | -0.0568 | 0 | Yes |

### SCC Count Bucket: 3

- **Kruskal-Wallis H-test**: $H = 2073.4625$, $p = 0$

#### Tukey HSD Pairwise Comparisons (vs. Runtime FVS):

| Baseline | Mean Difference | p-value | Significant |
| --- | --- | --- | --- |
| No Containment | 0.8819 | 0 | Yes |
| Random Revocation | 0.3717 | 0 | Yes |
| Degree Centrality | 0.1403 | 0 | Yes |
| Betweenness Centrality | 0.3106 | 0 | Yes |
| Pagerank | 0.1403 | 0 | Yes |
| Supervisor Only | 0.0695 | 0.00157 | Yes |
| Department Isolation | 0.5368 | 0 | Yes |
| Static Fvs | 0.0332 | 0.621 | No |
| Compromised Only | -0.1181 | 1.29e-10 | Yes |

## Part 2: OLS Interaction Regression Analysis

Model specification:
$$\text{Containment Ratio} = \beta_0 + \beta_1 \times \text{Initial SCC Count} + \sum \gamma_i D_i + \sum \delta_i (D_i \times \text{Initial SCC Count}) + \epsilon$$
where $D_i$ are dummy variables for other policies (Runtime FVS is the reference category).

- **Number of Observations**: 20000
- **Residual Degrees of Freedom**: 19980
- **R-squared**: 0.8070

| Variable | Coefficient | Std Error | t-statistic | p-value | Significant |
| --- | --- | --- | --- | --- | --- |
| Intercept | 0.9739 | 0.0063 | 154.696 | 0 | Yes |
| Initial Scc Count | -0.0307 | 0.0040 | -7.689 | 1.55e-14 | Yes |
| Betweenness Centrality | 0.0552 | 0.0089 | 6.199 | 5.79e-10 | Yes |
| Compromised Only | 0.0261 | 0.0089 | 2.928 | 0.00342 | Yes |
| Degree Centrality | -0.0284 | 0.0089 | -3.191 | 0.00142 | Yes |
| Department Isolation | -0.0732 | 0.0089 | -8.225 | 2.07e-16 | Yes |
| No Containment | -0.9739 | 0.0089 | -109.387 | 0 | Yes |
| Pagerank | -0.0053 | 0.0089 | -0.600 | 0.548 | No |
| Random Revocation | -0.2097 | 0.0089 | -23.550 | 5.59e-121 | Yes |
| Static Fvs | 0.0133 | 0.0089 | 1.490 | 0.136 | No |
| Supervisor Only | -0.0168 | 0.0089 | -1.882 | 0.0599 | No |
| Betweenness Centrality X Scc Count | -0.1219 | 0.0056 | -21.602 | 2.55e-102 | Yes |
| Compromised Only X Scc Count | 0.0307 | 0.0056 | 5.437 | 5.48e-08 | Yes |
| Degree Centrality X Scc Count | -0.0373 | 0.0056 | -6.610 | 3.95e-11 | Yes |
| Department Isolation X Scc Count | -0.1545 | 0.0056 | -27.372 | 5.67e-162 | Yes |
| No Containment X Scc Count | 0.0307 | 0.0056 | 5.437 | 5.48e-08 | Yes |
| Pagerank X Scc Count | -0.0450 | 0.0056 | -7.968 | 1.69e-15 | Yes |
| Random Revocation X Scc Count | -0.0540 | 0.0056 | -9.565 | 1.24e-21 | Yes |
| Static Fvs X Scc Count | -0.0155 | 0.0056 | -2.744 | 0.00608 | Yes |
| Supervisor Only X Scc Count | -0.0176 | 0.0056 | -3.116 | 0.00184 | Yes |

### Key Interpretation
- **Intercept**: Represents the baseline containment ratio of **Runtime FVS** when the graph has 0 SCCs.
- **Initial SCC Count**: Measures how the containment ratio of the reference policy (Runtime FVS) changes per additional SCC.
- **Interaction terms**: Measure the relative degradation of baseline policies compared to Runtime FVS as the SCC count increases. A significant negative interaction coefficient indicates that increasing complexity statistically degrades the baseline policy's containment ratio faster than Runtime FVS.
