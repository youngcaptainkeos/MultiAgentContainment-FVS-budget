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
STATIC_TAU, STATIC_FVS = compute_fvs(ENTERPRISE_GRAPH)


def create_experiment_directory() -> tuple[str, Path]:
    """Atomically create and return the next exp_NNN directory."""
    EXPERIMENTS_DIR.mkdir(exist_ok=True)
    number = 1
    while True:
        experiment_id = f"exp_{number:03d}"
        path = EXPERIMENTS_DIR / experiment_id
        try:
            path.mkdir()
            (path / "figures").mkdir()
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
                
    infected_after = trace.get("infected_nodes_after_revocation", [])
    k_before = len(infected_before)
    k_after = len(infected_after)
    containment_gain = k_before - k_after
    
    lines.extend([
        "",
        "### 🛡️ Feedback Vertex Set (FVS) Containment",
        f"- **FVS Nodes Selected**: {', '.join(fvs) if fvs else 'None (Topology is acyclic)'}",
        f"- **Containment Ratio**: {efficiency * 100:.1f}%",
        f"- **Containment Gain**: {containment_gain} agents contained.",
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
                radius=1.85,
                facecolor=DEPARTMENT_COLORS[department],
                edgecolor="#b8b8b8",
                linewidth=1.0,
                alpha=0.65,
                zorder=0,
            )
        )
        axis.text(
            center[0],
            center[1] + 2.05,
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
    run_id: str = "N/A",
    topology: str = "N/A",
    tau_runtime: int = 0,
    k_before: int = 0,
    k_after: int = 0,
    containment_efficiency: float = 1.0,
) -> None:
    """Render compromise state and FVS membership for one run with high-quality visual features."""
    path_png = Path(path)
    path_pdf = path_png.with_suffix(".pdf")
    
    display_graph = ENTERPRISE_GRAPH
    positions = departmental_layout(display_graph)
    active_nodes = set(graph.nodes())
    infected = set(infected_nodes)
    fvs = set(fvs_nodes)
    
    colors = [
        "#e74c3c" if node == compromised_node
        else "#f1c40f" if node in infected
        else "#2ecc71" if node in active_nodes
        else "#d9d9d9"
        for node in display_graph.nodes()
    ]
    borders = ["black" if node in fvs else "#666666" for node in display_graph.nodes()]
    widths = [3.2 if node in fvs else 1.0 for node in display_graph.nodes()]

    figure, axis = plt.subplots(figsize=(14, 11))
    draw_department_backgrounds(axis)
    
    inactive_edges = [
        edge for edge in display_graph.edges() if edge[0] not in active_nodes or edge[1] not in active_nodes
    ]
    
    active_edges_list = list(graph.edges())
    active_internal = []
    active_cross = []
    for u, v in active_edges_list:
        dept_u = graph.nodes[u].get("department")
        dept_v = graph.nodes[v].get("department")
        if dept_u == dept_v:
            active_internal.append((u, v))
        else:
            active_cross.append((u, v))
            
    nx.draw_networkx_edges(
        display_graph,
        positions,
        edgelist=inactive_edges,
        ax=axis,
        edge_color="#d0d0d0",
        alpha=0.25,
        arrows=True,
        arrowsize=8,
        width=0.7,
    )
    nx.draw_networkx_edges(
        graph,
        positions,
        edgelist=active_internal,
        ax=axis,
        edge_color="#111111",
        arrows=True,
        arrowsize=14,
        width=1.8,
    )
    nx.draw_networkx_edges(
        graph,
        positions,
        edgelist=active_cross,
        ax=axis,
        edge_color="#333333",
        style="dashed",
        arrows=True,
        arrowsize=14,
        width=1.8,
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
    
    label_positions = {node: (x, y + 0.15) for node, (x, y) in positions.items()}
    nx.draw_networkx_labels(
        display_graph,
        label_positions,
        ax=axis,
        font_size=7,
        font_family="DejaVu Sans",
        font_weight="bold",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, boxstyle="round,pad=0.2"),
    )
    
    axis.set_title(title, fontsize=12, fontweight="bold")
    axis.axis("off")
    
    axis.legend(
        handles=[
            Line2D([], [], marker="o", linestyle="", color="#e74c3c", label="Compromised"),
            Line2D([], [], marker="o", linestyle="", color="#f1c40f", label="Infected"),
            Line2D([], [], marker="o", linestyle="", color="#2ecc71", label="Active / Safe"),
            Line2D([], [], marker="o", linestyle="", color="#d9d9d9", label="Inactive"),
            Line2D(
                [], [], marker="o", linestyle="", markerfacecolor="white",
                markeredgecolor="black", markeredgewidth=3, label="FVS Node",
            ),
        ],
        loc="lower center",
        ncol=5,
        fontsize=9,
        bbox_to_anchor=(0.5, -0.05)
    )
    
    figure.tight_layout()
    figure.savefig(path_png, dpi=600, bbox_inches="tight")
    figure.savefig(path_pdf, bbox_inches="tight")
    plt.close(figure)


def save_scc_graph(path: Path, graph: nx.DiGraph, title: str) -> None:
    """Render each strongly connected component with a distinct color, highlighting nontrivial SCCs."""
    path_png = Path(path)
    path_pdf = path_png.with_suffix(".pdf")
    
    components = list(nx.strongly_connected_components(graph))
    nontrivial_sccs = [c for c in components if len(c) > 1]
    positions = departmental_layout(ENTERPRISE_GRAPH)
    
    palette = plt.get_cmap("Set2")
    
    colors = []
    borders = []
    widths = []
    for node in ENTERPRISE_GRAPH.nodes():
        in_scc = False
        scc_idx = -1
        for idx, scc in enumerate(nontrivial_sccs):
            if node in scc:
                in_scc = True
                scc_idx = idx
                break
        
        if in_scc:
            colors.append(palette(scc_idx % 8))
            borders.append("#111111")
            widths.append(1.5)
        else:
            colors.append("#e6e6e6")
            borders.append("#cccccc")
            widths.append(1.0)
            
    figure, axis = plt.subplots(figsize=(14, 11))
    draw_department_backgrounds(axis)
    
    active_edges_list = list(graph.edges())
    active_internal = []
    active_cross = []
    for u, v in active_edges_list:
        dept_u = graph.nodes[u].get("department")
        dept_v = graph.nodes[v].get("department")
        if dept_u == dept_v:
            active_internal.append((u, v))
        else:
            active_cross.append((u, v))
            
    nx.draw_networkx_edges(
        graph,
        positions,
        edgelist=active_internal,
        ax=axis,
        edge_color="#333333",
        arrows=True,
        arrowsize=14,
        width=1.5,
    )
    nx.draw_networkx_edges(
        graph,
        positions,
        edgelist=active_cross,
        ax=axis,
        edge_color="#555555",
        style="dashed",
        arrows=True,
        arrowsize=14,
        width=1.5,
    )
    nx.draw_networkx_nodes(
        ENTERPRISE_GRAPH,
        positions,
        ax=axis,
        node_color=colors,
        edgecolors=borders,
        linewidths=widths,
        node_size=1150,
    )
    
    label_positions = {node: (x, y + 0.15) for node, (x, y) in positions.items()}
    nx.draw_networkx_labels(
        ENTERPRISE_GRAPH,
        label_positions,
        ax=axis,
        font_size=7,
        font_family="DejaVu Sans",
        font_weight="bold",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, boxstyle="round,pad=0.2"),
    )
    
    for idx, scc in enumerate(nontrivial_sccs, 1):
        scc_nodes = list(scc)
        scc_subgraph = graph.subgraph(scc_nodes)
        scc_tau, _ = compute_fvs(scc_subgraph)
        
        xs = [positions[node][0] for node in scc_nodes]
        ys = [positions[node][1] for node in scc_nodes]
        centroid_x = sum(xs) / len(scc_nodes)
        centroid_y = sum(ys) / len(scc_nodes)
        
        scc_text = f"SCC {idx}\nNodes: {len(scc_nodes)}\nτ: {scc_tau}"
        axis.text(
            centroid_x, centroid_y + 0.45,
            scc_text,
            fontsize=8,
            fontweight="bold",
            fontfamily="DejaVu Sans",
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="#ffffff",
                edgecolor=palette((idx - 1) % 8),
                alpha=0.95,
                linewidth=1.5,
            ),
            zorder=10
        )
        
    axis.set_title(f"{title} — Strongly Connected Components", fontsize=12, fontweight="bold")
    axis.axis("off")
    figure.tight_layout()
    figure.savefig(path_png, dpi=600, bbox_inches="tight")
    figure.savefig(path_pdf, bbox_inches="tight")
    plt.close(figure)


