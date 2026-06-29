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
from matplotlib.patches import Circle

from enterprise_prompts import sample_enterprise_prompts
from enterprise_topology import (
    DEPARTMENTS,
    build_enterprise_runtime_trust_graph,
    build_enterprise_topology,
    route_prompt_departments,
    classify_workflow_family,
    compute_graph_hash,
)
from fvs_analysis import compute_fvs


LAYOUT_SEED = 42
ROOT = Path(__file__).resolve().parent
EXPERIMENTS_DIR = ROOT / "experiments"
ENTERPRISE_GRAPH = build_enterprise_topology(seed=LAYOUT_SEED)

NODES = list(ENTERPRISE_GRAPH.nodes())

PROMPT_SCENARIOS = sample_enterprise_prompts()

PROMPTS = [scenario["prompt"] for scenario in PROMPT_SCENARIOS]

COMPROMISED_NODES = NODES
TOPOLOGIES = ["enterprise_departmental_workflow"]
TOPOLOGY_TRACE_IDS = {"enterprise_departmental_workflow": "A"}
EXPECTED_TOPOLOGY_TAU: dict[str, int] = {}
STATIC_TAU = len(NODES)


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
            (path / "communications").mkdir()
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


def propagate_compromise_depth(graph: nx.DiGraph, compromised_node: str) -> tuple[list[str], int]:
    """Return reachable downstream nodes in BFS order and the maximum propagation depth."""
    if compromised_node not in graph:
        return [], 0

    visited = {compromised_node}
    infected: list[str] = []
    distances = {compromised_node: 0}
    queue = deque([compromised_node])
    while queue:
        current = queue.popleft()
        current_dist = distances[current]
        for neighbor in graph.successors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                distances[neighbor] = current_dist + 1
                infected.append(neighbor)
                queue.append(neighbor)
    max_depth = max(distances.values()) if distances else 0
    return infected, max_depth


def generate_agent_output(
    agent: str,
    scenario: dict[str, str],
    compromised_node: str,
) -> str:
    """Generate deterministic role-specific content carrying a poison marker."""
    finding = scenario["finding"]
    estimate = scenario["estimate"]
    category = scenario.get("category", "Enterprise")
    role_outputs = {
        "researcher": f"Researcher: Collected literature regarding {category.lower()} risk and documented evidence. {finding}",
        "writer": f"Writer: Drafted enterprise briefing with evidence, recommendations, and residual risks. {finding}",
        "reviewer": f"Reviewer: Reviewed assumptions, challenged unsupported claims, and requested validation. {finding}",
        "math": f"Finance: Estimated project cost and exposure. {estimate}",
        "auditor": f"Auditor: Policy violation identified and mapped to required remediation evidence. {finding}",
        "planner": f"Planner: Generated implementation roadmap with owners, milestones, and control checkpoints. {estimate}",
        "coder": "Backend Engineer: Implemented authentication service with audit logging, rollback hooks, and service telemetry.",
        "critic": f"Risk Reviewer: Identified unresolved dependency, compliance, and delivery risks. {finding}",
        "verifier": "QA: Detected failing security regression and flagged release readiness for follow-up.",
        "summarizer": f"Executive Communications: Summarized business impact, decision options, and cost exposure. {estimate}",
        "security": "Threat Intelligence: Detected malicious IOC and recommended containment, credential rotation, and monitoring.",
        "database": "Data Platform Engineer: Validated encryption, backup integrity, retention controls, and lineage coverage.",
        "api": "API Engineer: Reviewed authentication, schema validation, idempotency, throttling, and audit requirements.",
        "executor": "Operations Lead: Executed workflow handoff, tracked operational readiness, and recorded rollback conditions.",
        "supervisor": f"Executive Supervisor: Approved escalation path and requested measurable remediation plan. {estimate}",
        "Executive Supervisor": f"Executive Supervisor: Prioritized business risk, funding decision, and accountable owners. {estimate}",
        "Executive Strategy": f"Executive Strategy: Connected the work to enterprise objectives and risk appetite. {finding}",
        "Executive Legal": f"Legal Counsel: Reviewed contractual, privacy, and regulatory exposure. {finding}",
        "Executive Finance": f"Finance: Estimated project cost, business exposure, and funding impact. {estimate}",
        "Executive Communications": "Executive Communications: Prepared stakeholder update with decision context and next steps.",
        "Executive Governance": "Governance Lead: Recorded decision rights, policy exceptions, and escalation requirements.",
        "Research Supervisor": f"Research Supervisor: Scoped evidence collection and review criteria for the task. {finding}",
        "Research Scientist": f"Researcher: Collected literature regarding {category.lower()} migration and risk. {finding}",
        "Research Analyst": f"Research Analyst: Compared evidence, constraints, and likely enterprise impact. {finding}",
        "Research Writer": f"Research Writer: Drafted findings into an executive-ready research report. {finding}",
        "Research Reviewer": "Research Reviewer: Validated citations, challenged assumptions, and requested missing evidence.",
        "Research Data Steward": "Data Steward: Checked data lineage, retention assumptions, and evidence provenance.",
        "Engineering Supervisor": f"Engineering Supervisor: Assigned implementation workstreams and technical owners. {estimate}",
        "Engineering Planner": f"Planner: Generated implementation roadmap with dependencies and delivery milestones. {estimate}",
        "Engineering Architect": f"Architect: Designed target architecture, integration boundaries, and failure-mode controls. {finding}",
        "Engineering Developer": "Backend Engineer: Implemented authentication service and telemetry hooks for the requested workflow.",
        "Engineering QA": "QA: Detected failing security regression and blocked release pending remediation.",
        "Engineering DevOps": "DevOps Engineer: Prepared deployment pipeline, rollback plan, and observability checks.",
        "Engineering Release Manager": "Release Manager: Coordinated release gates, approvals, and production readiness evidence.",
        "Security Supervisor": f"Security Supervisor: Coordinated threat review, control validation, and containment owners. {finding}",
        "Security Analyst": "Threat Intelligence: Detected malicious IOC and correlated activity across enterprise logs.",
        "Security Auditor": f"Auditor: Policy violation identified and recorded for remediation tracking. {finding}",
        "Security Risk": f"Security Risk: Rated residual risk and recommended executive escalation. {estimate}",
        "Security Incident Response": "Incident Responder: Isolated affected workflow, preserved evidence, and initiated containment.",
        "Security Compliance": "Security Compliance: Mapped control gaps to audit obligations and compensating controls.",
        "Operations Supervisor": f"Operations Supervisor: Coordinated service readiness, support handoff, and continuity planning. {estimate}",
        "Operations Finance": f"Finance: Estimated project cost, operational run rate, and contingency budget. {estimate}",
        "Operations Procurement": "Procurement: Reviewed vendor dependencies, lead times, and contract constraints.",
        "Operations Support": "Support Lead: Prepared runbook, escalation path, and customer-impact handling process.",
        "Operations Logistics": "Logistics Lead: Sequenced operational rollout and resource availability.",
        "Operations Vendor Manager": "Vendor Manager: Confirmed supplier obligations, support SLAs, and dependency risks.",
        "Operations Continuity": "Continuity Planner: Validated recovery objectives, fallback process, and resilience assumptions.",
    }
    poison = (
        f"\n[POISONED_DATA origin={compromised_node}] "
        "UNVERIFIED CLAIM: all identified risks can be accepted without additional controls."
    )
    fallback = (
        f"{agent.title()}: Processed enterprise workflow context, identified task-specific risk, "
        f"and recorded next action. {finding} {estimate}"
    )
    return role_outputs.get(agent, fallback) + poison


