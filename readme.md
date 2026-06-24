# Runtime Trust Graph Containment Framework

## Overview

This repository implements a graph-theoretic framework for analyzing compromise propagation in multi-agent systems.

The framework models agent interactions as runtime trust graphs and evaluates containment strategies using Feedback Vertex Sets (FVS).

The primary goal is to study:

* Runtime trust graph extraction
* Runtime τ_FVS computation
* Compromise propagation
* FVS-based containment
* Runtime vs. static containment budgets

---

## Motivation

Multi-agent systems often contain cyclic trust relationships where compromised information can recursively propagate between agents.

Traditional security approaches focus on identifying compromised agents.

This project instead asks:

> What is the minimum revocation effort required to prevent recursive compromise propagation?

To answer this, agent interactions are modeled as directed graphs and analyzed using graph-theoretic containment techniques.


---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd langgraph-fvs-test
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running Experiments

Run the automated experiment framework:

```bash
python experiment_runner.py
```

A new experiment directory will automatically be created:

```text
experiments/
└── exp_001/
```

Each experiment contains:

* Runtime trust graph logs
* Communication traces
* Graph visualizations
* CSV results
* Validation reports

Generated artifacts are intentionally excluded from version control through `.gitignore` so that experiments can be reproduced independently by other researchers.

---

## Local LLM Configuration

The LangGraph experiments were tested using a locally hosted LLM through LM Studio.

Example configuration:

```python
model = ChatOpenAI(
    model="qwen/qwen3-8b",
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)
```

Ensure LM Studio is running and exposing an OpenAI-compatible API endpoint before executing LangGraph-based experiments.

---

## Reproducing Results

To reproduce the experiments:

1. Install all dependencies.
2. Start the local LLM endpoint.
3. Run:

```bash
python experiment_runner.py
```

4. Review generated outputs in:

```text
experiments/exp_xxx/
```

The framework automatically stores:

* Runtime trust graphs
* τ_FVS computations
* FVS selections
* Propagation statistics
* Communication logs
* Validation reports

allowing independent verification of all experimental results.

## Project Structure

```text
langgraph-fvs-test/

├── main.py
├── deterministic_workflow.py
├── runtime_graph.py
├── runtime_logger.py
├── fvs_analysis.py
├── experiment_runner.py
│
├── experiments/      # generated automatically
├── graphs/           # generated automatically
├── runtime_logs/     # generated automatically
│
└── venv/
```

---

## Key Components

### main.py

Initial LangGraph Supervisor experiments using a local LLM.

Used to collect runtime execution traces and validate runtime edge extraction.

---

### deterministic_workflow.py

Controlled compromise propagation experiment.

Implements:

* Compromise injection
* Infection tracking
* FVS revocation
* Containment measurement

---

### fvs_analysis.py

Computes:

* Cycles
* Runtime τ_FVS
* Runtime feedback vertex sets

from logged runtime graphs.

---

### experiment_runner.py

Automated evaluation framework.

Generates:

* Runtime trust graphs
* Runtime τ_FVS values
* Propagation statistics
* Graph visualizations
* Experiment reports

---

## Experimental Methodology

For each execution trace:

1. Construct runtime trust graph.
2. Compute runtime τ_FVS.
3. Inject compromise into a selected agent.
4. Measure downstream propagation.
5. Revoke runtime-computed FVS nodes.
6. Measure propagation after revocation.

Metrics collected:

* Runtime τ_FVS
* FVS nodes
* Number of cycles
* Number of SCCs
* K_before
* K_after
* Message count

---

## Running Experiments

Install dependencies:

```bash
pip install networkx pandas matplotlib
```

Run:

```bash
python experiment_runner.py
```

A new experiment directory will be created automatically:

```text
experiments/
└── exp_001/
```

Each run contains:

* Runtime logs
* Graph visualizations
* Communication traces
* CSV results
* Validation reports


## Research Objective

The framework is intended to evaluate the hypothesis that containment requirements depend on execution topology and that runtime-computed feedback vertex sets can reduce compromise propagation.

The implementation serves as an experimental platform for studying graph-theoretic containment in multi-agent systems.
