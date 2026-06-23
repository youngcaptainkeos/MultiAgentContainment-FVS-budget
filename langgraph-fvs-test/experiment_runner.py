"""Run numbered, deterministic runtime trust-graph experiments."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "langgraph-fvs-matplotlib")
)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from matplotlib.lines import Line2D

from fvs_analysis import compute_fvs


STATIC_TAU = 2
LAYOUT_SEED = 42
ROOT = Path(__file__).resolve().parent
EXPERIMENTS_DIR = ROOT / "experiments"

NODES = [
    "researcher",
    "writer",
    "reviewer",
    "math",
    "auditor",
    "planner",
    "coder",
    "critic",
    "verifier",
    "summarizer",
    "security",
    "database",
    "api",
    "executor",
    "supervisor",
]

PROMPTS = [
    "Research a company and write a report",
    "Research and perform calculations",
    "Create report and verify findings",
    "Generate security review",
    "Audit database consistency",
    "Plan project and summarize",
    "Code review workflow",
    "Multi-stage research pipeline",
    "Security validation pipeline",
    "End-to-end execution trace",
]

COMPROMISED_NODES = ["researcher", "writer", "math", "coder", "database"]

# Every topology contains all 15 nodes. One-way bridges connect cycle clusters
# without merging them, which keeps the intended minimum FVS sizes explicit.
TOPOLOGIES = {
    "tau_0_dag": [
        ("researcher", "writer"),
        ("researcher", "planner"),
        ("writer", "reviewer"),
        ("writer", "coder"),
        ("planner", "security"),
        ("reviewer", "math"),
        ("coder", "critic"),
        ("security", "database"),
        ("math", "auditor"),
        ("critic", "verifier"),
        ("database", "api"),
        ("auditor", "summarizer"),
        ("verifier", "executor"),
        ("api", "executor"),
        ("summarizer", "supervisor"),
        ("executor", "supervisor"),
    ],
    "tau_1_hub": [
        ("researcher", "writer"),
        ("writer", "reviewer"),
        ("reviewer", "researcher"),
        ("researcher", "math"),
        ("math", "auditor"),
        ("auditor", "researcher"),
        ("researcher", "planner"),
        ("planner", "researcher"),
        ("reviewer", "coder"),
        ("coder", "critic"),
        ("critic", "verifier"),
        ("auditor", "security"),
        ("security", "database"),
        ("database", "api"),
        ("api", "executor"),
        ("executor", "summarizer"),
        ("summarizer", "supervisor"),
    ],
    "tau_2_clusters": [
        ("researcher", "writer"),
        ("writer", "reviewer"),
        ("reviewer", "researcher"),
        ("math", "auditor"),
        ("auditor", "planner"),
        ("planner", "math"),
        ("reviewer", "math"),
        ("writer", "coder"),
        ("coder", "critic"),
        ("critic", "verifier"),
        ("planner", "security"),
        ("security", "database"),
        ("database", "api"),
        ("api", "executor"),
        ("executor", "summarizer"),
        ("summarizer", "supervisor"),
    ],
    "dense_interconnected": [
        ("researcher", "writer"),
        ("writer", "reviewer"),
        ("reviewer", "researcher"),
        ("math", "auditor"),
        ("auditor", "planner"),
        ("planner", "math"),
        ("coder", "critic"),
        ("critic", "verifier"),
        ("verifier", "coder"),
        ("database", "api"),
        ("api", "executor"),
        ("executor", "database"),
        ("supervisor", "summarizer"),
        ("summarizer", "supervisor"),
        ("reviewer", "math"),
        ("planner", "coder"),
        ("verifier", "security"),
        ("security", "database"),
        ("executor", "supervisor"),
    ],
}


def create_experiment_directory() -> tuple[str, Path]:
    """Atomically create and return the next exp_NNN directory."""
    EXPERIMENTS_DIR.mkdir(exist_ok=True)
    number = 1
    while True:
        experiment_id = f"exp_{number:03d}"
        path = EXPERIMENTS_DIR / experiment_id
        try:
            path.mkdir()
            (path / "graphs").mkdir()
            (path / "runtime_logs").mkdir()
            return experiment_id, path
        except FileExistsError:
            number += 1


def build_graph(edges: list[tuple[str, str]]) -> nx.DiGraph:
    """Build a topology containing the complete configured node set."""
    graph = nx.DiGraph()
    graph.add_nodes_from(NODES)
    graph.add_edges_from(edges)
    return graph


def propagate_compromise(graph: nx.DiGraph, compromised_node: str) -> list[str]:
    """Return reachable downstream nodes in deterministic BFS order."""
    if compromised_node not in graph:
        return []

    visited = {compromised_node}
    infected: list[str] = []
    queue = deque([compromised_node])
    while queue:
        current = queue.popleft()
        for neighbor in graph.successors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                infected.append(neighbor)
                queue.append(neighbor)
    return infected


def save_runtime_log(path: Path, edges: list[tuple[str, str]]) -> None:
    """Save a deterministic JSONL edge trace."""
    with path.open("w", encoding="utf-8") as log_file:
        for source, target in edges:
            log_file.write(json.dumps({"source": source, "target": target}) + "\n")


def save_trace_graph(
    path: Path,
    graph: nx.DiGraph,
    compromised_node: str,
    infected_nodes: list[str],
    fvs_nodes: list[str],
    title: str,
) -> None:
    """Render compromise state and FVS membership for one run."""
    positions = nx.spring_layout(graph, seed=LAYOUT_SEED)
    infected = set(infected_nodes)
    fvs = set(fvs_nodes)
    colors = [
        "#e74c3c"
        if node == compromised_node
        else "#f1c40f"
        if node in infected
        else "#2ecc71"
        for node in graph.nodes()
    ]
    borders = ["black" if node in fvs else "#666666" for node in graph.nodes()]
    widths = [3.0 if node in fvs else 1.0 for node in graph.nodes()]

    figure, axis = plt.subplots(figsize=(11, 8))
    nx.draw_networkx(
        graph,
        positions,
        ax=axis,
        node_color=colors,
        edgecolors=borders,
        linewidths=widths,
        node_size=1700,
        font_size=8,
        arrowsize=16,
    )
    axis.set_title(title)
    axis.axis("off")
    axis.legend(
        handles=[
            Line2D([], [], marker="o", linestyle="", color="#e74c3c", label="Compromised"),
            Line2D([], [], marker="o", linestyle="", color="#f1c40f", label="Infected"),
            Line2D([], [], marker="o", linestyle="", color="#2ecc71", label="Normal"),
            Line2D(
                [], [], marker="o", linestyle="", markerfacecolor="white",
                markeredgecolor="black", markeredgewidth=3, label="FVS",
            ),
        ]
    )
    figure.tight_layout()
    figure.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(figure)


def save_scc_graph(path: Path, graph: nx.DiGraph, title: str) -> None:
    """Render each strongly connected component with a distinct color."""
    components = list(nx.strongly_connected_components(graph))
    component_by_node = {
        node: component_index
        for component_index, component in enumerate(components)
        for node in component
    }
    palette = plt.get_cmap("tab20")
    colors = [palette(component_by_node[node] % 20) for node in graph.nodes()]
    positions = nx.spring_layout(graph, seed=LAYOUT_SEED)

    figure, axis = plt.subplots(figsize=(11, 8))
    nx.draw_networkx(
        graph,
        positions,
        ax=axis,
        node_color=colors,
        edgecolors="#444444",
        node_size=1700,
        font_size=8,
        arrowsize=16,
    )
    axis.set_title(f"{title} — Strongly Connected Components")
    axis.axis("off")
    figure.tight_layout()
    figure.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(figure)


def save_aggregate_charts(results: pd.DataFrame, graphs_dir: Path) -> None:
    """Save τ distribution and compromise propagation comparison charts."""
    tau_min = int(results["Runtime τ_FVS"].min())
    tau_max = int(results["Runtime τ_FVS"].max())
    bins = [value - 0.5 for value in range(tau_min, tau_max + 2)]
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.hist(results["Runtime τ_FVS"], bins=bins, edgecolor="black", color="#3498db")
    axis.set_xticks(range(tau_min, tau_max + 1))
    axis.set_xlabel("Runtime τ_FVS")
    axis.set_ylabel("Run count")
    axis.set_title("Runtime τ_FVS Distribution")
    figure.tight_layout()
    figure.savefig(graphs_dir / "runtime_tau_histogram.png", dpi=150)
    plt.close(figure)

    positions = list(range(len(results)))
    width = 0.42
    figure, axis = plt.subplots(figsize=(15, 6))
    axis.bar(
        [position - width / 2 for position in positions],
        results["K Before"],
        width,
        label="K Before",
        color="#f1c40f",
    )
    axis.bar(
        [position + width / 2 for position in positions],
        results["K After"],
        width,
        label="K After",
        color="#2ecc71",
    )
    axis.set_xlabel("Run")
    axis.set_ylabel("Infected downstream agents")
    axis.set_title("Compromise Propagation Before vs After FVS Revocation")
    axis.set_xticks(positions)
    axis.set_xticklabels(results["Run ID"], rotation=90, fontsize=7)
    axis.legend()
    figure.tight_layout()
    figure.savefig(graphs_dir / "k_before_vs_after.png", dpi=150)
    plt.close(figure)


def write_prompts(path: Path) -> None:
    """Persist the exact ordered prompt set used by the experiment."""
    path.write_text(
        "\n".join(f"{index}. {prompt}" for index, prompt in enumerate(PROMPTS, 1)) + "\n",
        encoding="utf-8",
    )


def write_metadata(experiment_id: str, path: Path, run_count: int) -> None:
    """Persist experiment configuration and reproducibility metadata."""
    metadata = {
        "experiment_id": experiment_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "static_tau": STATIC_TAU,
        "layout_seed": LAYOUT_SEED,
        "node_count": len(NODES),
        "nodes": NODES,
        "topologies": list(TOPOLOGIES),
        "prompt_count": len(PROMPTS),
        "run_count": run_count,
        "compromised_node_rotation": COMPROMISED_NODES,
        "networkx_version": nx.__version__,
        "pandas_version": pd.__version__,
    }
    path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def write_validation_report(results: pd.DataFrame, path: Path) -> None:
    """Generate a conclusion from observed values without assuming success."""
    observed = sorted(int(value) for value in results["Runtime τ_FVS"].unique())
    maximum = int(results["Runtime τ_FVS"].max())
    minimum = int(results["Runtime τ_FVS"].min())
    containment_rate = float(results["Containment Success"].mean() * 100)
    average_before = float(results["K Before"].mean())
    average_after = float(results["K After"].mean())
    bound_holds = maximum <= STATIC_TAU

    violating_topologies = sorted(
        results.loc[results["Runtime τ_FVS"] > STATIC_TAU, "Topology"].unique()
    )
    lines = [
        "Runtime τ_FVS Validation Report",
        "================================",
        "",
        f"Observed τ values: {set(observed)}",
        f"Maximum runtime τ: {maximum}",
        f"Minimum runtime τ: {minimum}",
        f"Containment Success Rate: {containment_rate:.1f}%",
        f"Average K Before: {average_before:.2f}",
        f"Average K After: {average_after:.2f}",
        f"Static τ_FVS: {STATIC_TAU}",
        "",
        "Static upper-bound validation: " + ("PASS" if bound_holds else "FAIL"),
    ]
    if bound_holds:
        lines.append("All observed runtime τ values were less than or equal to the static upper bound.")
    else:
        lines.append(
            "The configured static upper bound was exceeded by: "
            + ", ".join(violating_topologies)
            + "."
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "FVS revocation guarantees removal of directed cycles. It does not, by itself, "
            "guarantee zero downstream reachability from every compromised node.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_experiment() -> tuple[str, Path, pd.DataFrame]:
    """Execute every prompt against every topology in a new experiment directory."""
    experiment_id, experiment_dir = create_experiment_directory()
    graphs_dir = experiment_dir / "graphs"
    logs_dir = experiment_dir / "runtime_logs"
    write_prompts(experiment_dir / "prompts.txt")

    topology_analyses = {}
    for topology, edges in TOPOLOGIES.items():
        graph = build_graph(edges)
        cycles = list(nx.simple_cycles(graph))
        tau_runtime, fvs_nodes = compute_fvs(graph)
        topology_analyses[topology] = {
            "graph": graph,
            "cycles": cycles,
            "scc_count": nx.number_strongly_connected_components(graph),
            "tau": tau_runtime,
            "fvs": fvs_nodes,
        }

    records = []
    run_number = 0
    for topology, edges in TOPOLOGIES.items():
        analysis = topology_analyses[topology]
        graph = analysis["graph"]
        for prompt in PROMPTS:
            run_number += 1
            run_id = f"run_{run_number:03d}"
            compromised = COMPROMISED_NODES[(run_number - 1) % len(COMPROMISED_NODES)]
            infected_before = propagate_compromise(graph, compromised)
            revoked_graph = graph.copy()
            revoked_graph.remove_nodes_from(analysis["fvs"])
            infected_after = propagate_compromise(revoked_graph, compromised)
            containment_success = len(infected_before) > 0 and len(infected_after) == 0

            save_runtime_log(logs_dir / f"{run_id}.jsonl", edges)
            title = f"{run_id}: {topology} | compromised={compromised}"
            save_trace_graph(
                graphs_dir / f"{run_id}_trace_graph.png",
                graph,
                compromised,
                infected_before,
                analysis["fvs"],
                title,
            )
            save_scc_graph(graphs_dir / f"{run_id}_scc.png", graph, title)

            records.append(
                {
                    "Experiment ID": experiment_id,
                    "Run ID": run_id,
                    "Prompt": prompt,
                    "Topology": topology,
                    "Nodes": graph.number_of_nodes(),
                    "Edges": graph.number_of_edges(),
                    "Cycle Count": len(analysis["cycles"]),
                    "SCC Count": analysis["scc_count"],
                    "Runtime τ_FVS": analysis["tau"],
                    "FVS Nodes": "|".join(analysis["fvs"]),
                    "Compromised Node": compromised,
                    "K Before": len(infected_before),
                    "K After": len(infected_after),
                    "Containment Success": containment_success,
                }
            )

    results = pd.DataFrame.from_records(records)
    results.to_csv(experiment_dir / "results.csv", index=False)
    save_aggregate_charts(results, graphs_dir)
    write_validation_report(results, experiment_dir / "validation_report.txt")
    write_metadata(experiment_id, experiment_dir / "metadata.json", len(results))
    return experiment_id, experiment_dir, results


def print_summary(experiment_id: str, experiment_dir: Path, results: pd.DataFrame) -> None:
    """Print the experiment location and aggregate observations."""
    observed = set(int(value) for value in results["Runtime τ_FVS"].unique())
    successes = int(results["Containment Success"].sum())
    print(f"Experiment: {experiment_id}")
    print(f"Output: {experiment_dir}")
    print(f"Runs: {len(results)}")
    print(f"Observed runtime τ values: {observed}")
    print(f"Maximum runtime τ: {int(results['Runtime τ_FVS'].max())}")
    print(f"Minimum runtime τ: {int(results['Runtime τ_FVS'].min())}")
    print(f"Containment success rate: {successes}/{len(results)}")
    print(f"Average K Before: {results['K Before'].mean():.2f}")
    print(f"Average K After: {results['K After'].mean():.2f}")


if __name__ == "__main__":
    current_id, current_dir, experiment_results = run_experiment()
    print_summary(current_id, current_dir, experiment_results)