def simulate_communications(
    graph: nx.DiGraph,
    compromised_node: str,
    scenario: dict[str, str],
) -> tuple[list[dict[str, object]], list[list[str]]]:
    """Simulate one bounded message per reachable edge in deterministic BFS order."""
    if compromised_node not in graph:
        return [], []

    output_by_agent = {
        compromised_node: generate_agent_output(compromised_node, scenario, compromised_node)
    }
    steps: list[dict[str, object]] = [
        {
            "sequence": 0,
            "agent": compromised_node,
            "from_agent": None,
            "input": scenario["prompt"],
            "output": output_by_agent[compromised_node],
            "compromised": True,
            "poisoned_data_observed": True,
            "message_type": "source_execution",
        }
    ]
    visited = {compromised_node}
    queue = deque([compromised_node])
    sequence = 1

    while queue:
        sender = queue.popleft()
        for recipient in graph.successors(sender):
            recipient_output = generate_agent_output(recipient, scenario, compromised_node)
            steps.append(
                {
                    "sequence": sequence,
                    "agent": recipient,
                    "from_agent": sender,
                    "input": output_by_agent[sender],
                    "output": recipient_output,
                    "compromised": recipient == compromised_node,
                    "poisoned_data_observed": True,
                    "message_type": "agent_message",
                }
            )
            sequence += 1
            output_by_agent[recipient] = recipient_output
            if recipient not in visited:
                visited.add(recipient)
                queue.append(recipient)

    infection_paths = [
        nx.shortest_path(graph, compromised_node, infected_node)
        for infected_node in visited
        if infected_node != compromised_node
    ]
    infection_paths.sort(key=lambda path: (len(path), path))
    return steps, infection_paths


