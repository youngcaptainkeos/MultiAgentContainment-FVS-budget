"""Deterministic enterprise organization topology for FVS experiments.

This module intentionally only defines the topology generator. It does not
modify runtime logging, FVS computation, experiment orchestration,
visualization, reporting, or output folder behavior.
"""

from __future__ import annotations

import networkx as nx


DEFAULT_SEED = 42


DEPARTMENTS = {
    "Executive": {
        "supervisor": "Executive Supervisor",
        "agents": [
            "Executive Strategy",
            "Executive Legal",
            "Executive Finance",
            "Executive Communications",
            "Executive Governance",
        ],
        "internal_edges": [
            ("Executive Supervisor", "Executive Strategy"),
            ("Executive Supervisor", "Executive Legal"),
            ("Executive Supervisor", "Executive Finance"),
            ("Executive Supervisor", "Executive Communications"),
            ("Executive Supervisor", "Executive Governance"),
            ("Executive Strategy", "Executive Finance"),
            ("Executive Finance", "Executive Governance"),
            ("Executive Governance", "Executive Supervisor"),
            ("Executive Legal", "Executive Communications"),
            ("Executive Communications", "Executive Supervisor"),
        ],
    },
    "Research": {
        "supervisor": "Research Supervisor",
        "agents": [
            "Research Scientist",
            "Research Analyst",
            "Research Writer",
            "Research Reviewer",
            "Research Data Steward",
        ],
        "internal_edges": [
            ("Research Supervisor", "Research Scientist"),
            ("Research Supervisor", "Research Analyst"),
            ("Research Scientist", "Research Analyst"),
            ("Research Analyst", "Research Writer"),
            ("Research Writer", "Research Reviewer"),
            ("Research Reviewer", "Research Supervisor"),
            ("Research Data Steward", "Research Scientist"),
            ("Research Reviewer", "Research Data Steward"),
        ],
    },
    "Engineering": {
        "supervisor": "Engineering Supervisor",
        "agents": [
            "Engineering Planner",
            "Engineering Architect",
            "Engineering Developer",
            "Engineering QA",
            "Engineering DevOps",
            "Engineering Release Manager",
        ],
        "internal_edges": [
            ("Engineering Supervisor", "Engineering Planner"),
            ("Engineering Planner", "Engineering Architect"),
            ("Engineering Architect", "Engineering Developer"),
            ("Engineering Developer", "Engineering QA"),
            ("Engineering QA", "Engineering Release Manager"),
            ("Engineering Release Manager", "Engineering Supervisor"),
            ("Engineering DevOps", "Engineering Developer"),
            ("Engineering QA", "Engineering DevOps"),
            ("Engineering Supervisor", "Engineering DevOps"),
        ],
    },
    "Security": {
        "supervisor": "Security Supervisor",
        "agents": [
            "Security Analyst",
            "Security Auditor",
            "Security Risk",
            "Security Incident Response",
            "Security Compliance",
        ],
        "internal_edges": [
            ("Security Supervisor", "Security Analyst"),
            ("Security Analyst", "Security Incident Response"),
            ("Security Incident Response", "Security Risk"),
            ("Security Risk", "Security Compliance"),
            ("Security Compliance", "Security Auditor"),
            ("Security Auditor", "Security Supervisor"),
            ("Security Supervisor", "Security Compliance"),
            ("Security Risk", "Security Analyst"),
        ],
    },
    "Operations": {
        "supervisor": "Operations Supervisor",
        "agents": [
            "Operations Finance",
            "Operations Procurement",
            "Operations Support",
            "Operations Logistics",
            "Operations Vendor Manager",
            "Operations Continuity",
        ],
        "internal_edges": [
            ("Operations Supervisor", "Operations Finance"),
            ("Operations Finance", "Operations Procurement"),
            ("Operations Procurement", "Operations Vendor Manager"),
            ("Operations Vendor Manager", "Operations Logistics"),
            ("Operations Logistics", "Operations Support"),
            ("Operations Support", "Operations Supervisor"),
            ("Operations Continuity", "Operations Logistics"),
            ("Operations Supervisor", "Operations Continuity"),
            ("Operations Finance", "Operations Continuity"),
        ],
    },
}


