# Multi-Agent System (MAS) Simulator — FVS Containment Framework

This project contains the empirical simulator, graph containment algorithms, and statistical analysis pipeline for validating Feedback Vertex Set (FVS) based compromise containment in Enterprise Multi-Agent Systems.

Repository URL: [https://github.com/youngcaptainkeos/MultiAgentContainment-FVS-budget/tree/main](https://github.com/youngcaptainkeos/MultiAgentContainment-FVS-budget/tree/main)

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

## 🧪 Experimental Methodology

Our validation pipeline implements a rigorous comparative methodology to evaluate the containment efficacy, operational cost, and decision overhead of the **Runtime FVS** containment policy:

1. **Benchmark Dataset**: 200 distinct enterprise tasks divided into 10 workflow families (e.g., `security_incident_response`, `financial_planning`, `ai_governance`, `infrastructure_deployment`, etc.) representing realistic cross-department operations.
2. **Identical Run Conditions**: For each of the 200 workflows, we keep the starting workflow route, compromised node, dynamic runtime trust graph topology, and random seed **identical** across all tested containment strategies. The containment strategy is the *only* independent variable changed.
3. **Simultaneous Baseline Evaluation**: Each run evaluates the following 10 containment policies:
   - **No Containment**: Allows propagation to terminate naturally without revocation.
   - **Random Revocation**: Revokes $τ_{FVS}$ nodes randomly (averaged over 100 trials).
   - **Degree Centrality**: Revokes the top $τ_{FVS}$ nodes by degree centrality on the runtime graph.
   - **Betweenness Centrality**: Revokes the top $τ_{FVS}$ nodes by betweenness centrality on the runtime graph.
   - **PageRank**: Revokes the top $τ_{FVS}$ nodes by PageRank on the runtime graph.
   - **Supervisor Only**: Revokes department supervisors of active departments in the route.
   - **Department Isolation**: Disconnects all inter-department communication edges connected to the compromised department, keeping agent states intact.
   - **Static Enterprise FVS**: Revokes the complete static FVS set calculated once on the global enterprise graph topology (higher operational cost).
   - **Oracle Compromised Node**: Directly revokes the compromised agent itself (blocks propagation but incurs high disruption cost).
   - **Runtime FVS**: The reference dynamic feedback vertex set algorithm (our method).
4. **Statistical Significance Testing**:
   - Normality of paired differences is automatically verified using the **Shapiro-Wilk test**.
   - If normality assumptions hold, the pipeline performs a **paired t-test**; otherwise, it performs the non-parametric **Wilcoxon signed-rank test**.
   - All raw $p$-values are adjusted using the **Benjamini-Hochberg False Discovery Rate (FDR) control procedure** to correct for multiple comparisons.
   - Effect sizes are computed using **Cohen's d** (for t-tests) and **Rank-biserial correlation** (for Wilcoxon).
5. **Confidence Interval Student-t Verification**:
   - Recomputes 95% Confidence Intervals using the Student's t-distribution critical values ($t_{\text{crit}} \approx 1.972$ for $n=200$) and compares them against standard normal approximation bounds ($z = 1.96$) to log any precision shifts.

---

## 📊 Experimental Results & Sample Directory

A pre-generated sample experiment folder is available in the repository at [experiments/exp_032/](file:///C:/PDocuments/ccbd/langchain%20internals/langgraph-fvs-test/experiments/exp_032) for a detailed, immediate view of the simulator's exports.

### 📈 Current Empirical Results (exp_032 Summary)
* **Runs**: 200 (utilizing the complete 200 prompts dataset)
- **Unique Runtime Graphs**: 151 / 200
- **Average Containment Ratio**: **97.1%**
- **Average Containment Gain**: **12.46 agents saved** (average footprint reduced from $12.85 \rightarrow 0.39$)
- **Average Message Count**: 22.21
- **Average Propagation Depth**: Reduced from **$6.40 \rightarrow 0.39$** hops

### 📁 Output Directory Structure
For every execution, a new directory `experiments/exp_NNN/` is atomically created. It contains:

#### 1. Analytical Summary CSVs
* **`results.csv`**: Raw metrics for the reference Runtime FVS runs.
* **`policy_{name}_summary.csv`**: Run-by-run records for each alternative baseline.
* **`overall_comparison.csv`**: Compiled aggregate comparison table reporting Mean, Median, Std, and 95% Confidence Intervals for all 10 policies.
* **`statistical_significance.csv`**: Primaried hypothesis testing database. Logs Wilcoxon and t-test $p$-values, False Discovery Rate (FDR) adjusted $p$-values, and Cohen's d / rank-biserial effect sizes.
* **`confidence_interval_validation.csv`**: Validation trace verifying intervals against Student's t distribution.

#### 2. Visualizations (`experiments/exp_NNN/figures/`)
All plots are exported in **600 DPI PNG** and **vector PDF** formats:
* **Theorem Flow Grid Layouts (`run_NNN_before_after`)**: 4-panel figures showing (a) Runtime Trust Graph, (b) SCC & Feedback Cycles, (c) Before Containment, and (d) After FVS Containment. 
  - **Node Sizes**: Compromised (`1350`), Infected (`1200`), FVS Nodes (`1150`), and active/inactive nodes (`950`).
  - **Color Saturation**: Active/safe nodes are colored in green (at `alpha=0.35` in Panel d for contrast), compromised in red, infected in yellow, and inactive/revoked in gray (`alpha=0.20` in Panel d).
  - **Edge Widths**: Highlighted workflow paths are drawn at `1.8` (active internal) and `2.0` (active cross) thickness.
* **Executive Summary Tables (`run_NNN_summary`)**: Standalone, clean summary tables presenting key graph metrics.
* **Baseline Comparison Charts**:
  - `baseline_containment_ratio`: Average Containment Ratio with 95% CI error bars.
  - `baseline_k_footprint`: Boxplot comparing K Before vs. K After across all policies.
  - `baseline_propagation_depth`: Boxplot of propagation hops after containment.
  - `baseline_message_reduction`: Bar chart of message count reductions.
  - `baseline_revocation_cost` / `operational_revocation_budget`: Average count of revoked agents (policy operational budget).
  - `baseline_runtime_comparison`: Log-scale computational execution times in milliseconds.
  - `baseline_pareto_frontier`: Scatter plot of Containment Ratio vs. Revocation Size, highlighting the optimal Pareto frontier.
  - `baseline_tau_distribution`: Boxplot showing the distribution of revocation sizes by policy.

---

## 🚀 Running the Experiments

### 1. Clone the Repository
Clone the repository from GitHub:
```bash
git clone https://github.com/youngcaptainkeos/MultiAgentContainment-FVS-budget.git
cd MultiAgentContainment-FVS-budget
```

### 2. Prerequisites
Install dependencies in your python virtual environment:
```bash
pip install -r requirements.txt
pip install scipy
```

### 3. Run Configuration
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

### 4. Execution
Run the simulator to execute the 200 workflows, perform baseline testing, compute statistical significance, and generate all plots:
```bash
python experiment_runner.py
```
Outputs will be saved in the next available directory under `experiments/exp_NNN/`.