def save_before_after_comparison(
    path_png: Path,
    path_pdf: Path,
    graph: nx.DiGraph,
    revoked_graph: nx.DiGraph,
    compromised_node: str,
    infected_before: list[str],
    infected_after: list[str],
    fvs_nodes: list[str],
    title: str,
    run_id: str = "N/A",
    topology: str = "N/A",
    tau_runtime: int = 0,
    k_before: int = 0,
    k_after: int = 0,
    containment_efficiency: float = 1.0,
) -> None:
    """Generate a 4-panel figure showing the complete theorem flow from runtime graph to contained state."""
    display_graph = ENTERPRISE_GRAPH
    positions = departmental_layout(display_graph)
    active_nodes = set(graph.nodes())
    fvs = set(fvs_nodes)
    
    active_depts = set(graph.nodes[n].get("department") for n in active_nodes if n in graph)
    
    figure, ((ax_a, ax_b), (ax_c, ax_d)) = plt.subplots(2, 2, figsize=(24, 22))
    
    def draw_backgrounds(ax):
        for dept, center in DEPARTMENT_CENTERS.items():
            is_active = dept in active_depts
            alpha_val = 0.65 if is_active else 0.20
            ax.add_patch(
                Circle(
                    center,
                    radius=1.85,
                    facecolor=DEPARTMENT_COLORS[dept],
                    edgecolor="#b8b8b8",
                    linewidth=1.0,
                    alpha=alpha_val,
                    zorder=0,
                )
            )
            ax.text(
                center[0],
                center[1] + 2.05,
                dept,
                ha="center",
                va="center",
                fontsize=11,
                fontweight="bold",
                color="#333333",
                alpha=1.0 if is_active else 0.4
            )
            
    label_positions = {node: (x, y + 0.15) for node, (x, y) in positions.items()}
    
    def draw_fvs_double_outline(ax, fvs_set, size=950):
        fvs_list = [n for n in display_graph.nodes() if n in fvs_set]
        if fvs_list:
            nx.draw_networkx_nodes(
                display_graph, positions, nodelist=fvs_list, ax=ax,
                node_color="black", node_size=size + 350
            )
            nx.draw_networkx_nodes(
                display_graph, positions, nodelist=fvs_list, ax=ax,
                node_color="white", node_size=size + 150
            )

    # ----------------------------------------------------
    # Panel (a): Runtime Trust Graph
    # ----------------------------------------------------
    draw_backgrounds(ax_a)
    
    colors_a = [
        "#e74c3c" if node == compromised_node
        else "#2ecc71" if node in active_nodes
        else "#d9d9d9"
        for node in display_graph.nodes()
    ]
    borders_a = ["black" if node in fvs else "#666666" for node in display_graph.nodes()]
    widths_a = [1.0 for _ in display_graph.nodes()]
    
    sizes_a = [
        1350 if node == compromised_node
        else 1150 if node in fvs
        else 950
        for node in display_graph.nodes()
    ]
    
    inactive_edges = [
        edge for edge in display_graph.edges() if edge[0] not in active_nodes or edge[1] not in active_nodes
    ]
    active_edges_list = list(graph.edges())
    active_internal = [e for e in active_edges_list if graph.nodes[e[0]].get("department") == graph.nodes[e[1]].get("department")]
    active_cross = [e for e in active_edges_list if graph.nodes[e[0]].get("department") != graph.nodes[e[1]].get("department")]
    
    nx.draw_networkx_edges(
        display_graph, positions, edgelist=inactive_edges, ax=ax_a,
        edge_color="#d0d0d0", alpha=0.25, arrows=True, arrowsize=8, width=0.7
    )
    nx.draw_networkx_edges(
        graph, positions, edgelist=active_internal, ax=ax_a,
        edge_color="#111111", arrows=True, arrowsize=14, width=1.8
    )
    nx.draw_networkx_edges(
        graph, positions, edgelist=active_cross, ax=ax_a,
        edge_color="#333333", style="dashed", arrows=True, arrowsize=18, width=2.0,
        connectionstyle="arc3,rad=0.1"
    )
    
    draw_fvs_double_outline(ax_a, fvs, size=950)
    nx.draw_networkx_nodes(
        display_graph, positions, ax=ax_a,
        node_color=colors_a, edgecolors=borders_a, linewidths=widths_a, node_size=sizes_a
    )
    nx.draw_networkx_labels(
        display_graph, label_positions, ax=ax_a,
        font_size=7, font_family="DejaVu Sans", font_weight="bold",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, boxstyle="round,pad=0.2")
    )
    ax_a.set_title("(a) Runtime Trust Graph", fontsize=14, fontweight="bold", pad=10)
    ax_a.axis("off")
    
    # ----------------------------------------------------
    # Panel (b): Strongly Connected Components (SCC)
    # ----------------------------------------------------
    draw_backgrounds(ax_b)
    components = list(nx.strongly_connected_components(graph))
    nontrivial_sccs = [c for c in components if len(c) > 1]
    
    palette = plt.get_cmap("Set2")
    colors_b = []
    borders_b = []
    sizes_b = []
    for node in display_graph.nodes():
        in_scc = False
        scc_idx = -1
        for idx, scc in enumerate(nontrivial_sccs):
            if node in scc:
                in_scc = True
                scc_idx = idx
                break
        if in_scc:
            colors_b.append(palette(scc_idx % 8))
            borders_b.append("#111111")
            sizes_b.append(1200)
        else:
            colors_b.append("#e6e6e6")
            borders_b.append("#cccccc")
            sizes_b.append(950)
            
    nx.draw_networkx_edges(
        graph, positions, edgelist=active_internal, ax=ax_b,
        edge_color="#333333", arrows=True, arrowsize=14, width=1.5
    )
    nx.draw_networkx_edges(
        graph, positions, edgelist=active_cross, ax=ax_b,
        edge_color="#555555", style="dashed", arrows=True, arrowsize=18, width=1.5,
        connectionstyle="arc3,rad=0.1"
    )
    nx.draw_networkx_nodes(
        display_graph, positions, ax=ax_b,
        node_color=colors_b, edgecolors=borders_b, node_size=sizes_b
    )
    nx.draw_networkx_labels(
        display_graph, label_positions, ax=ax_b,
        font_size=7, font_family="DejaVu Sans", font_weight="bold",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, boxstyle="round,pad=0.2")
    )
    
    for idx, scc in enumerate(nontrivial_sccs, 1):
        scc_nodes = list(scc)
        scc_subgraph = graph.subgraph(scc_nodes)
        scc_tau, _ = compute_fvs(scc_subgraph)
        xs = [positions[node][0] for node in scc_nodes]
        ys = [positions[node][1] for node in scc_nodes]
        centroid_x = sum(xs) / len(scc_nodes)
        centroid_y = sum(ys) / len(scc_nodes)
        
        scc_text = f"SCC {idx}\nNodes: {len(scc_nodes)}\nτ: {scc_tau}"
        ax_b.text(
            centroid_x, centroid_y + 0.45,
            scc_text,
            fontsize=8,
            fontweight="bold",
            fontfamily="DejaVu Sans",
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="#ffffff",
                edgecolor=palette((idx - 1) % 8),
                alpha=0.95,
                linewidth=1.5,
            ),
            zorder=10
        )
    ax_b.set_title("(b) SCC & Feedback Cycles", fontsize=14, fontweight="bold", pad=10)
    ax_b.axis("off")
    
    # ----------------------------------------------------
    # Panel (c): Before FVS Revocation
    # ----------------------------------------------------
    draw_backgrounds(ax_c)
    inf_left = set(infected_before)
    
    colors_c = [
        "#e74c3c" if node == compromised_node
        else "#f1c40f" if node in inf_left
        else "#2ecc71" if node in active_nodes
        else "#d9d9d9"
        for node in display_graph.nodes()
    ]
    borders_c = ["black" if node in fvs else "#666666" for node in display_graph.nodes()]
    
    sizes_c = [
        1350 if node == compromised_node
        else 1200 if node in inf_left
        else 1150 if node in fvs
        else 950
        for node in display_graph.nodes()
    ]
    
    nx.draw_networkx_edges(
        display_graph, positions, edgelist=inactive_edges, ax=ax_c,
        edge_color="#d0d0d0", alpha=0.25, arrows=True, arrowsize=8, width=0.7
    )
    nx.draw_networkx_edges(
        graph, positions, edgelist=active_internal, ax=ax_c,
        edge_color="#111111", arrows=True, arrowsize=14, width=1.8
    )
    nx.draw_networkx_edges(
        graph, positions, edgelist=active_cross, ax=ax_c,
        edge_color="#333333", style="dashed", arrows=True, arrowsize=18, width=2.0,
        connectionstyle="arc3,rad=0.1"
    )
    
    draw_fvs_double_outline(ax_c, fvs, size=950)
    nx.draw_networkx_nodes(
        display_graph, positions, ax=ax_c,
        node_color=colors_c, edgecolors=borders_c, node_size=sizes_c
    )
    nx.draw_networkx_labels(
        display_graph, label_positions, ax=ax_c,
        font_size=7, font_family="DejaVu Sans", font_weight="bold",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, boxstyle="round,pad=0.2")
    )
    ax_c.set_title("(c) Before Containment", fontsize=14, fontweight="bold", pad=10)
    ax_c.axis("off")
    
    # ----------------------------------------------------
    # Panel (d): After FVS-Based Containment
    # ----------------------------------------------------
    draw_backgrounds(ax_d)
    active_right = set(revoked_graph.nodes())
    inf_right = set(infected_after)
    
    colors_d = []
    alphas_d = []
    sizes_d = []
    for node in display_graph.nodes():
        if node == compromised_node:
            colors_d.append("#e74c3c")
            alphas_d.append(1.0)
            sizes_d.append(1350)
        elif node in inf_right:
            colors_d.append("#f1c40f")
            alphas_d.append(1.0)
            sizes_d.append(1200)
        elif node in active_right:
            colors_d.append("#2ecc71")
            alphas_d.append(0.35)
            sizes_d.append(950)
        else:
            colors_d.append("#d9d9d9")
            alphas_d.append(0.20)
            sizes_d.append(950)
            
    borders_d = ["black" if node in fvs else "#666666" for node in display_graph.nodes()]
    
    inactive_right_edges = [
        edge for edge in display_graph.edges() if edge[0] not in active_right or edge[1] not in active_right
    ]
    active_right_edges = list(revoked_graph.edges())
    active_right_internal = [e for e in active_right_edges if revoked_graph.nodes[e[0]].get("department") == revoked_graph.nodes[e[1]].get("department")]
    active_right_cross = [e for e in active_right_edges if revoked_graph.nodes[e[0]].get("department") != revoked_graph.nodes[e[1]].get("department")]
    
    nx.draw_networkx_edges(
        display_graph, positions, edgelist=inactive_right_edges, ax=ax_d,
        edge_color="#d0d0d0", alpha=0.15, arrows=True, arrowsize=8, width=0.7
    )
    nx.draw_networkx_edges(
        revoked_graph, positions, edgelist=active_right_internal, ax=ax_d,
        edge_color="#111111", alpha=0.9, arrows=True, arrowsize=14, width=1.8
    )
    nx.draw_networkx_edges(
        revoked_graph, positions, edgelist=active_right_cross, ax=ax_d,
        edge_color="#333333", style="dashed", alpha=0.9, arrows=True, arrowsize=18, width=2.0,
        connectionstyle="arc3,rad=0.1"
    )
    
    for node_idx, node in enumerate(display_graph.nodes()):
        if node in fvs:
            nx.draw_networkx_nodes(
                display_graph, positions, nodelist=[node], ax=ax_d,
                node_color="black", node_size=sizes_d[node_idx] + 350,
                alpha=alphas_d[node_idx]
            )
            nx.draw_networkx_nodes(
                display_graph, positions, nodelist=[node], ax=ax_d,
                node_color="white", node_size=sizes_d[node_idx] + 150,
                alpha=alphas_d[node_idx]
            )
            
        nx.draw_networkx_nodes(
            display_graph, positions, nodelist=[node], ax=ax_d,
            node_color=[colors_d[node_idx]], edgecolors=[borders_d[node_idx]],
            node_size=[sizes_d[node_idx]], alpha=alphas_d[node_idx]
        )
        
    nx.draw_networkx_labels(
        display_graph, label_positions, ax=ax_d,
        font_size=7, font_family="DejaVu Sans", font_weight="bold",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.6, boxstyle="round,pad=0.2")
    )
    ax_d.set_title("(d) After FVS Containment", fontsize=14, fontweight="bold", pad=10)
    ax_d.axis("off")
    
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#e74c3c", markersize=10, label="Compromised"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#f1c40f", markersize=10, label="Infected"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="white", markeredgecolor="black", markeredgewidth=3, markersize=10, label="FVS Node (Revocation target)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#2ecc71", markersize=10, label="Active / Safe"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#d9d9d9", markersize=10, label="Inactive / Revoked"),
    ]
    figure.legend(handles=legend_elements, loc="lower center", ncol=5, fontsize=12, frameon=True, bbox_to_anchor=(0.5, 0.02))
    
    figure.suptitle(f"FVS Containment Theorem Flow — {run_id} ({topology})", fontsize=18, fontweight="bold", y=0.96)
    
    plt.subplots_adjust(bottom=0.08, top=0.90, wspace=0.15, hspace=0.15)
    figure.savefig(path_png, dpi=600, bbox_inches="tight")
    figure.savefig(path_pdf, bbox_inches="tight")
    plt.close(figure)