SUPERVISOR_COMMUNICATION_EDGES = [
    ("Executive Supervisor", "Research Supervisor"),
    ("Executive Supervisor", "Engineering Supervisor"),
    ("Executive Supervisor", "Security Supervisor"),
    ("Executive Supervisor", "Operations Supervisor"),
    ("Research Supervisor", "Executive Supervisor"),
    ("Research Supervisor", "Engineering Supervisor"),
    ("Research Supervisor", "Security Supervisor"),
    ("Engineering Supervisor", "Executive Supervisor"),
    ("Engineering Supervisor", "Research Supervisor"),
    ("Engineering Supervisor", "Security Supervisor"),
    ("Engineering Supervisor", "Operations Supervisor"),
    ("Security Supervisor", "Executive Supervisor"),
    ("Security Supervisor", "Engineering Supervisor"),
    ("Security Supervisor", "Operations Supervisor"),
    ("Operations Supervisor", "Executive Supervisor"),
    ("Operations Supervisor", "Research Supervisor"),
    ("Operations Supervisor", "Security Supervisor"),
]


CROSS_DEPARTMENT_EDGES = [
    ("Research Writer", "Engineering Planner"),
    ("Engineering QA", "Security Auditor"),
    ("Security Risk", "Executive Supervisor"),
    ("Operations Finance", "Research Supervisor"),
]


WORKFLOW_ROUTES = {
    "research": ["Executive", "Research", "Engineering", "Executive"],
    "engineering": ["Executive", "Engineering", "Security", "Executive"],
    "security_incident": ["Executive", "Security", "Engineering", "Executive"],
    "enterprise_architecture": [
        "Executive",
        "Research",
        "Engineering",
        "Security",
        "Operations",
        "Executive",
    ],
}


WORKFLOW_TEMPLATES = [
    ["Executive", "Research", "Engineering", "Executive"],
    ["Executive", "Research", "Security", "Operations", "Executive"],
    ["Operations", "Security", "Engineering", "Executive"],
    ["Research", "Security", "Engineering", "Operations", "Executive"],
    ["Executive", "Engineering", "Security", "Operations", "Executive"],
    ["Executive", "Research", "Engineering", "Security", "Operations", "Executive"],
]


PROMPT_TYPE_KEYWORDS = {
    "security_incident": [
        "attack",
        "breach",
        "incident",
        "ransomware",
        "compromise",
        "threat",
        "zero-trust",
        "security incident",
    ],
    "enterprise_architecture": [
        "architecture",
        "platform",
        "migration",
        "multi-region",
        "enterprise",
        "supply-chain",
        "workflow",
        "system design",
    ],
    "engineering": [
        "build",
        "code",
        "developer",
        "deployment",
        "design",
        "implementation",
        "infrastructure",
        "microservices",
        "release",
    ],
    "research": [
        "analyze",
        "assess",
        "evaluate",
        "feasibility",
        "research",
        "report",
        "study",
    ],
}


ROUTE_INTERNAL_ENTRYPOINTS = {
    "Executive": [
        ("Executive Supervisor", "Executive Strategy"),
        ("Executive Strategy", "Executive Finance"),
        ("Executive Finance", "Executive Governance"),
        ("Executive Governance", "Executive Supervisor"),
    ],
    "Research": [
        ("Research Supervisor", "Research Scientist"),
        ("Research Scientist", "Research Analyst"),
        ("Research Analyst", "Research Writer"),
        ("Research Writer", "Research Reviewer"),
        ("Research Reviewer", "Research Supervisor"),
    ],
    "Engineering": [
        ("Engineering Supervisor", "Engineering Planner"),
        ("Engineering Planner", "Engineering Architect"),
        ("Engineering Architect", "Engineering Developer"),
        ("Engineering Developer", "Engineering QA"),
        ("Engineering QA", "Engineering Release Manager"),
        ("Engineering Release Manager", "Engineering Supervisor"),
    ],
    "Security": [
        ("Security Supervisor", "Security Analyst"),
        ("Security Analyst", "Security Incident Response"),
        ("Security Incident Response", "Security Risk"),
        ("Security Risk", "Security Compliance"),
        ("Security Compliance", "Security Auditor"),
        ("Security Auditor", "Security Supervisor"),
    ],
    "Operations": [
        ("Operations Supervisor", "Operations Finance"),
        ("Operations Finance", "Operations Procurement"),
        ("Operations Procurement", "Operations Vendor Manager"),
        ("Operations Vendor Manager", "Operations Logistics"),
        ("Operations Logistics", "Operations Support"),
        ("Operations Support", "Operations Supervisor"),
    ],
}