HANDOFF_RATIONALES = {
    ("Executive", "Research"): "Executive Supervisor assigned the strategic objective to Research Supervisor for in-depth analysis.",
    ("Research", "Executive"): "Research Supervisor sent the finalized research findings to Executive Supervisor for strategic review.",
    ("Executive", "Engineering"): "Executive Supervisor commissioned Engineering Supervisor to initiate system design and development.",
    ("Engineering", "Executive"): "Engineering Supervisor delivered the release report to Executive Supervisor for review.",
    ("Executive", "Security"): "Executive Supervisor requested Security Supervisor to conduct a compliance and threat audit.",
    ("Security", "Executive"): "Security Risk escalated risk and assessment findings to Executive Supervisor.",
    ("Executive", "Operations"): "Executive Supervisor tasked Operations Supervisor with deployment and procurement coordination.",
    ("Operations", "Executive"): "Operations Supervisor confirmed operational readiness to Executive Supervisor.",
    ("Research", "Engineering"): "Research Writer shared requirements with Engineering Planner to start architecting the solution.",
    ("Research", "Security"): "Research Supervisor consulted Security Supervisor on zero-trust and encryption requirements.",
    ("Engineering", "Research"): "Engineering Supervisor requested Research Supervisor for further feasibility assessment on new tech.",
    ("Engineering", "Security"): "Engineering QA requested Security Auditor to perform a security and vulnerability scan on release.",
    ("Engineering", "Operations"): "Engineering Supervisor coordinated rollout plans with Operations Supervisor.",
    ("Security", "Engineering"): "Security Supervisor advised Engineering Supervisor on containment and patch deployment.",
    ("Security", "Operations"): "Security Supervisor coordinated firewall and access controls with Operations Supervisor.",
    ("Operations", "Security"): "Operations Supervisor requested Security Supervisor to review vendor security compliance.",
    ("Operations", "Research"): "Operations Finance consulted Research Supervisor on research adoption cost estimates.",
}


def generate_execution_narrative(trace: dict[str, object]) -> list[str]:
    """Generate a human-readable case study explanation for the empirical evaluation."""
    route = trace.get("route", [])
    active_nodes = trace.get("active_nodes_list", [])
    compromised = trace.get("compromise_source", "")
    fvs = trace.get("fvs_nodes", [])
    infected_before = trace.get("infected_nodes", [])
    depth_before = trace.get("depth_before", 0)
    depth_after = trace.get("depth_after", 0)
    depts_before = trace.get("affected_depts_before", 0)
    depts_after = trace.get("affected_depts_after", 0)
    efficiency = trace.get("containment_efficiency", 0.0)
    paths = trace.get("infection_paths", [])

    lines = [
        "# Execution Narrative",
        "",
        "### 🏢 Participating Departments",
        " → ".join(route),
        "",
        "### 👥 Specialists Collaborating",
    ]
    
    dept_agents: dict[str, list[str]] = {}
    for node in active_nodes:
        for dept in ["Executive", "Research", "Engineering", "Security", "Operations"]:
            if node.startswith(dept):
                dept_agents.setdefault(dept, []).append(node)
                break
                
    for dept in sorted(dept_agents.keys()):
        agents_str = ", ".join(sorted(dept_agents[dept]))
        lines.append(f"- **{dept}**: {agents_str}")
        
    lines.extend([
        "",
        "### 🔗 Handoff Rationale",
    ])
    for u, v in zip(route, route[1:]):
        if u != v:
            rationale = HANDOFF_RATIONALES.get((u, v), f"Handoff from {u} to {v} for workflow progression.")
            lines.append(f"- **{u} → {v}**: {rationale}")
            
    lines.extend([
        "",
        "### ⚠️ Compromise Propagation Trace",
    ])
    if not infected_before:
        lines.append(f"The compromise remained isolated at the source (**{compromised}**) and did not spread.")
    else:
        lines.append(f"The compromise initiated at **{compromised}** and propagated to the following downstream nodes:")
        for path in paths:
            if len(path) > 1:
                target = path[-1]
                path_str = " → ".join(path)
                lines.append(f"- **{target}** (Path: {path_str})")
                
    lines.extend([
        "",
        "### 🛡️ Feedback Vertex Set (FVS) Containment",
        f"- **FVS Nodes Selected**: {', '.join(fvs) if fvs else 'None (Topology is acyclic)'}",
        f"- **Containment Efficiency**: {efficiency * 100:.1f}%",
        f"- **Propagation Depth**: Reduced from {depth_before} to {depth_after} hops.",
        f"- **Affected Departments**: Reduced from {depts_before} to {depts_after} departments.",
    ])
    if efficiency == 1.0:
        lines.append("Complete containment was achieved. All downstream compromise propagation was blocked.")
    elif efficiency > 0.0:
        lines.append("Partial containment was achieved. Compromise propagation was significantly limited.")
    else:
        lines.append("No active feedback cycles were present, or containment did not change the reachability footprint.")
        
    lines.extend([
        "",
        "---",
        ""
    ])
    return lines