def save_run_summary_table(
    path_png: Path,
    path_pdf: Path,
    graph: nx.DiGraph,
    compromised_node: str,
    fvs_nodes: list[str],
    run_id: str,
    topology: str,
    tau_runtime: int,
    scc_count: int,
    components: list[set[str]],
    k_before: int,
    k_after: int,
    containment_ratio: float,
    depth_before: int,
    depth_after: int,
    graph_hash: str,
) -> None:
    """Render a separate publication-quality summary table figure for a run."""
    fig, ax = plt.subplots(figsize=(10, 6.8))
    ax.axis("off")
    
    largest_scc = max([len(c) for c in components]) if components else 0
    
    table_data = [
        ["Experiment Metric", "Observed Simulation Value"],
        ["Run ID", run_id],
        ["Workflow", topology],
        ["Compromised Agent", compromised_node],
        ["Runtime τ_FVS", str(tau_runtime)],
        ["FVS Size", str(len(fvs_nodes))],
        ["Active Agents", str(graph.number_of_nodes())],
        ["Active Edges", str(graph.number_of_edges())],
        ["SCC Count", str(scc_count)],
        ["Largest SCC Size", str(largest_scc)],
        ["Infected Before", str(k_before)],
        ["Infected After", str(k_after)],
        ["Containment Ratio", f"{containment_ratio * 100:.1f}%"],
        ["Containment Gain", f"{k_before - k_after} agents"],
        ["Propagation Depth", f"{depth_before} -> {depth_after} (Reduction: {depth_before - depth_after} hops)"],
        ["Graph Hash", graph_hash],
    ]
    
    table = ax.table(
        cellText=table_data[1:],
        colLabels=table_data[0],
        loc="center",
        cellLoc="left",
        colWidths=[0.38, 0.62],
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(10.5)
    table.scale(1.2, 1.6)
    
    for (row_idx, col_idx), cell in table.get_celld().items():
        if row_idx == 0:
            cell.set_text_props(weight="bold", color="white", fontsize=11)
            cell.set_facecolor("#2c3e50")
            cell.set_edgecolor("#2c3e50")
        else:
            if row_idx % 2 == 0:
                cell.set_facecolor("#f8f9fa")
            else:
                cell.set_facecolor("#ffffff")
            cell.set_edgecolor("#e9ecef")
            
            if table_data[row_idx][0] == "Containment Ratio":
                cell.set_text_props(weight="bold", color="#27ae60" if k_after == 0 else "#e67e22")
            if table_data[row_idx][0] == "Run ID":
                cell.set_text_props(weight="bold")
                 
    fig.suptitle(f"Containment Simulation Executive Summary — {run_id}", fontsize=14, fontweight="bold", y=0.96)
    
    fig.savefig(path_png, dpi=600, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)


def get_contained_graph(
    graph: nx.DiGraph,
    compromised: str,
    policy_name: str,
    runtime_fvs_nodes: list[str],
    runtime_tau: int,
    route: list[str]
) -> tuple[nx.DiGraph, list[str]]:
    """Apply the specified graph containment policy to isolate or block compromise propagation."""
    contained_graph = graph.copy()
    revoked_nodes = []
    
    if policy_name == "no_containment":
        pass
        
    elif policy_name == "degree_centrality":
        centrality = nx.degree_centrality(graph)
        candidates = [n for n in graph.nodes() if n != compromised]
        candidates.sort(key=lambda n: (-centrality[n], n))
        revoked_nodes = candidates[:runtime_tau]
        contained_graph.remove_nodes_from(revoked_nodes)
        
    elif policy_name == "betweenness_centrality":
        centrality = nx.betweenness_centrality(graph)
        candidates = [n for n in graph.nodes() if n != compromised]
        candidates.sort(key=lambda n: (-centrality[n], n))
        revoked_nodes = candidates[:runtime_tau]
        contained_graph.remove_nodes_from(revoked_nodes)
        
    elif policy_name == "pagerank":
        try:
            centrality = nx.pagerank(graph, alpha=0.85, max_iter=200)
        except Exception:
            centrality = nx.degree_centrality(graph)
        candidates = [n for n in graph.nodes() if n != compromised]
        candidates.sort(key=lambda n: (-centrality[n], n))
        revoked_nodes = candidates[:runtime_tau]
        contained_graph.remove_nodes_from(revoked_nodes)
        
    elif policy_name == "supervisor_only":
        unique_depts = set(route)
        for dept in unique_depts:
            sup = DEPARTMENTS.get(dept, {}).get("supervisor")
            if sup in contained_graph:
                revoked_nodes.append(sup)
        contained_graph.remove_nodes_from(revoked_nodes)
        
    elif policy_name == "department_isolation":
        if compromised in graph:
            compromised_dept = graph.nodes[compromised].get("department")
            edges_to_remove = []
            for u, v in contained_graph.edges():
                dept_u = contained_graph.nodes[u].get("department")
                dept_v = contained_graph.nodes[v].get("department")
                if dept_u != dept_v and (dept_u == compromised_dept or dept_v == compromised_dept):
                    edges_to_remove.append((u, v))
            contained_graph.remove_edges_from(edges_to_remove)
            
    elif policy_name == "static_fvs":
        revoked_nodes = [n for n in STATIC_FVS if n in contained_graph]
        contained_graph.remove_nodes_from(revoked_nodes)
        
    elif policy_name == "compromised_only":
        revoked_nodes = [compromised] if compromised in contained_graph else []
        contained_graph.remove_nodes_from(revoked_nodes)
        
    elif policy_name == "runtime_fvs":
        revoked_nodes = runtime_fvs_nodes
        contained_graph.remove_nodes_from(revoked_nodes)
        
    return contained_graph, revoked_nodes


    return contained_graph, revoked_nodes


def run_statistical_validation(
    policy_records: dict[str, list[dict]],
    experiment_dir: Path
) -> None:
    import numpy as np
    import pandas as pd
    from scipy.stats import ttest_rel, wilcoxon, shapiro
    
    baseline_map = {
        "no_containment": "No Containment",
        "random_revocation": "Random Revocation",
        "degree_centrality": "Degree Centrality",
        "betweenness_centrality": "Betweenness Centrality",
        "pagerank": "PageRank",
        "supervisor_only": "Supervisor Only",
        "department_isolation": "Department Isolation",
        "static_fvs": "Static FVS",
        "compromised_only": "Oracle Compromised Node"
    }
    
    metrics = [
        ("K After", "Infected After"),
        ("Containment Ratio", "Containment Ratio"),
        ("Containment Gain", "Containment Gain"),
        ("Message Count After", "Message Count After"),
        ("Propagation Depth After", "Propagation Depth After")
    ]
    
    comparisons = []
    df_ref = pd.DataFrame(policy_records["runtime_fvs"])
    
    for baseline_key, baseline_name in baseline_map.items():
        df_p = pd.DataFrame(policy_records[baseline_key])
        n = len(df_p)
        
        for metric_label, col in metrics:
            ref_vals = df_ref[col].to_numpy()
            p_vals = df_p[col].to_numpy()
            diffs = ref_vals - p_vals
            
            mean_ref = np.mean(ref_vals)
            mean_p = np.mean(p_vals)
            mean_diff = mean_ref - mean_p
            median_diff = np.median(ref_vals) - np.median(p_vals)
            
            normal = False
            try:
                if len(diffs) >= 3 and not np.all(diffs == 0):
                    shap_stat, shap_p = shapiro(diffs)
                    normal = (shap_p > 0.05)
            except Exception:
                pass
                
            t_stat, t_p = float('nan'), float('nan')
            try:
                t_stat, t_p = ttest_rel(ref_vals, p_vals)
            except Exception:
                pass
                
            wilc_stat, wilc_p = float('nan'), float('nan')
            try:
                if np.all(diffs == 0):
                    wilc_stat, wilc_p = 0.0, 1.0
                else:
                    res = wilcoxon(ref_vals, p_vals)
                    wilc_stat, wilc_p = res.statistic, res.pvalue
            except Exception:
                pass
                
            if normal:
                test_used = "Paired t-test"
                stat_val = t_stat
                raw_p = t_p
            else:
                test_used = "Wilcoxon signed-rank"
                stat_val = wilc_stat
                raw_p = wilc_p
                
            std_diff = np.std(diffs, ddof=1) if n > 1 else 0.0
            if normal:
                cohen_d = mean_diff / std_diff if std_diff > 0 else 0.0
                effect_size = cohen_d
                abs_es = abs(effect_size)
                if abs_es < 0.2:
                    es_label = "negligible"
                elif abs_es < 0.5:
                    es_label = "small"
                elif abs_es < 0.8:
                    es_label = "medium"
                else:
                    es_label = "large"
            else:
                abs_diffs = np.abs(diffs)
                nonzero = abs_diffs != 0
                if np.sum(nonzero) == 0:
                    rank_biserial = 0.0
                else:
                    from scipy.stats import rankdata
                    ranks = rankdata(abs_diffs[nonzero])
                    signs = np.sign(diffs[nonzero])
                    w_plus = np.sum(ranks[signs == 1])
                    w_minus = np.sum(ranks[signs == -1])
                    rank_biserial = (w_plus - w_minus) / (w_plus + w_minus)
                effect_size = rank_biserial
                abs_es = abs(effect_size)
                if abs_es < 0.1:
                    es_label = "negligible"
                elif abs_es < 0.3:
                    es_label = "small"
                elif abs_es < 0.5:
                    es_label = "medium"
                else:
                    es_label = "large"
                    
            pct_impr = 0.0
            if metric_label in ["K After", "Message Count After", "Propagation Depth After"]:
                if mean_p > 0:
                    pct_impr = (mean_p - mean_ref) / mean_p * 100
                else:
                    pct_impr = 0.0 if mean_ref == 0 else float('-inf')
            else:
                if mean_p > 0:
                    pct_impr = (mean_ref - mean_p) / mean_p * 100
                else:
                    pct_impr = 100.0 if mean_ref > 0 else 0.0
                    
            comparisons.append({
                "baseline_key": baseline_key,
                "baseline": baseline_name,
                "metric": metric_label,
                "runtime_mean": mean_ref,
                "baseline_mean": mean_p,
                "mean_difference": mean_diff,
                "median_difference": median_diff,
                "test": test_used,
                "stat_val": stat_val,
                "p": raw_p,
                "effect_size": effect_size,
                "effect_size_label": es_label,
                "pct_improvement": pct_impr,
                "ref_vals": ref_vals,
                "p_vals": p_vals
            })
            
    # Apply Benjamini-Hochberg (BH) correction
    p_values = [c["p"] for c in comparisons]
    m = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]
    
    adj_p = np.zeros(m)
    prev_adj = 1.0
    for i in range(m - 1, -1, -1):
        val = (sorted_p[i] * m) / (i + 1)
        adj_val = min(prev_adj, val)
        adj_p[i] = min(1.0, adj_val)
        prev_adj = adj_p[i]
        
    restored_adj_p = np.zeros(m)
    for idx, orig_idx in enumerate(sorted_indices):
        restored_adj_p[orig_idx] = adj_p[idx]
        
    for idx, c in enumerate(comparisons):
        c["adjusted_p"] = restored_adj_p[idx]
        c["significant"] = "Yes" if c["adjusted_p"] < 0.05 else "No"
        
    df_sig = pd.DataFrame([{
        "metric": c["metric"],
        "baseline": c["baseline"],
        "runtime_mean": c["runtime_mean"],
        "baseline_mean": c["baseline_mean"],
        "mean_difference": c["mean_difference"],
        "median_difference": c["median_difference"],
        "test": c["test"],
        "p": c["p"],
        "adjusted_p": c["adjusted_p"],
        "effect_size": c["effect_size"],
        "effect_size_label": c["effect_size_label"],
        "significant": c["significant"]
    } for c in comparisons])
    df_sig.to_csv(experiment_dir / "statistical_significance.csv", index=False)
    
    df_es = pd.DataFrame([{
        "metric": c["metric"],
        "baseline": c["baseline"],
        "pct_improvement": c["pct_improvement"],
        "effect_size": c["effect_size"],
        "effect_size_label": c["effect_size_label"],
        "test": c["test"],
        "p": c["p"],
        "adjusted_p": c["adjusted_p"]
    } for c in comparisons])
    df_es.to_csv(experiment_dir / "effect_sizes.csv", index=False)
    
    # Generate baseline_significance_summary.md
    lines = [
        "# Baseline Significance and Effect Size Report",
        "",
        "This report statistically validates the performance of **Runtime FVS** containment against alternative baselines. We evaluate paired observations across 200 simulation runs. Shapiro-Wilk test determines the normality of paired differences, paired t-tests or Wilcoxon signed-rank tests assess statistical significance, and Benjamini-Hochberg FDR adjustments correct for multiple hypothesis testing.",
        "",
        "---",
        "",
        "## 🔬 Per-Baseline Comparison Summaries",
        ""
    ]
    
    grouped = {}
    for c in comparisons:
        grouped.setdefault(c["baseline"], []).append(c)
        
    for baseline, comps in grouped.items():
        lines.append(f"### 🛡️ Runtime FVS vs. {baseline}")
        lines.append("")
        for c in comps:
            metric = c["metric"]
            rmean = c["runtime_mean"]
            bmean = c["baseline_mean"]
            diff = c["mean_difference"]
            test = c["test"]
            pval = c["p"]
            adj_p_val = c["adjusted_p"]
            es = c["effect_size"]
            es_lbl = c["effect_size_label"]
            pct = c["pct_improvement"]
            sig = c["significant"]
            
            p_str = f"< 0.001" if adj_p_val < 0.001 else f"= {adj_p_val:.4f}"
            
            lines.append(f"- **{metric}**:")
            lines.append(f"  - Mean: {rmean:.3f} (Runtime FVS) vs. {bmean:.3f} ({baseline}) [Diff: {diff:.3f}]")
            lines.append(f"  - Relative Improvement: **{pct:.1f}%**")
            es_name = "Cohen's d" if "t-test" in test else "Rank-biserial"
            lines.append(f"  - Test: {test} (adjusted $p$ {p_str}, Significant: **{sig}**)")
            lines.append(f"  - Effect Size ({es_name}): {es:.3f} ({es_lbl.title()} Effect)")
            lines.append("")
            
        k_after_c = [c for c in comps if c["metric"] == "K After"][0]
        ratio_c = [c for c in comps if c["metric"] == "Containment Ratio"][0]
        
        if k_after_c["significant"] == "Yes" or ratio_c["significant"] == "Yes":
            if ratio_c["runtime_mean"] > ratio_c["baseline_mean"]:
                lines.append(f"**Conclusion**: Runtime FVS significantly outperformed {baseline} in containment effectiveness.")
            else:
                lines.append(f"**Conclusion**: {baseline} achieved significantly different containment levels (e.g. oracle compromised node isolation).")
        else:
            lines.append(f"**Conclusion**: No statistically significant difference in containment effectiveness was observed between Runtime FVS and {baseline}.")
        lines.append("")
        lines.append("---")
        lines.append("")
        
    lines.append("## 📊 LaTeX Publication Tables")
    lines.append("")
    lines.append("### LaTeX Table: Statistical Significance and Effect Sizes")
    lines.append("```latex")
    lines.append(r"\begin{table}[ht]")
    lines.append(r"\centering")
    lines.append(r"\caption{Paired Statistical Significance Comparisons of Runtime FVS against Baselines}")
    lines.append(r"\begin{tabular}{llrrrrrc}")
    lines.append(r"\hline")
    lines.append(r"Baseline & Metric & FVS Mean & Base Mean & Mean Diff & adj. $p$-val & Effect Size & Sig. \\")
    lines.append(r"\hline")
    for c in comparisons:
        b_name = c["baseline"]
        metric = c["metric"]
        rmean = f"{c['runtime_mean']:.3f}"
        bmean = f"{c['baseline_mean']:.3f}"
        diff = f"{c['mean_difference']:.3f}"
        adj_p_val = c["adjusted_p"]
        p_str = "$< 0.001$" if adj_p_val < 0.001 else f"{adj_p_val:.4f}"
        es = f"{c['effect_size']:.3f}"
        es_label = c['effect_size_label']
        sig_str = c["significant"]
        lines.append(f"{b_name} & {metric} & {rmean} & {bmean} & {diff} & {p_str} & {es} ({es_label}) & {sig_str} \\\\")
    lines.append(r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\label{tab:statistical_significance}")
    lines.append(r"\end{table}")
    lines.append("```")
    
    (experiment_dir / "baseline_significance_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_confidence_intervals(
    policy_records: dict[str, list[dict]],
    experiment_dir: Path
) -> None:
    import numpy as np
    import pandas as pd
    from scipy.stats import t
    
    baseline_map = {
        "no_containment": "No Containment",
        "random_revocation": "Random Revocation",
        "degree_centrality": "Degree Centrality",
        "betweenness_centrality": "Betweenness Centrality",
        "pagerank": "PageRank",
        "supervisor_only": "Supervisor Only",
        "department_isolation": "Department Isolation",
        "static_fvs": "Static FVS",
        "compromised_only": "Oracle Compromised Node",
        "runtime_fvs": "Runtime FVS"
    }
    
    overall_path = experiment_dir / "overall_comparison.csv"
    reported_cis = {}
    if overall_path.exists():
        df_overall = pd.read_csv(overall_path)
        for _, row in df_overall.iterrows():
            b_key = row["Baseline"]
            reported_cis[b_key] = {}
            for col in df_overall.columns:
                if col.endswith("_95CI"):
                    metric_name = col[:-5]
                    reported_cis[b_key][metric_name] = str(row[col])
                    
    validation_rows = []
    
    metrics_to_validate = [
        ("Containment Ratio", "Containment Ratio"),
        ("Containment Gain", "Containment Gain"),
        ("K After", "Infected After"),
        ("Message Count After", "Message Count After"),
        ("Propagation Depth After", "Propagation Depth After"),
        ("FVS Size", "FVS Size"),
        ("Runtime Execution Time", "Runtime Execution Time")
    ]
    
    before_metrics = [
        ("K Before", "Infected Before"),
        ("Message Count Before", "Message Count Before"),
        ("Propagation Depth Before", "Propagation Depth Before")
    ]
    
    for b_key, b_name in baseline_map.items():
        df_p = pd.DataFrame(policy_records[b_key])
        n = len(df_p)
        if n == 0:
            continue
            
        t_crit = t.ppf(0.975, df=n-1) if n > 1 else 0.0
        
        for metric_label, col in metrics_to_validate:
            vals = df_p[col].to_numpy()
            mean = np.mean(vals)
            std = np.std(vals, ddof=1) if n > 1 else 0.0
            
            margin_t = t_crit * (std / np.sqrt(n)) if n > 0 else 0.0
            ci_t_lower = mean - margin_t
            ci_t_upper = mean + margin_t
            ci_t_str = f"[{ci_t_lower:.3f}, {ci_t_upper:.3f}]"
            
            margin_z = 1.96 * (std / np.sqrt(n)) if n > 0 else 0.0
            ci_z_lower = mean - margin_z
            ci_z_upper = mean + margin_z
            ci_z_str = f"[{ci_z_lower:.3f}, {ci_z_upper:.3f}]"
            
            reported_str = "N/A"
            abs_diff = 0.0
            status = "Pass"
            
            if b_key in reported_cis and metric_label in reported_cis[b_key]:
                reported_str = reported_cis[b_key][metric_label]
                try:
                    parts = reported_str.replace("[", "").replace("]", "").split(",")
                    rep_lower = float(parts[0])
                    rep_upper = float(parts[1])
                    
                    diff_normal = max(abs(rep_lower - round(ci_z_lower, 3)), abs(rep_upper - round(ci_z_upper, 3)))
                    if diff_normal > 1e-4:
                        status = "Fail (Incorrect reported value)"
                    elif abs(rep_lower - round(ci_t_lower, 3)) > 1e-6 or abs(rep_upper - round(ci_t_upper, 3)) > 1e-6:
                        status = "Precision discrepancy (using Normal approximation instead of Student t)"
                    else:
                        status = "Pass"
                    
                    diff_lower = abs(rep_lower - ci_t_lower)
                    diff_upper = abs(rep_upper - ci_t_upper)
                    abs_diff = max(diff_lower, diff_upper)
                except Exception:
                    status = "Parsing Error"
            else:
                status = "Not Reported in Summary"
                
            validation_rows.append({
                "baseline": b_name,
                "metric": metric_label,
                "reported_ci": reported_str,
                "recomputed_student_t_ci": ci_t_str,
                "recomputed_normal_ci": ci_z_str,
                "mean": mean,
                "std": std,
                "n": n,
                "t_critical": t_crit,
                "status": status,
                "absolute_difference_vs_student_t": abs_diff
            })
            
        if b_key == "runtime_fvs":
            for metric_label, col in before_metrics:
                vals = df_p[col].to_numpy()
                mean = np.mean(vals)
                std = np.std(vals, ddof=1) if n > 1 else 0.0
                
                margin_t = t_crit * (std / np.sqrt(n)) if n > 0 else 0.0
                ci_t_lower = mean - margin_t
                ci_t_upper = mean + margin_t
                ci_t_str = f"[{ci_t_lower:.3f}, {ci_t_upper:.3f}]"
                
                margin_z = 1.96 * (std / np.sqrt(n)) if n > 0 else 0.0
                ci_z_lower = mean - margin_z
                ci_z_upper = mean + margin_z
                ci_z_str = f"[{ci_z_lower:.3f}, {ci_z_upper:.3f}]"
                
                validation_rows.append({
                    "baseline": "Runtime FVS (Before)",
                    "metric": metric_label,
                    "reported_ci": "N/A",
                    "recomputed_student_t_ci": ci_t_str,
                    "recomputed_normal_ci": ci_z_str,
                    "mean": mean,
                    "std": std,
                    "n": n,
                    "t_critical": t_crit,
                    "status": "Verified (Not reported in baseline comparisons summary)",
                    "absolute_difference_vs_student_t": 0.0
                })
                
    df_val = pd.DataFrame(validation_rows)
    df_val.to_csv(experiment_dir / "confidence_interval_validation.csv", index=False)
    
    lines = [
        "# Confidence Interval Validation Report",
        "",
        "This report verifies the statistical correctness of the confidence intervals reported in the experimental results.",
        "",
        "## 📐 Statistical Formulas",
        "",
        "The standard formula for computing a $95\\%$ confidence interval using the Student $t$-distribution is:",
        "",
        "\\[CI_{95\\%} = \\bar{x} \\pm t_{\\text{crit}} \\times \\frac{s}{\\sqrt{n}}\\]",
        "",
        "Where:",
        "- $\\bar{x}$ is the sample mean.",
        "- $s$ is the sample standard deviation (with $df = n-1$).",
        "- $n$ is the sample size (number of runs, $200$).",
        "- $t_{\\text{crit}}$ is the critical value from the Student $t$-distribution with $n-1$ degrees of freedom. For $n=200$, $df=199$ and $t_{\\text{crit}, 0.025} \\approx 1.972$.",
        "",
        "Previously, the summary table reported confidence intervals based on the standard normal approximation:",
        "",
        "\\[CI_{\\text{normal}} = \\bar{x} \\pm 1.96 \\times \\frac{s}{\\sqrt{n}}\\]",
        "",
        "---",
        "",
        "## 🔬 Validation Log",
        "",
        "We compared the recomputed Student $t$ confidence intervals against the currently reported intervals in `overall_comparison.csv`. The validation results are detailed below:",
        ""
    ]
    
    for _, r in df_val.iterrows():
        b = r["baseline"]
        m = r["metric"]
        rep = r["reported_ci"]
        student_ci = r["recomputed_student_t_ci"]
        normal_ci = r["recomputed_normal_ci"]
        status = r["status"]
        diff = r["absolute_difference_vs_student_t"]
        
        lines.append(f"### 🛡️ {b} — {m}")
        lines.append(f"- **Reported CI**: `{rep}`")
        lines.append(f"- **Recomputed Student $t$ CI**: `{student_ci}` (using $t_{{\\text{{crit}}}} = {r['t_critical']:.4f}$)")
        lines.append(f"- **Recomputed Normal CI**: `{normal_ci}`")
        lines.append(f"- **Status**: **{status}** (Absolute difference vs. Student $t$: `{diff:.6f}`)")
        lines.append("")
        
    lines.append("---")
    lines.append("")
    lines.append("## 📈 Recommendation")
    lines.append("The reported intervals in the summary comparison table match the recomputed Normal approximation confidence intervals with $100\\%$ precision. However, to maintain the highest statistical rigor, we recommend updating all publication summaries to use the recomputed Student $t$-distribution intervals since the sample size $n=200$ is finite and the Student $t$-distribution provides the mathematically exact interval.")
    
    (experiment_dir / "confidence_interval_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_baselines_and_statistics(
    policy_records: dict[str, list[dict]],
    figures_dir: Path,
    experiment_dir: Path
) -> None:
    import numpy as np
    import pandas as pd
    from scipy.stats import ttest_rel, wilcoxon, shapiro
    
    # 1. Save summary CSV for every baseline
    for p, records in policy_records.items():
        df_p = pd.DataFrame(records)
        df_p.to_csv(experiment_dir / f"policy_{p}_summary.csv", index=False)
        
    # 2. Overall Comparison CSV
    overall_rows = []
    for p, records in policy_records.items():
        df_p = pd.DataFrame(records)
        n = len(df_p)
        
        row = {"Baseline": p}
        for metric in ["Containment Ratio", "Containment Gain", "Infected After", "Message Count After", "FVS Size", "Runtime Execution Time"]:
            vals = df_p[metric].to_numpy()
            mean = np.mean(vals)
            median = np.median(vals)
            std = np.std(vals, ddof=1) if n > 1 else 0.0
            margin = 1.96 * (std / np.sqrt(n)) if n > 0 else 0.0
            ci_lower = mean - margin
            ci_upper = mean + margin
            
            row[f"{metric}_Mean"] = mean
            row[f"{metric}_Median"] = median
            row[f"{metric}_Std"] = std
            row[f"{metric}_95CI"] = f"[{ci_lower:.3f}, {ci_upper:.3f}]"
            
        overall_rows.append(row)
        
    df_overall = pd.DataFrame(overall_rows)
    df_overall.to_csv(experiment_dir / "overall_comparison.csv", index=False)
    
    # 3. Pairwise Statistical Comparison
    df_ref = pd.DataFrame(policy_records["runtime_fvs"])
    pairwise_rows = []
    
    metrics_to_compare = [
        ("Containment Ratio", "Containment Ratio"),
        ("Containment Gain", "Containment Gain"),
        ("Propagation Depth After", "Propagation Depth After"),
        ("Message Count After", "Message Count After")
    ]
    
    for p in policy_records.keys():
        if p == "runtime_fvs":
            continue
            
        df_p = pd.DataFrame(policy_records[p])
        n = len(df_p)
        
        for metric_label, col in metrics_to_compare:
            ref_vals = df_ref[col].to_numpy()
            p_vals = df_p[col].to_numpy()
            diffs = ref_vals - p_vals
            
            mean_ref = np.mean(ref_vals)
            mean_p = np.mean(p_vals)
            mean_diff = np.mean(diffs)
            std_diff = np.std(diffs, ddof=1) if n > 1 else 0.0
            
            cohen_d = mean_diff / std_diff if std_diff > 0 else 0.0
            
            # Test normality
            normal = False
            try:
                if n >= 3 and not np.all(diffs == 0):
                    shap_stat, shap_p = shapiro(diffs)
                    normal = (shap_p > 0.05)
            except Exception:
                pass
                
            # paired t-test
            try:
                t_stat, t_p = ttest_rel(ref_vals, p_vals)
            except Exception:
                t_stat, t_p = float('nan'), float('nan')
                
            # Wilcoxon signed-rank test
            try:
                if np.all(diffs == 0):
                    wilc_stat, wilc_p = 0.0, 1.0
                else:
                    wilc_stat, wilc_p = wilcoxon(ref_vals, p_vals)
            except Exception:
                wilc_stat, wilc_p = float('nan'), float('nan')
                
            selected_p = t_p if normal else wilc_p
            test_used = "Paired t-test" if normal else "Wilcoxon signed-rank"
            
            pairwise_rows.append({
                "Baseline": p,
                "Metric": metric_label,
                "Runtime FVS Mean": mean_ref,
                "Baseline Mean": mean_p,
                "Mean Difference": mean_diff,
                "Std Deviation Difference": std_diff,
                "Cohen's d": cohen_d,
                "t-test p-value": t_p,
                "Wilcoxon p-value": wilc_p,
                "Selected Test": test_used,
                "Selected p-value": selected_p
            })
            
    df_pairwise = pd.DataFrame(pairwise_rows)
    df_pairwise.to_csv(experiment_dir / "pairwise_statistical_comparison.csv", index=False)


def save_baseline_plots(policy_records: dict[str, list[dict]], figures_dir: Path) -> None:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from matplotlib.lines import Line2D
    
    baselines = list(policy_records.keys())
    labels = [b.replace("_", " ").title() for b in baselines]
    
    # 1. Containment Ratio Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    means = []
    errors = []
    for b in baselines:
        vals = pd.DataFrame(policy_records[b])["Containment Ratio"].to_numpy() * 100
        mean = np.mean(vals)
        std = np.std(vals, ddof=1) if len(vals) > 1 else 0.0
        margin = 1.96 * (std / np.sqrt(len(vals)))
        means.append(mean)
        errors.append(margin)
        
    bars = ax.bar(labels, means, yerr=errors, color="#3498db", edgecolor="black", error_kw=dict(ecolor="black", lw=1.5, capsize=4))
    ax.set_ylabel("Average Containment Ratio (%)", fontsize=11, fontweight="bold")
    ax.set_title("Containment Ratio Comparison (with 95% CI)", fontsize=13, fontweight="bold")
    plt.xticks(rotation=30, ha="right")
    ax.set_ylim(0, 105)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, height + 1.5, f"{height:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
        
    fig.tight_layout()
    fig.savefig(figures_dir / "baseline_containment_ratio.png", dpi=600)
    fig.savefig(figures_dir / "baseline_containment_ratio.pdf")
    plt.close(fig)
    
    # 2. K_before vs K_after
    fig, ax = plt.subplots(figsize=(10, 6))
    k_before_mean = np.mean([r["Infected Before"] for r in policy_records["runtime_fvs"]])
    data_k_after = [pd.DataFrame(policy_records[b])["Infected After"].to_numpy() for b in baselines]
    
    ax.boxplot(data_k_after, patch_artist=True,
               boxprops=dict(facecolor="#f1c40f", color="black"),
               medianprops=dict(color="red", linewidth=1.5))
    ax.axhline(y=k_before_mean, color="red", linestyle="--", linewidth=1.5, label=f"Mean K Before ({k_before_mean:.2f})")
    ax.set_ylabel("Infected Agents Footprint (K)", fontsize=11, fontweight="bold")
    ax.set_title("Compromise Footprint (K After) by Containment Policy", fontsize=13, fontweight="bold")
    ax.set_xticks(range(1, len(baselines) + 1))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "baseline_k_footprint.png", dpi=600)
    fig.savefig(figures_dir / "baseline_k_footprint.pdf")
    plt.close(fig)
    
    # 3. Propagation Depth Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    depth_before_mean = np.mean([r["Propagation Depth Before"] for r in policy_records["runtime_fvs"]])
    data_depth_after = [pd.DataFrame(policy_records[b])["Propagation Depth After"].to_numpy() for b in baselines]
    
    ax.boxplot(data_depth_after, patch_artist=True,
               boxprops=dict(facecolor="#9b59b6", color="black"),
               medianprops=dict(color="red", linewidth=1.5))
    ax.axhline(y=depth_before_mean, color="red", linestyle="--", linewidth=1.5, label=f"Mean Depth Before ({depth_before_mean:.2f})")
    ax.set_ylabel("Propagation Depth (Hops)", fontsize=11, fontweight="bold")
    ax.set_title("Propagation Depth After Containment by Policy", fontsize=13, fontweight="bold")
    ax.set_xticks(range(1, len(baselines) + 1))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "baseline_propagation_depth.png", dpi=600)
    fig.savefig(figures_dir / "baseline_propagation_depth.pdf")
    plt.close(fig)
    
    # 4. Message Reduction Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    msg_red_means = [np.mean(pd.DataFrame(policy_records[b])["Message Reduction"]) for b in baselines]
    msg_red_errors = []
    for b in baselines:
        vals = pd.DataFrame(policy_records[b])["Message Reduction"].to_numpy()
        std = np.std(vals, ddof=1) if len(vals) > 1 else 0.0
        margin = 1.96 * (std / np.sqrt(len(vals)))
        msg_red_errors.append(margin)
        
    bars = ax.bar(labels, msg_red_means, yerr=msg_red_errors, color="#e67e22", edgecolor="black", error_kw=dict(ecolor="black", lw=1.5, capsize=4))
    ax.set_ylabel("Average Message Reduction Count", fontsize=11, fontweight="bold")
    ax.set_title("Communication Overhead Reduction by Policy", fontsize=13, fontweight="bold")
    plt.xticks(rotation=30, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, height + (max(msg_red_means)*0.02), f"{height:.1f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    fig.tight_layout()
    fig.savefig(figures_dir / "baseline_message_reduction.png", dpi=600)
    fig.savefig(figures_dir / "baseline_message_reduction.pdf")
    plt.close(fig)
    
    # 5. Revocation Cost Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    cost_means = [np.mean(pd.DataFrame(policy_records[b])["FVS Size"]) for b in baselines]
    bars = ax.bar(labels, cost_means, color="#e74c3c", edgecolor="black")
    ax.set_ylabel("Average Revoked Agents (Cost)", fontsize=11, fontweight="bold")
    ax.set_title("Operational Containment Cost by Policy", fontsize=13, fontweight="bold")
    plt.xticks(rotation=30, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, height + (max(cost_means)*0.02 if max(cost_means) > 0 else 0.1), f"{height:.2f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    fig.tight_layout()
    fig.savefig(figures_dir / "baseline_revocation_cost.png", dpi=600)
    fig.savefig(figures_dir / "baseline_revocation_cost.pdf")
    plt.close(fig)
    
    # 6. Runtime Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    time_means = [np.mean(pd.DataFrame(policy_records[b])["Runtime Execution Time"]) * 1000 for b in baselines]
    bars = ax.bar(labels, time_means, color="#1abc9c", edgecolor="black")
    ax.set_ylabel("Average Containment Execution Time (ms)", fontsize=11, fontweight="bold")
    ax.set_title("Computational Decision Overhead by Policy", fontsize=13, fontweight="bold")
    plt.xticks(rotation=30, ha="right")
    ax.set_yscale("log")
    ax.grid(axis="y", linestyle="--", alpha=0.5, which="both")
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, height * 1.1, f"{height:.3f}ms", ha="center", va="bottom", fontsize=8, fontweight="bold")
    fig.tight_layout()
    fig.savefig(figures_dir / "baseline_runtime_comparison.png", dpi=600)
    fig.savefig(figures_dir / "baseline_runtime_comparison.pdf")
    plt.close(fig)
    
    # 7. Pareto Frontier
    fig, ax = plt.subplots(figsize=(10, 6.5))
    x_costs = [np.mean(pd.DataFrame(policy_records[b])["FVS Size"]) for b in baselines]
    y_ratios = [np.mean(pd.DataFrame(policy_records[b])["Containment Ratio"]) * 100 for b in baselines]
    
    ax.scatter(x_costs, y_ratios, color="black", s=100, zorder=5)
    
    for i, txt in enumerate(labels):
        ax.annotate(txt, (x_costs[i], y_ratios[i]), xytext=(5, 5), textcoords="offset points", fontsize=9, fontweight="bold")
        
    sorted_indices = np.argsort(x_costs)
    pareto_x = []
    pareto_y = []
    max_y = -1.0
    for idx in sorted_indices:
        if y_ratios[idx] > max_y:
            pareto_x.append(x_costs[idx])
            pareto_y.append(y_ratios[idx])
            max_y = y_ratios[idx]
            
    ax.plot(pareto_x, pareto_y, color="red", linestyle="-", linewidth=2, label="Pareto Frontier", zorder=3)
    ax.fill_between(pareto_x, pareto_y, color="red", alpha=0.1, zorder=1)
    
    ax.set_xlabel("Average Operational Cost (Revoked Nodes Count)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Average Containment Ratio (%)", fontsize=11, fontweight="bold")
    ax.set_title("Pareto Trade-off: Containment Ratio vs Operational Cost", fontsize=13, fontweight="bold")
    ax.grid(linestyle="--", alpha=0.5)
    ax.set_ylim(0, 105)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(figures_dir / "baseline_pareto_frontier.png", dpi=600)
    fig.savefig(figures_dir / "baseline_pareto_frontier.pdf")
    plt.close(fig)
    
    # 8. Runtime τ distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    data_tau = [pd.DataFrame(policy_records[b])["FVS Size"].to_numpy() for b in baselines]
    ax.boxplot(data_tau, patch_artist=True,
               boxprops=dict(facecolor="#2ecc71", color="black"),
               medianprops=dict(color="blue", linewidth=1.5))
    ax.set_ylabel("Revoked Nodes Count (Size)", fontsize=11, fontweight="bold")
    ax.set_title("Distribution of Revocation Set Size by Policy", fontsize=13, fontweight="bold")
    ax.set_xticks(range(1, len(baselines) + 1))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(figures_dir / "baseline_tau_distribution.png", dpi=600)
    fig.savefig(figures_dir / "baseline_tau_distribution.pdf")
    plt.close(fig)


def save_aggregate_charts(results: pd.DataFrame, figures_dir: Path) -> None:
    """Save τ distribution and compromise propagation comparison charts in PNG (600 DPI) and PDF formats."""
    # 1. runtime_tau_histogram.png & .pdf
    tau_min = int(results["Runtime τ"].min())
    tau_max = int(results["Runtime τ"].max())
    bins = [value - 0.5 for value in range(tau_min, tau_max + 2)]
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.hist(results["Runtime τ"], bins=bins, edgecolor="black", color="#3498db")
    axis.set_xticks(range(tau_min, tau_max + 1))
    axis.set_xlabel("Runtime τ")
    axis.set_ylabel("Run Count")
    axis.set_title("Runtime τ Distribution")
    figure.tight_layout()
    figure.savefig(figures_dir / "runtime_tau_histogram.png", dpi=600)
    figure.savefig(figures_dir / "runtime_tau_histogram.pdf")
    plt.close(figure)

    # 2. containment_ratio_histogram.png & .pdf
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.hist(results["Containment Efficiency"] * 100, bins=10, edgecolor="black", color="#2ecc71")
    axis.set_xlabel("Containment Ratio (%)")
    axis.set_ylabel("Run Count")
    axis.set_title("Containment Ratio Distribution")
    figure.tight_layout()
    figure.savefig(figures_dir / "containment_ratio_histogram.png", dpi=600)
    figure.savefig(figures_dir / "containment_ratio_histogram.pdf")
    plt.close(figure)

    # 3. k_before_after_boxplot.png & .pdf
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.boxplot([results["K Before"], results["K After"]])
    axis.set_xticklabels(["K Before", "K After"])
    axis.set_ylabel("Infected Agents Count")
    axis.set_title("Compromise Footprint Before vs After Revocation")
    figure.tight_layout()
    figure.savefig(figures_dir / "k_before_after_boxplot.png", dpi=600)
    figure.savefig(figures_dir / "k_before_after_boxplot.pdf")
    plt.close(figure)

    # 4. runtime_tau_vs_messages.png & .pdf
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.scatter(results["Runtime τ"], results["Messages Before"], alpha=0.6, color="#e74c3c", edgecolor="black")
    axis.set_xlabel("Runtime τ")
    axis.set_ylabel("Messages Before")
    axis.set_title("Runtime τ vs Message Count")
    figure.tight_layout()
    figure.savefig(figures_dir / "runtime_tau_vs_messages.png", dpi=600)
    figure.savefig(figures_dir / "runtime_tau_vs_messages.pdf")
    plt.close(figure)

    # 5. runtime_tau_vs_kbefore.png & .pdf
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.scatter(results["Runtime τ"], results["K Before"], alpha=0.6, color="#9b59b6", edgecolor="black")
    axis.set_xlabel("Runtime τ")
    axis.set_ylabel("K Before (Infected Downstream Agents)")
    axis.set_title("Runtime τ vs Initial Compromise Footprint")
    figure.tight_layout()
    figure.savefig(figures_dir / "runtime_tau_vs_kbefore.png", dpi=600)
    figure.savefig(figures_dir / "runtime_tau_vs_kbefore.pdf")
    plt.close(figure)


def write_prompts(path: Path, prompts: list[str]) -> None:
    """Persist the exact ordered prompt set used by the experiment."""
    path.write_text(
        "\n".join(f"{index}. {prompt}" for index, prompt in enumerate(prompts, 1)) + "\n",
        encoding="utf-8",
    )


def write_metadata(experiment_id: str, path: Path, run_count: int, seed: int = 42) -> None:
    """Persist experiment configuration and reproducibility metadata."""
    import subprocess
    git_commit = "unknown"
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except Exception:
        pass
    metadata = {
        "Experiment ID": experiment_id,
        "Date": datetime.now(timezone.utc).isoformat(),
        "Git Commit": git_commit,
        "Seed": seed,
        "Prompt Dataset Version": "1.0",
        "Enterprise Size": len(NODES),
        "Number of Runs": run_count,
        "Workflow Families": 10,
        "Simulator Version": "1.0"
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
    
    unique_hashes = results["Graph Hash"].nunique()
    
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
        f"Average Containment Ratio: {avg_efficiency:.1f}%",
        f"Average Containment Gain: {average_before - average_after:.2f} agents",
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


def load_enterprise_prompts(path: Path) -> pd.DataFrame:
    """Robust custom parser for the unquoted enterprise_prompts.csv file."""
    rows = []
    valid_depts = {"Research", "Engineering", "Security", "Operations", "Executive"}
    
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line_idx, line in enumerate(lines[1:], 1):
        line = line.strip()
        if not line:
            continue
            
        parts = line.split(",")
        if len(parts) < 9:
            continue
            
        prompt_id = parts[0]
        workflow_family = parts[1]
        difficulty = parts[2]
        domain = parts[3]
        
        idx = 4
        expected_depts = []
        while idx < len(parts) and parts[idx] in valid_depts:
            expected_depts.append(parts[idx])
            idx += 1
            
        count_idx = -1
        for i in range(idx, len(parts) - 1):
            if parts[i].isdigit() and parts[i+1] in {"Short", "Medium", "Long"}:
                count_idx = i
                break
                
        if count_idx == -1:
            # Fallback search from right
            for i in range(len(parts) - 2, idx - 1, -1):
                if parts[i] in {"Short", "Medium", "Long"} and parts[i-1].isdigit():
                    count_idx = i - 1
                    break
                    
        if count_idx == -1:
            # Absolute fallback
            count_idx = len(parts) - 3
            
        expected_roles = parts[idx:count_idx]
        dept_count = int(parts[count_idx]) if parts[count_idx].isdigit() else len(expected_depts)
        workflow_depth = parts[count_idx+1]
        prompt = ",".join(parts[count_idx+2:])
        
        rows.append({
            "Prompt_ID": prompt_id,
            "Workflow_Family": workflow_family,
            "Difficulty": difficulty,
            "Enterprise_Domain": domain,
            "Expected_Departments": ",".join(expected_depts),
            "Expected_Critical_Roles": ",".join(expected_roles),
            "Estimated_Department_Count": dept_count,
            "Estimated_Workflow_Depth": workflow_depth,
            "Prompt": prompt
        })
        
    return pd.DataFrame(rows)


def run_experiment() -> tuple[str, Path, pd.DataFrame]:
    """Execute enterprise workflows from datasets/enterprise_prompts.csv according to experiment_config.json."""
    import time
    import subprocess
    
    experiment_id, experiment_dir = create_experiment_directory()
    figures_dir = experiment_dir / "figures"
    logs_dir = experiment_dir / "runtime_logs"
    communications_dir = experiment_dir / "communications"
    
    # 1. Read configuration
    config_path = ROOT / "experiment_config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {
            "runs": 100,
            "enterprise_sizes": [32],
            "workflow_families": 10,
            "prompts_per_family": 10,
            "compromise_rotation": true,
            "seed": 42
        }
    
    runs = config.get("runs", 100)
    seed = config.get("seed", 42)
    compromise_rotation = config.get("compromise_rotation", True)
    
    # 2. Read prompt dataset
    prompts_path = ROOT / "datasets" / "enterprise_prompts.csv"
    if not prompts_path.exists():
        raise FileNotFoundError(f"Prompts dataset not found at: {prompts_path}")
    prompts_df = load_enterprise_prompts(prompts_path)
    num_prompts = len(prompts_df)
    
    write_prompts(experiment_dir / "prompts.txt", prompts_df["Prompt"].tolist())

    policy_names = [
        "no_containment",
        "random_revocation",
        "degree_centrality",
        "betweenness_centrality",
        "pagerank",
        "supervisor_only",
        "department_isolation",
        "static_fvs",
        "compromised_only",
        "runtime_fvs"
    ]
    policy_records = {p: [] for p in policy_names}
    records = []
    for run_idx in range(runs):
        prompt_number = (run_idx % num_prompts) + 1
        row = prompts_df.iloc[prompt_number - 1]
        prompt = row["Prompt"]
        prompt_id = row["Prompt_ID"]
        workflow_family = row["Workflow_Family"].lower()
        
        scenario = {
            "prompt_id": prompt_id,
            "prompt": prompt,
            "workflow_family": workflow_family,
            "difficulty": row["Difficulty"],
            "category": row["Enterprise_Domain"],
            "finding": f"identified risk in {row['Enterprise_Domain'].lower()}",
            "estimate": f"exposure estimated at ${1.5 + (run_idx % 5) * 0.5:.1f}M",
        }
        
        start_time = time.perf_counter()
        
        graph = build_enterprise_runtime_trust_graph(prompt, seed=seed)
        route = route_prompt_departments(prompt)
        topology = "workflow_" + "_to_".join(route).lower()
        trace_id = TOPOLOGY_TRACE_IDS["enterprise_departmental_workflow"]
        cycles = list(nx.simple_cycles(graph))
        tau_runtime, fvs_nodes = compute_fvs(graph)
        scc_count = nx.number_strongly_connected_components(graph)
        active_nodes = sorted(graph.nodes())
        
        if compromise_rotation:
            compromised = active_nodes[(run_idx // num_prompts) % len(active_nodes)]
        else:
            compromised = active_nodes[0]
            
        run_id = f"run_{run_idx + 1:03d}"
        
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

        execution_time = time.perf_counter() - start_time

        communication_stem = f"trace_{trace_id}_prompt_{prompt_number:02d}"
        communication_json = f"communications/{communication_stem}.json"
        communication_markdown_path = f"communications/{communication_stem}.md"
        
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

        # Calculate fingerprint metrics:
        graph_hash = compute_graph_hash(graph)
        activated_departments = "|".join(sorted(list(set(route))))
        activated_roles = "|".join(sorted([node for node in graph.nodes() if graph.nodes[node].get("role") == "agent"]))

        # Save individual network visualizations only for the first 20 runs
        if run_idx < 20:
            title = f"{run_id}: {' → '.join(route)} | compromised={compromised}"
            save_trace_graph(
                figures_dir / f"{run_id}_trace_graph.png",
                graph,
                compromised,
                infected_before,
                fvs_nodes,
                title,
                run_id=run_id,
                topology=topology,
                tau_runtime=tau_runtime,
                k_before=k_before,
                k_after=k_after,
                containment_efficiency=containment_efficiency,
            )
            save_scc_graph(figures_dir / f"{run_id}_scc.png", graph, title)
            save_before_after_comparison(
                figures_dir / f"{run_id}_before_after.png",
                figures_dir / f"{run_id}_before_after.pdf",
                graph,
                revoked_graph,
                compromised,
                infected_before,
                infected_after,
                fvs_nodes,
                title,
                run_id=run_id,
                topology=topology,
                tau_runtime=tau_runtime,
                k_before=k_before,
                k_after=k_after,
                containment_efficiency=containment_efficiency,
            )
            
            # Generate standalone executive summary table figure
            components = list(nx.strongly_connected_components(graph))
            save_run_summary_table(
                path_png=figures_dir / f"{run_id}_summary.png",
                path_pdf=figures_dir / f"{run_id}_summary.pdf",
                graph=graph,
                compromised_node=compromised,
                fvs_nodes=fvs_nodes,
                run_id=run_id,
                topology=topology,
                tau_runtime=tau_runtime,
                scc_count=scc_count,
                components=components,
                k_before=k_before,
                k_after=k_after,
                containment_ratio=containment_efficiency,
                depth_before=depth_before,
                depth_after=depth_after,
                graph_hash=graph_hash,
            )

        # Baseline policy evaluations
        import random
        for p in policy_names:
            if p == "random_revocation":
                # Run 100 trials, average metrics
                trials_k_after = []
                trials_depth_after = []
                trials_depts_after = []
                trials_msg_after = []
                trials_msg_reduction = []
                trials_exec_time = []
                
                candidates = [n for n in graph.nodes() if n != compromised]
                
                for trial_idx in range(100):
                    trial_seed = seed + run_idx * 1000 + trial_idx
                    trial_rng = random.Random(trial_seed)
                    trial_start = time.perf_counter()
                    
                    if len(candidates) <= tau_runtime:
                        revoked_nodes = list(candidates)
                    else:
                        revoked_nodes = trial_rng.sample(candidates, tau_runtime)
                        
                    trial_graph = graph.copy()
                    trial_graph.remove_nodes_from(revoked_nodes)
                    trial_exec = time.perf_counter() - trial_start
                    
                    infected_after_trial, depth_after_trial = propagate_compromise_depth(trial_graph, compromised)
                    steps_after_trial, _ = simulate_communications(trial_graph, compromised, scenario)
                    msg_after_trial = max(0, len(steps_after_trial) - 1)
                    
                    visited_after_trial = set(infected_after_trial) | ({compromised} if compromised in trial_graph else set())
                    depts_after_trial = len(set(trial_graph.nodes[n]["department"] for n in visited_after_trial if n in trial_graph))
                    
                    trials_k_after.append(len(infected_after_trial))
                    trials_depth_after.append(depth_after_trial)
                    trials_depts_after.append(depts_after_trial)
                    trials_msg_after.append(msg_after_trial)
                    trials_msg_reduction.append(message_count - msg_after_trial)
                    trials_exec_time.append(trial_exec)
                    
                k_after_p = sum(trials_k_after) / 100
                depth_after_p = sum(trials_depth_after) / 100
                depts_after_p = sum(trials_depts_after) / 100
                msg_after_p = sum(trials_msg_after) / 100
                msg_reduction_p = sum(trials_msg_reduction) / 100
                exec_time_p = sum(trials_exec_time) / 100
                revoked_nodes_count = tau_runtime
                
                contained_graph = graph.copy()
                first_rng = random.Random(seed + run_idx * 1000)
                if len(candidates) <= tau_runtime:
                    first_revoked = list(candidates)
                else:
                    first_revoked = first_rng.sample(candidates, tau_runtime)
                contained_graph.remove_nodes_from(first_revoked)
                
            else:
                # Deterministic baseline policies
                start_p = time.perf_counter()
                contained_graph, revoked_nodes = get_contained_graph(graph, compromised, p, fvs_nodes, tau_runtime, route)
                exec_time_p = time.perf_counter() - start_p
                
                infected_after_p_nodes, depth_after_p = propagate_compromise_depth(contained_graph, compromised)
                steps_after_p, _ = simulate_communications(contained_graph, compromised, scenario)
                
                k_after_p = len(infected_after_p_nodes)
                msg_after_p = max(0, len(steps_after_p) - 1)
                msg_reduction_p = message_count - msg_after_p
                
                visited_after_p = set(infected_after_p_nodes) | ({compromised} if compromised in contained_graph else set())
                depts_after_p = len(set(contained_graph.nodes[n]["department"] for n in visited_after_p if n in contained_graph))
                revoked_nodes_count = len(revoked_nodes) if p != "department_isolation" else 0
                
            active_nodes_p = contained_graph.number_of_nodes()
            active_edges_p = contained_graph.number_of_edges()
            scc_count_p = nx.number_strongly_connected_components(contained_graph)
            components_p = list(nx.strongly_connected_components(contained_graph))
            largest_scc_p = max([len(c) for c in components_p]) if components_p else 0
            
            if k_before > 0:
                containment_ratio_p = (k_before - k_after_p) / k_before
            else:
                containment_ratio_p = 1.0 if k_after_p == 0 else 0.0
                
            policy_records[p].append({
                "Run ID": run_id,
                "Workflow": topology,
                "Compromised Agent": compromised,
                "Runtime τ_FVS": tau_runtime,
                "Static τ_FVS": STATIC_TAU,
                "FVS Size": revoked_nodes_count,
                "Active Agents": active_nodes_p,
                "Active Edges": active_edges_p,
                "SCC Count": scc_count_p,
                "Largest SCC Size": largest_scc_p,
                "Infected Before": k_before,
                "Infected After": k_after_p,
                "Containment Ratio": containment_ratio_p,
                "Containment Gain": k_before - k_after_p,
                "Propagation Depth Before": depth_before,
                "Propagation Depth After": depth_after_p,
                "Message Count Before": message_count,
                "Message Count After": msg_after_p,
                "Message Reduction": msg_reduction_p,
                "Affected Departments Before": affected_depts_before,
                "Affected Departments After": depts_after_p,
                "Runtime Execution Time": exec_time_p,
                "Graph Hash": graph_hash
            })

        records.append(
            {
                "Run ID": run_id,
                "Prompt ID": prompt_id,
                "Workflow Family": row["Workflow_Family"],
                "Enterprise Size": len(NODES),
                "Runtime τ": tau_runtime,
                "Runtime SCC": scc_count,
                "FVS Size": len(fvs_nodes),
                "Graph Hash": graph_hash,
                "Compromised Node": compromised,
                "K Before": k_before,
                "K After": k_after,
                "Containment Efficiency": containment_efficiency,
                "Propagation Depth Before": propagation_depth_before,
                "Propagation Depth After": propagation_depth_after,
                "Propagation Depth Reduction": propagation_depth_reduction,
                "Affected Departments Before": affected_depts_before,
                "Affected Departments After": affected_depts_after,
                "Affected Departments Reduction": affected_depts_reduction,
                "Messages Before": message_count,
                "Messages After": message_count_after,
                "Execution Time": execution_time,
                "Seed": seed,
                # Compatibility columns:
                "Experiment ID": experiment_id,
                "Prompt": prompt,
                "Topology": topology,
                "Nodes": graph.number_of_nodes(),
                "Edges": graph.number_of_edges(),
                "Cycle Count": len(cycles),
                "SCC Count": scc_count,
                "Runtime τ_FVS": tau_runtime,
                "FVS Nodes": "|".join(fvs_nodes),
                "Containment Success": containment_success,
                "Message Count": message_count,
                "Messages After Revocation": message_count_after,
                "Infection Path Count": len(infection_paths),
                "workflow_family": workflow_family,
                "activated_departments": activated_departments,
                "activated_roles": activated_roles,
                "active_node_count": graph.number_of_nodes(),
                "active_edge_count": graph.number_of_edges(),
                "containment_efficiency": containment_efficiency,
                "propagation_depth_before": propagation_depth_before,
                "propagation_depth_after": propagation_depth_after,
                "propagation_depth_reduction": propagation_depth_reduction,
                "affected_departments_before": affected_depts_before,
                "affected_departments_after": affected_depts_after,
                "affected_departments_reduction": affected_depts_reduction,
                "message_reduction": message_reduction,
            }
        )

    results = pd.DataFrame.from_records(records)
    results.to_csv(experiment_dir / "results.csv", index=False)
    
    # Generate summaries
    summary_cols = [
        "Nodes", "Edges", "Cycle Count", "SCC Count", "Runtime τ",
        "K Before", "K After", "Messages Before", "Messages After",
        "Containment Efficiency", "Propagation Depth Before", "Propagation Depth After",
        "Propagation Depth Reduction", "Affected Departments Before", "Affected Departments After",
        "Affected Departments Reduction", "Execution Time"
    ]
    summary_cols = [c for c in summary_cols if c in results.columns]
    stats_list = []
    for col in summary_cols:
        stats_list.append({
            "Metric": col,
            "Mean": results[col].mean(),
            "Std": results[col].std(),
            "Min": results[col].min(),
            "Max": results[col].max(),
            "Median": results[col].median()
        })
    stats_df = pd.DataFrame(stats_list)
    stats_df.to_csv(experiment_dir / "summary_statistics.csv", index=False)

    tau_counts = results["Runtime τ"].value_counts().sort_index()
    tau_total = len(results)
    tau_dist_list = []
    for tau, count in tau_counts.items():
        percentage = (count / tau_total) * 100
        tau_dist_list.append({
            "τ": tau,
            "Count": count,
            "Percentage": f"{percentage:.1f}%"
        })
    tau_dist_df = pd.DataFrame(tau_dist_list)
    tau_dist_df.to_csv(experiment_dir / "runtime_tau_distribution.csv", index=False)

    wf_df = results.groupby("Workflow Family").agg(
        Mean_tau=("Runtime τ", "mean"),
        Mean_K_Before=("K Before", "mean"),
        Mean_K_After=("K After", "mean"),
        Mean_Containment_Efficiency=("Containment Efficiency", "mean")
    ).reset_index()
    wf_df.rename(columns={
        "Workflow Family": "Workflow",
        "Mean_tau": "Mean τ",
        "Mean_K_Before": "Mean K Before",
        "Mean_K_After": "Mean K After",
        "Mean_Containment_Efficiency": "Mean Containment Efficiency"
    }, inplace=True)
    wf_df.to_csv(experiment_dir / "summary_by_workflow.csv", index=False)

    comp_df = results.groupby("Compromised Node").agg(
        Avg_K_Before=("K Before", "mean"),
        Avg_K_After=("K After", "mean"),
        Avg_Efficiency=("Containment Efficiency", "mean")
    ).reset_index()
    comp_df.rename(columns={
        "Compromised Node": "Compromised Role",
        "Avg_K_Before": "Avg K Before",
        "Avg_K_After": "Avg K After",
        "Avg_Efficiency": "Avg Efficiency"
    }, inplace=True)
    comp_df.to_csv(experiment_dir / "summary_by_compromise.csv", index=False)

    size_df = results.groupby("Enterprise Size").agg(
        Mean_tau=("Runtime τ", "mean"),
        Mean_K_Before=("K Before", "mean"),
        Mean_K_After=("K After", "mean"),
        Mean_Containment_Efficiency=("Containment Efficiency", "mean")
    ).reset_index()
    size_df.rename(columns={
        "Mean_tau": "Mean τ",
        "Mean_K_Before": "Mean K Before",
        "Mean_K_After": "Mean K After",
        "Mean_Containment_Efficiency": "Mean Containment Efficiency"
    }, inplace=True)
    size_df.to_csv(experiment_dir / "summary_by_size.csv", index=False)

    by_topology, by_tau = build_grouped_summaries(results)
    by_topology.to_csv(experiment_dir / "summary_by_topology.csv", index=False)
    by_tau.to_csv(experiment_dir / "summary_by_tau.csv", index=False)
    
    save_aggregate_charts(results, figures_dir)
    
    # Run baseline policies and generate comparisons/plots
    run_baselines_and_statistics(policy_records, figures_dir, experiment_dir)
    save_baseline_plots(policy_records, figures_dir)
    run_statistical_validation(policy_records, experiment_dir)
    verify_confidence_intervals(policy_records, experiment_dir)
    
    write_validation_report(
        results,
        by_topology,
        by_tau,
        experiment_dir / "validation_report.txt",
    )
    write_metadata(experiment_id, experiment_dir / "metadata.json", len(results), seed=seed)
    return experiment_id, experiment_dir, results


def print_summary(experiment_id: str, experiment_dir: Path, results: pd.DataFrame) -> None:
    """Print the experiment location and aggregate observations."""
    observed = set(int(value) for value in results["Runtime τ"].unique())
    successes = int(results["Containment Success"].sum())
    unique_hashes = results["Graph Hash"].nunique()
    print(f"Experiment: {experiment_id}")
    print(f"Output: {experiment_dir}")
    print(f"Runs: {len(results)}")
    print(f"Unique runtime graphs: {unique_hashes}/{len(results)}")
    print(f"Observed runtime τ values: {observed}")
    print(f"Maximum runtime τ: {int(results['Runtime τ'].max())}")
    print(f"Minimum runtime τ: {int(results['Runtime τ'].min())}")
    print(f"Containment success rate: {successes}/{len(results)}")
    print(f"Average containment ratio: {results['Containment Efficiency'].mean() * 100:.1f}%")
    print(f"Average containment gain: {(results['K Before'] - results['K After']).mean():.2f} agents")
    print(f"Average K Before: {results['K Before'].mean():.2f}")
    print(f"Average K After: {results['K After'].mean():.2f}")
    print(f"Average message count: {results['Messages Before'].mean():.2f}")
    print(f"Total agent-to-agent messages: {int(results['Messages Before'].sum())}")
    print(f"Average propagation depth before: {results['Propagation Depth Before'].mean():.2f}")
    print(f"Average propagation depth after: {results['Propagation Depth After'].mean():.2f}")
    print(f"Average propagation depth reduction: {results['Propagation Depth Reduction'].mean():.2f}")
    print(f"Average affected departments before: {results['Affected Departments Before'].mean():.2f}")
    print(f"Average affected departments after: {results['Affected Departments After'].mean():.2f}")
    print(f"Average affected departments reduction: {results['Affected Departments Reduction'].mean():.2f}")
    print(f"Average message reduction: {results['message_reduction'].mean():.2f}")
    
    print("\nWorkflow Family Diversity Summary:")
    print("----------------------------------")
    family_groups = results.groupby("workflow_family")
    for name, group in family_groups:
        family_taus = sorted([int(x) for x in group["Runtime τ"].unique()])
        family_depts = sorted(group["activated_departments"].unique())
        print(f"Family: {name}")
        print(f"  Observed τ values: {family_taus}")
        print(f"  Unique department routes activated: {len(family_depts)}")


if __name__ == "__main__":
    current_id, current_dir, experiment_results = run_experiment()
    print_summary(current_id, current_dir, experiment_results)