ROUTE_CROSS_DEPARTMENT_EDGES = {
    ("Executive", "Research"): ("Executive Supervisor", "Research Supervisor"),
    ("Research", "Executive"): ("Research Supervisor", "Executive Supervisor"),
    ("Executive", "Engineering"): ("Executive Supervisor", "Engineering Supervisor"),
    ("Engineering", "Executive"): ("Engineering Supervisor", "Executive Supervisor"),
    ("Executive", "Security"): ("Executive Supervisor", "Security Supervisor"),
    ("Security", "Executive"): ("Security Risk", "Executive Supervisor"),
    ("Executive", "Operations"): ("Executive Supervisor", "Operations Supervisor"),
    ("Operations", "Executive"): ("Operations Supervisor", "Executive Supervisor"),
    ("Research", "Engineering"): ("Research Writer", "Engineering Planner"),
    ("Research", "Security"): ("Research Supervisor", "Security Supervisor"),
    ("Engineering", "Research"): ("Engineering Supervisor", "Research Supervisor"),
    ("Engineering", "Security"): ("Engineering QA", "Security Auditor"),
    ("Engineering", "Operations"): ("Engineering Supervisor", "Operations Supervisor"),
    ("Security", "Engineering"): ("Security Supervisor", "Engineering Supervisor"),
    ("Security", "Operations"): ("Security Supervisor", "Operations Supervisor"),
    ("Operations", "Security"): ("Operations Supervisor", "Security Supervisor"),
    ("Operations", "Research"): ("Operations Finance", "Research Supervisor"),
}


def build_enterprise_topology(seed: int = DEFAULT_SEED) -> nx.DiGraph:
    """Build a deterministic enterprise communication topology.

    The graph models five departments with one supervisor each, 5-6 specialized
    agents per department, realistic intra-department communication, at least
    one feedback cycle per department, supervisor-mediated department-to-
    department communication, and selected direct cross-department links.
    """

    # The seed is part of the public generator signature so callers can keep a
    # stable experiment contract. The current topology is fully specified, so no
    # random sampling is needed.
    _ = seed
    graph = nx.DiGraph()

    for department, spec in DEPARTMENTS.items():
        supervisor = spec["supervisor"]
        graph.add_node(supervisor, department=department, role="supervisor")

        for agent in spec["agents"]:
            graph.add_node(agent, department=department, role="agent")

        graph.add_edges_from(spec["internal_edges"])

    graph.add_edges_from(SUPERVISOR_COMMUNICATION_EDGES)
    graph.add_edges_from(CROSS_DEPARTMENT_EDGES)

    return graph


def create_enterprise_topology(seed: int = DEFAULT_SEED) -> nx.DiGraph:
    """Compatibility alias for callers that prefer a create_* naming style."""

    return build_enterprise_topology(seed=seed)


def classify_prompt(prompt: str) -> str:
    """Classify a prompt into a deterministic enterprise workflow type."""

    normalized_prompt = prompt.casefold()
    for prompt_type, keywords in PROMPT_TYPE_KEYWORDS.items():
        if any(keyword in normalized_prompt for keyword in keywords):
            return prompt_type
    return "enterprise_architecture"


def route_prompt_departments(prompt: str) -> list[str]:
    """Return a deterministic varied department route activated by a prompt."""

    prompt_type = classify_prompt(prompt)
    base_route = WORKFLOW_ROUTES[prompt_type]
    selector = sum(ord(character) for character in prompt) + len(prompt_type)
    route = WORKFLOW_TEMPLATES[selector % len(WORKFLOW_TEMPLATES)]
    if set(base_route).issubset(route):
        return list(route)
    return list(base_route)


def build_enterprise_runtime_trust_graph(
    prompt: str,
    seed: int = DEFAULT_SEED,
) -> nx.DiGraph:
    """Build the prompt-specific runtime trust graph.

    The static enterprise topology contains the full organization. This runtime
    graph activates only departments needed for the prompt's workflow route and
    only the supervisor/cross-department links used by that route.
    """

    static_graph = build_enterprise_topology(seed=seed)
    route = route_prompt_departments(prompt)
    active_departments = set(route)
    runtime_graph = nx.DiGraph()
    runtime_graph.graph["prompt_type"] = classify_prompt(prompt)
    runtime_graph.graph["department_route"] = route

    for node, attributes in static_graph.nodes(data=True):
        if attributes["department"] in active_departments:
            runtime_graph.add_node(node, **attributes)

    for department in sorted(active_departments):
        runtime_graph.add_edges_from(ROUTE_INTERNAL_ENTRYPOINTS[department])

    for source_department, target_department in zip(route, route[1:]):
        if source_department == target_department:
            continue
        route_edge = ROUTE_CROSS_DEPARTMENT_EDGES[(source_department, target_department)]
        runtime_graph.add_edge(*route_edge)

    return runtime_graph