def communication_markdown(trace: dict[str, object]) -> str:
    """Render a communication trace as a reviewer-readable Markdown transcript."""
    lines = generate_execution_narrative(trace)
    
    lines.extend([
        "# Prompt",
        "",
        str(trace["prompt"]),
        "",
        f"**Topology:** {trace['topology']}  ",
        f"**Compromised node:** {trace['compromise_source']}  ",
        f"**Runtime τ_FVS:** {trace['runtime_tau']}  ",
        f"**FVS nodes:** {', '.join(trace['fvs_nodes']) or 'None'}  ",
        f"**Messages before revocation:** {trace['message_count']}  ",
        f"**Messages after revocation:** {trace['message_count_after_revocation']}",
        "",
        "---",
        "",
        "# Communication Before Revocation",
    ])
    for step in trace["steps"]:
        lines.extend(
            [
                "",
                f"## {step['sequence']:02d}. {str(step['agent']).title()}",
                "",
                f"From: {step['from_agent'] or 'User prompt'}",
                "",
                "Input:",
                str(step["input"]),
                "",
                "Output:",
                str(step["output"]),
                "",
                f"Compromised: {step['compromised']}",
                "",
                f"Poisoned Data Observed: {step['poisoned_data_observed']}",
                "",
                "---",
            ]
        )

    lines.extend(["", "# Communication After FVS Revocation"])
    if not trace["post_revocation_steps"]:
        lines.extend(["", "No communication occurred because the compromise source was revoked."])
    else:
        for step in trace["post_revocation_steps"]:
            lines.extend(
                [
                    "",
                    f"## {step['sequence']:02d}. {str(step['agent']).title()}",
                    "",
                    f"From: {step['from_agent'] or 'User prompt'}",
                    "",
                    "Input:",
                    str(step["input"]),
                    "",
                    "Output:",
                    str(step["output"]),
                    "",
                    f"Poisoned Data Observed: {step['poisoned_data_observed']}",
                    "",
                    "---",
                ]
            )
    return "\n".join(lines) + "\n"


def save_communication_trace(
    json_path: Path,
    markdown_path: Path,
    trace: dict[str, object],
) -> None:
    """Store the same communication evidence as structured JSON and Markdown."""
    json_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(communication_markdown(trace), encoding="utf-8")


def save_runtime_log(path: Path, edges: list[tuple[str, str]]) -> None:
    """Save a deterministic JSONL edge trace."""
    with path.open("w", encoding="utf-8") as log_file:
        for source, target in edges:
            log_file.write(json.dumps({"source": source, "target": target}) + "\n")


DEPARTMENT_CENTERS = {
    "Research": (0.0, 3.2),
    "Engineering": (-3.3, 0.4),
    "Executive": (3.3, 0.4),
    "Security": (-3.3, -2.8),
    "Operations": (3.3, -2.8),
}

DEPARTMENT_COLORS = {
    "Executive": "#f8e7d0",
    "Research": "#dceefb",
    "Engineering": "#e4f4df",
    "Security": "#fde2e1",
    "Operations": "#eee6fb",
}


def departmental_layout(graph: nx.DiGraph) -> dict[str, tuple[float, float]]:
    """Return deterministic positions using fixed department centers."""
    positions: dict[str, tuple[float, float]] = {}
    for department, center in DEPARTMENT_CENTERS.items():
        department_nodes = [
            node
            for node, attributes in graph.nodes(data=True)
            if attributes.get("department") == department
        ]
        subgraph = graph.subgraph(department_nodes)
        local_positions = nx.spring_layout(subgraph, seed=LAYOUT_SEED, scale=0.95)
        supervisor = DEPARTMENTS[department]["supervisor"]
        for node, (x_position, y_position) in local_positions.items():
            if node == supervisor:
                positions[node] = center
            else:
                positions[node] = (center[0] + float(x_position), center[1] + float(y_position))
    return positions


def draw_department_backgrounds(axis: plt.Axes) -> None:
    """Draw lightly shaded department regions behind the enterprise graph."""
    for department, center in DEPARTMENT_CENTERS.items():
        axis.add_patch(
            Circle(
                center,
                radius=1.55,
                facecolor=DEPARTMENT_COLORS[department],
                edgecolor="#b8b8b8",
                linewidth=1.0,
                alpha=0.65,
                zorder=0,
            )
        )
        axis.text(
            center[0],
            center[1] + 1.72,
            department,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="#333333",
        )


def save_trace_graph(
    path: Path,
    graph: nx.DiGraph,
    compromised_node: str,
    infected_nodes: list[str],
    fvs_nodes: list[str],
    title: str,
) -> None:
    """Render compromise state and FVS membership for one run."""
    display_graph = ENTERPRISE_GRAPH
    positions = departmental_layout(display_graph)
    active_nodes = set(graph.nodes())
    infected = set(infected_nodes)
    fvs = set(fvs_nodes)
    colors = [
        "#e74c3c"
        if node == compromised_node
        else "#f1c40f"
        if node in infected
        else "#2ecc71"
        if node in active_nodes
        else "#d9d9d9"
        for node in display_graph.nodes()
    ]
    borders = ["black" if node in fvs else "#666666" for node in display_graph.nodes()]
    widths = [3.2 if node in fvs else 1.0 for node in display_graph.nodes()]

    figure, axis = plt.subplots(figsize=(13, 10))
    draw_department_backgrounds(axis)
    inactive_edges = [
        edge for edge in display_graph.edges() if edge[0] not in active_nodes or edge[1] not in active_nodes
    ]
    nx.draw_networkx_edges(
        display_graph,
        positions,
        edgelist=inactive_edges,
        ax=axis,
        edge_color="#d0d0d0",
        alpha=0.35,
        arrows=True,
        arrowsize=9,
        width=0.8,
    )
    nx.draw_networkx_edges(
        graph,
        positions,
        ax=axis,
        edge_color="#606060",
        arrows=True,
        arrowsize=14,
        width=1.4,
    )
    nx.draw_networkx_nodes(
        display_graph,
        positions,
        ax=axis,
        node_color=colors,
        edgecolors=borders,
        linewidths=widths,
        node_size=1150,
    )
    nx.draw_networkx_labels(
        display_graph,
        positions,
        ax=axis,
        font_size=6.5,
        font_family="DejaVu Sans",
    )
    axis.set_title(title)
    axis.axis("off")
    axis.legend(
        handles=[
            Line2D([], [], marker="o", linestyle="", color="#e74c3c", label="Compromised"),
            Line2D([], [], marker="o", linestyle="", color="#f1c40f", label="Infected"),
            Line2D([], [], marker="o", linestyle="", color="#2ecc71", label="Active"),
            Line2D([], [], marker="o", linestyle="", color="#d9d9d9", label="Inactive"),
            Line2D(
                [], [], marker="o", linestyle="", markerfacecolor="white",
                markeredgecolor="black", markeredgewidth=3, label="FVS",
            ),
        ]
    )
    figure.tight_layout()
    figure.savefig(path, dpi=300, bbox_inches="tight")
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
    colors = [palette(component_by_node.get(node, -1) % 20) if node in graph else "#d9d9d9" for node in ENTERPRISE_GRAPH.nodes()]
    positions = departmental_layout(ENTERPRISE_GRAPH)

    figure, axis = plt.subplots(figsize=(13, 10))
    draw_department_backgrounds(axis)
    nx.draw_networkx_edges(
        graph,
        positions,
        ax=axis,
        edge_color="#606060",
        arrows=True,
        arrowsize=14,
        width=1.4,
    )
    nx.draw_networkx_nodes(
        ENTERPRISE_GRAPH,
        positions,
        ax=axis,
        node_color=colors,
        edgecolors="#444444",
        node_size=1150,
    )
    nx.draw_networkx_labels(
        ENTERPRISE_GRAPH,
        positions,
        ax=axis,
        font_size=6.5,
        font_family="DejaVu Sans",
    )
    axis.set_title(f"{title} — Strongly Connected Components")
    axis.axis("off")
    figure.tight_layout()
    figure.savefig(path, dpi=300, bbox_inches="tight")
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
    figure.savefig(graphs_dir / "runtime_tau_histogram.png", dpi=300)
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
    figure.savefig(graphs_dir / "k_before_vs_after.png", dpi=300)
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
        "topology_tau": EXPECTED_TOPOLOGY_TAU,
        "prompt_count": len(PROMPTS),
        "run_count": run_count,
        "summary_files": ["summary_by_topology.csv", "summary_by_tau.csv"],
        "compromised_node_rotation": COMPROMISED_NODES,
        "communication_model": (
            "Deterministic simulation: one source execution and one message per "
            "reachable directed edge, with each reachable node expanded once."
        ),
        "communication_formats": ["json", "markdown"],
        "networkx_version": nx.__version__,
        "pandas_version": pd.__version__,
    }
    path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def build_grouped_summaries(results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate run metrics by topology and by observed runtime tau."""
    aggregations = {
        "Runs": ("Run ID", "count"),
        "Mean K Before": ("K Before", "mean"),
        "Mean K After": ("K After", "mean"),
        "Containment Success Rate (%)": ("Containment Success", lambda values: values.mean() * 100),
        "Mean Message Count": ("Message Count", "mean"),
        "Total Message Count": ("Message Count", "sum"),
        "Mean Containment Efficiency": ("containment_efficiency", "mean"),
        "Mean Propagation Depth Before": ("propagation_depth_before", "mean"),
        "Mean Propagation Depth After": ("propagation_depth_after", "mean"),
    }
    by_topology = (
        results.groupby(["Topology", "Runtime τ_FVS"], sort=False)
        .agg(**aggregations)
        .reset_index()
    )
    by_tau = (
        results.groupby("Runtime τ_FVS", sort=True)
        .agg(Topologies=("Topology", "nunique"), **aggregations)
        .reset_index()
    )
    numeric_columns = [
        "Mean K Before",
        "Mean K After",
        "Containment Success Rate (%)",
        "Mean Message Count",
        "Mean Containment Efficiency",
        "Mean Propagation Depth Before",
        "Mean Propagation Depth After",
    ]
    by_topology[numeric_columns] = by_topology[numeric_columns].round(2)
    by_tau[numeric_columns] = by_tau[numeric_columns].round(2)
    return by_topology, by_tau


def write_validation_report(
    results: pd.DataFrame,
    by_topology: pd.DataFrame,
    by_tau: pd.DataFrame,
    path: Path,
) -> None:
    """Generate a conclusion from observed values without assuming success."""
    observed = sorted(int(value) for value in results["Runtime τ_FVS"].unique())
    maximum = int(results["Runtime τ_FVS"].max())
    minimum = int(results["Runtime τ_FVS"].min())
    containment_rate = float(results["Containment Success"].mean() * 100)
    average_before = float(results["K Before"].mean())
    average_after = float(results["K After"].mean())
    average_messages = float(results["Message Count"].mean())
    total_messages = int(results["Message Count"].sum())
    bound_holds = maximum <= STATIC_TAU
    
    unique_hashes = results["graph_hash"].nunique()
    
    avg_efficiency = float(results["containment_efficiency"].mean() * 100)
    avg_prop_depth_before = float(results["propagation_depth_before"].mean())
    avg_prop_depth_after = float(results["propagation_depth_after"].mean())
    avg_prop_depth_reduction = float(results["propagation_depth_reduction"].mean())
    avg_depts_before = float(results["affected_departments_before"].mean())
    avg_depts_after = float(results["affected_departments_after"].mean())
    avg_depts_reduction = float(results["affected_departments_reduction"].mean())
    avg_msg_reduction = float(results["message_reduction"].mean())

    violating_topologies = sorted(
        results.loc[results["Runtime τ_FVS"] > STATIC_TAU, "Topology"].unique()
    )
    lines = [
        "Runtime τ_FVS Validation Report",
        "================================",
        "",
        f"Unique Runtime Graphs: {unique_hashes}/{len(results)}",
        f"Observed τ values: {set(observed)}",
        f"Maximum runtime τ: {maximum}",
        f"Minimum runtime τ: {minimum}",
        f"Containment Success Rate: {containment_rate:.1f}%",
        f"Average Containment Efficiency: {avg_efficiency:.1f}%",
        f"Average K Before: {average_before:.2f}",
        f"Average K After: {average_after:.2f}",
        f"Average Message Count: {average_messages:.2f}",
        f"Total Agent-to-Agent Messages: {total_messages}",
        f"Average Propagation Depth Before: {avg_prop_depth_before:.2f}",
        f"Average Propagation Depth After: {avg_prop_depth_after:.2f}",
        f"Average Propagation Depth Reduction: {avg_prop_depth_reduction:.2f}",
        f"Average Affected Departments Before: {avg_depts_before:.2f}",
        f"Average Affected Departments After: {avg_depts_after:.2f}",
        f"Average Affected Departments Reduction: {avg_depts_reduction:.2f}",
        f"Average Message Reduction: {avg_msg_reduction:.2f}",
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
        
    lines.extend([
        "",
        "Workflow Family Validation Summary:",
        "-----------------------------------"
    ])
    family_groups = results.groupby("workflow_family")
    for name, group in family_groups:
        family_taus = sorted([int(x) for x in group["Runtime τ_FVS"].unique()])
        family_depts = sorted(group["activated_departments"].unique())
        lines.append(f"Family: {name}")
        lines.append(f"  Observed τ values: {family_taus}")
        lines.append(f"  Unique department routes activated: {len(family_depts)}")

    lines.extend(
        [
            "",
            "Summary by topology:",
            by_topology.to_string(index=False),
            "",
            "Summary by runtime τ value:",
            by_tau.to_string(index=False),
            "",
            "Interpretation:",
            "FVS revocation guarantees removal of directed cycles. It does not, by itself, "
            "guarantee zero downstream reachability from every compromised node.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_experiment() -> tuple[str, Path, pd.DataFrame]:
    """Execute every sampled prompt against a prompt-specific enterprise graph."""
    experiment_id, experiment_dir = create_experiment_directory()
    graphs_dir = experiment_dir / "graphs"
    logs_dir = experiment_dir / "runtime_logs"
    communications_dir = experiment_dir / "communications"
    write_prompts(experiment_dir / "prompts.txt")

    records = []
    for prompt_number, scenario in enumerate(PROMPT_SCENARIOS, 1):
        prompt = scenario["prompt"]
        graph = build_enterprise_runtime_trust_graph(prompt, seed=LAYOUT_SEED)
        route = route_prompt_departments(prompt)
        topology = "workflow_" + "_to_".join(route).lower()
        trace_id = TOPOLOGY_TRACE_IDS["enterprise_departmental_workflow"]
        cycles = list(nx.simple_cycles(graph))
        tau_runtime, fvs_nodes = compute_fvs(graph)
        scc_count = nx.number_strongly_connected_components(graph)
        active_nodes = sorted(graph.nodes())
        compromised = active_nodes[(prompt_number - 1) % len(active_nodes)]
        run_id = f"run_{prompt_number:03d}"
        
        # Linear-time BFS depth compromise propagation
        infected_before, depth_before = propagate_compromise_depth(graph, compromised)
        revoked_graph = graph.copy()
        revoked_graph.remove_nodes_from(fvs_nodes)
        infected_after, depth_after = propagate_compromise_depth(revoked_graph, compromised)
        
        containment_success = len(infected_before) > 0 and len(infected_after) == 0
        steps_before, infection_paths = simulate_communications(
            graph, compromised, scenario
        )
        steps_after, infection_paths_after = simulate_communications(
            revoked_graph, compromised, scenario
        )
        message_count = max(0, len(steps_before) - 1)
        message_count_after = max(0, len(steps_after) - 1)

        # Calculate semantic and comparative metrics:
        internal_messages = sum(
            1 for u, v in graph.edges()
            if graph.nodes[u].get("department") == graph.nodes[v].get("department")
        )
        department_handoffs = sum(
            1 for u, v in graph.edges()
            if graph.nodes[u].get("department") != graph.nodes[v].get("department")
        )
        
        active_agents = [n for n in graph if graph.nodes[n].get("role") == "agent"]
        active_specialists_count = len(active_agents)
        collaboration_depth = active_specialists_count
        review_cycles = len(cycles)
        
        active_depts = set(route)
        average_department_size = graph.number_of_nodes() / len(active_depts) if active_depts else 0.0
        
        max_dept_depth = 0
        for d in active_depts:
            dept_agents = [n for n in graph if graph.nodes[n].get("department") == d and graph.nodes[n].get("role") == "agent"]
            max_dept_depth = max(max_dept_depth, len(dept_agents))
            
        propagation_depth_before = depth_before
        propagation_depth_after = depth_after
        propagation_depth_reduction = depth_before - depth_after
        
        visited_before_nodes = set(infected_before) | ({compromised} if compromised in graph else set())
        visited_after_nodes = set(infected_after) | ({compromised} if compromised in revoked_graph else set())
        
        affected_depts_before = len(set(graph.nodes[n]["department"] for n in visited_before_nodes if n in graph))
        affected_depts_after = len(set(revoked_graph.nodes[n]["department"] for n in visited_after_nodes if n in revoked_graph))
        affected_depts_reduction = affected_depts_before - affected_depts_after
        
        message_reduction = message_count - message_count_after
        
        k_before = len(infected_before)
        k_after = len(infected_after)
        if k_before > 0:
            containment_efficiency = (k_before - k_after) / k_before
        else:
            containment_efficiency = 1.0 if k_after == 0 else 0.0

        communication_stem = f"trace_{trace_id}_prompt_{prompt_number:02d}"
        communication_json = f"communications/{communication_stem}.json"
        communication_markdown_path = f"communications/{communication_stem}.md"
        
        # Prepare trace with narrative details
        communication_trace = {
            "experiment": experiment_id,
            "run_id": run_id,
            "prompt": prompt,
            "topology": topology,
            "runtime_tau": tau_runtime,
            "compromise_source": compromised,
            "fvs_nodes": fvs_nodes,
            "k_before": k_before,
            "k_after": k_after,
            "message_count": message_count,
            "message_count_after_revocation": message_count_after,
            "infected_nodes": infected_before,
            "infected_nodes_after_revocation": infected_after,
            "infection_paths": infection_paths,
            "infection_paths_after_revocation": infection_paths_after,
            "steps": steps_before,
            "post_revocation_steps": steps_after,
            "trace_semantics": (
                "Deterministic simulation; each reachable directed edge transmits "
                "at most once, preventing infinite replay through cycles."
            ),
            # Narrative fields:
            "route": route,
            "active_nodes_list": list(active_nodes),
            "depth_before": depth_before,
            "depth_after": depth_after,
            "affected_depts_before": affected_depts_before,
            "affected_depts_after": affected_depts_after,
            "containment_efficiency": containment_efficiency,
        }
        save_communication_trace(
            experiment_dir / communication_json,
            experiment_dir / communication_markdown_path,
            communication_trace,
        )

        save_runtime_log(logs_dir / f"{run_id}.jsonl", list(graph.edges()))
        title = f"{run_id}: {' → '.join(route)} | compromised={compromised}"
        save_trace_graph(
            graphs_dir / f"{run_id}_trace_graph.png",
            graph,
            compromised,
            infected_before,
            fvs_nodes,
            title,
        )
        save_scc_graph(graphs_dir / f"{run_id}_scc.png", graph, title)

        # Calculate fingerprint metrics:
        graph_hash = compute_graph_hash(graph)
        workflow_family = classify_workflow_family(prompt)
        activated_departments = "|".join(sorted(list(set(route))))
        activated_roles = "|".join(sorted([node for node in graph.nodes() if graph.nodes[node].get("role") == "agent"]))

        records.append(
            {
                "Experiment ID": experiment_id,
                "Run ID": run_id,
                "Prompt": prompt,
                "Topology": topology,
                "Nodes": graph.number_of_nodes(),
                "Edges": graph.number_of_edges(),
                "Cycle Count": len(cycles),
                "SCC Count": scc_count,
                "Runtime τ_FVS": tau_runtime,
                "FVS Nodes": "|".join(fvs_nodes),
                "Compromised Node": compromised,
                "K Before": k_before,
                "K After": k_after,
                "Containment Success": containment_success,
                "Message Count": message_count,
                "Messages After Revocation": message_count_after,
                "Infection Path Count": len(infection_paths),
                "Communications JSON": communication_json,
                "Communications Markdown": communication_markdown_path,
                # New metrics:
                "graph_hash": graph_hash,
                "workflow_family": workflow_family,
                "activated_departments": activated_departments,
                "activated_roles": activated_roles,
                "active_node_count": graph.number_of_nodes(),
                "active_edge_count": graph.number_of_edges(),
                # Expanded containment comparative metrics
                "internal_messages": internal_messages,
                "department_handoffs": department_handoffs,
                "collaboration_depth": collaboration_depth,
                "review_cycles": review_cycles,
                "active_specialists": active_specialists_count,
                "average_department_size": average_department_size,
                "maximum_department_depth": max_dept_depth,
                "propagation_depth_before": propagation_depth_before,
                "propagation_depth_after": propagation_depth_after,
                "propagation_depth_reduction": propagation_depth_reduction,
                "affected_departments_before": affected_depts_before,
                "affected_departments_after": affected_depts_after,
                "affected_departments_reduction": affected_depts_reduction,
                "message_reduction": message_reduction,
                "containment_efficiency": containment_efficiency,
            }
        )

    results = pd.DataFrame.from_records(records)
    results.to_csv(experiment_dir / "results.csv", index=False)
    by_topology, by_tau = build_grouped_summaries(results)
    by_topology.to_csv(experiment_dir / "summary_by_topology.csv", index=False)
    by_tau.to_csv(experiment_dir / "summary_by_tau.csv", index=False)
    save_aggregate_charts(results, graphs_dir)
    write_validation_report(
        results,
        by_topology,
        by_tau,
        experiment_dir / "validation_report.txt",
    )
    write_metadata(experiment_id, experiment_dir / "metadata.json", len(results))
    return experiment_id, experiment_dir, results


def print_summary(experiment_id: str, experiment_dir: Path, results: pd.DataFrame) -> None:
    """Print the experiment location and aggregate observations."""
    observed = set(int(value) for value in results["Runtime τ_FVS"].unique())
    successes = int(results["Containment Success"].sum())
    unique_hashes = results["graph_hash"].nunique()
    print(f"Experiment: {experiment_id}")
    print(f"Output: {experiment_dir}")
    print(f"Runs: {len(results)}")
    print(f"Unique runtime graphs: {unique_hashes}/{len(results)}")
    print(f"Observed runtime τ values: {observed}")
    print(f"Maximum runtime τ: {int(results['Runtime τ_FVS'].max())}")
    print(f"Minimum runtime τ: {int(results['Runtime τ_FVS'].min())}")
    print(f"Containment success rate: {successes}/{len(results)}")
    print(f"Average containment efficiency: {results['containment_efficiency'].mean() * 100:.1f}%")
    print(f"Average K Before: {results['K Before'].mean():.2f}")
    print(f"Average K After: {results['K After'].mean():.2f}")
    print(f"Average message count: {results['Message Count'].mean():.2f}")
    print(f"Total agent-to-agent messages: {int(results['Message Count'].sum())}")
    print(f"Average propagation depth before: {results['propagation_depth_before'].mean():.2f}")
    print(f"Average propagation depth after: {results['propagation_depth_after'].mean():.2f}")
    print(f"Average propagation depth reduction: {results['propagation_depth_reduction'].mean():.2f}")
    print(f"Average affected departments before: {results['affected_departments_before'].mean():.2f}")
    print(f"Average affected departments after: {results['affected_departments_after'].mean():.2f}")
    print(f"Average affected departments reduction: {results['affected_departments_reduction'].mean():.2f}")
    print(f"Average message reduction: {results['message_reduction'].mean():.2f}")
    
    print("\nWorkflow Family Diversity Summary:")
    print("----------------------------------")
    family_groups = results.groupby("workflow_family")
    for name, group in family_groups:
        family_taus = sorted([int(x) for x in group["Runtime τ_FVS"].unique()])
        family_depts = sorted(group["activated_departments"].unique())
        print(f"Family: {name}")
        print(f"  Observed τ values: {family_taus}")
        print(f"  Unique department routes activated: {len(family_depts)}")


if __name__ == "__main__":
    current_id, current_dir, experiment_results = run_experiment()
    print_summary(current_id, current_dir, experiment_results)
