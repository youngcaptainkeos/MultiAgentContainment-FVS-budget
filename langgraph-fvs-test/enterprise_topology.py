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
    "research": ["Executive", "Research", "Executive"],
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
    # --- 1. Research-Intensive (0-5) ---
    {
        "family": "research_intensive",
        "route": ["Executive", "Research", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Communications"],
            "Research": ["Research Scientist", "Research Analyst", "Research Reviewer"]
        }
    },
    {
        "family": "research_intensive",
        "route": ["Executive", "Research", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Research": ["Research Scientist", "Research Analyst", "Research Writer"],
            "Engineering": ["Engineering Planner", "Engineering Architect"]
        }
    },
    {
        "family": "research_intensive",
        "route": ["Executive", "Research", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Research": ["Research Analyst", "Research Reviewer"],
            "Security": ["Security Analyst", "Security Compliance"]
        }
    },
    {
        "family": "research_intensive",
        "route": ["Research", "Engineering", "Executive"],
        "base_roles": {
            "Research": ["Research Scientist", "Research Writer"],
            "Engineering": ["Engineering Planner", "Engineering Developer"],
            "Executive": ["Executive Strategy"]
        }
    },
    {
        "family": "research_intensive",
        "route": ["Research", "Security", "Executive"],
        "base_roles": {
            "Research": ["Research Analyst", "Research Reviewer"],
            "Security": ["Security Auditor", "Security Risk"],
            "Executive": ["Executive Strategy"]
        }
    },
    {
        "family": "research_intensive",
        "route": ["Executive", "Research", "Engineering", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Research": ["Research Scientist", "Research Analyst", "Research Reviewer"],
            "Engineering": ["Engineering Planner", "Engineering Architect"],
            "Security": ["Security Analyst", "Security Compliance"]
        }
    },

    # --- 2. Engineering-Intensive (6-11) ---
    {
        "family": "engineering_intensive",
        "route": ["Executive", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Engineering": ["Engineering Architect", "Engineering Developer", "Engineering QA"]
        }
    },
    {
        "family": "engineering_intensive",
        "route": ["Executive", "Engineering", "Research", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Engineering": ["Engineering Planner", "Engineering Architect", "Engineering Developer"],
            "Research": ["Research Scientist", "Research Reviewer"]
        }
    },
    {
        "family": "engineering_intensive",
        "route": ["Executive", "Engineering", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Engineering": ["Engineering Developer", "Engineering QA", "Engineering DevOps"],
            "Security": ["Security Analyst", "Security Compliance"]
        }
    },
    {
        "family": "engineering_intensive",
        "route": ["Executive", "Engineering", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Engineering": ["Engineering Developer", "Engineering QA", "Engineering Release Manager"],
            "Operations": ["Operations Logistics", "Operations Support"]
        }
    },
    {
        "family": "engineering_intensive",
        "route": ["Engineering", "Research", "Executive"],
        "base_roles": {
            "Engineering": ["Engineering Architect", "Engineering Developer"],
            "Research": ["Research Scientist", "Research Analyst"],
            "Executive": ["Executive Strategy"]
        }
    },
    {
        "family": "engineering_intensive",
        "route": ["Engineering", "Security", "Executive"],
        "base_roles": {
            "Engineering": ["Engineering Developer", "Engineering QA"],
            "Security": ["Security Auditor", "Security Compliance"],
            "Executive": ["Executive Strategy"]
        }
    },

    # --- 3. Security Incident Response (12-17) ---
    {
        "family": "security_incident_response",
        "route": ["Executive", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Communications", "Executive Legal"],
            "Security": ["Security Analyst", "Security Incident Response", "Security Risk"]
        }
    },
    {
        "family": "security_incident_response",
        "route": ["Executive", "Security", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Legal"],
            "Security": ["Security Analyst", "Security Incident Response", "Security Risk"],
            "Engineering": ["Engineering Planner", "Engineering DevOps"]
        }
    },
    {
        "family": "security_incident_response",
        "route": ["Executive", "Security", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Communications"],
            "Security": ["Security Analyst", "Security Incident Response", "Security Compliance"],
            "Operations": ["Operations Support", "Operations Continuity"]
        }
    },
    {
        "family": "security_incident_response",
        "route": ["Security", "Engineering", "Executive"],
        "base_roles": {
            "Security": ["Security Analyst", "Security Incident Response", "Security Risk"],
            "Engineering": ["Engineering DevOps", "Engineering Release Manager"],
            "Executive": ["Executive Strategy"]
        }
    },
    {
        "family": "security_incident_response",
        "route": ["Security", "Operations", "Executive"],
        "base_roles": {
            "Security": ["Security Analyst", "Security Incident Response"],
            "Operations": ["Operations Support", "Operations Continuity"],
            "Executive": ["Executive Strategy"]
        }
    },
    {
        "family": "security_incident_response",
        "route": ["Executive", "Security", "Engineering", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Communications"],
            "Security": ["Security Analyst", "Security Incident Response", "Security Risk"],
            "Engineering": ["Engineering DevOps"],
            "Operations": ["Operations Support"]
        }
    },

    # --- 4. Operations Planning (18-23) ---
    {
        "family": "operations_planning",
        "route": ["Executive", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Finance"],
            "Operations": ["Operations Procurement", "Operations Logistics", "Operations Vendor Manager"]
        }
    },
    {
        "family": "operations_planning",
        "route": ["Executive", "Operations", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Operations": ["Operations Logistics", "Operations Vendor Manager", "Operations Continuity"],
            "Security": ["Security Compliance", "Security Risk"]
        }
    },
    {
        "family": "operations_planning",
        "route": ["Executive", "Operations", "Research", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Operations": ["Operations Procurement", "Operations Logistics"],
            "Research": ["Research Analyst", "Research Data Steward"]
        }
    },
    {
        "family": "operations_planning",
        "route": ["Operations", "Security", "Executive"],
        "base_roles": {
            "Operations": ["Operations Vendor Manager", "Operations Logistics"],
            "Security": ["Security Compliance", "Security Auditor"],
            "Executive": ["Executive Strategy"]
        }
    },
    {
        "family": "operations_planning",
        "route": ["Operations", "Research", "Executive"],
        "base_roles": {
            "Operations": ["Operations Procurement", "Operations Finance"],
            "Research": ["Research Analyst", "Research Data Steward"],
            "Executive": ["Executive Strategy"]
        }
    },
    {
        "family": "operations_planning",
        "route": ["Executive", "Operations", "Security", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Operations": ["Operations Logistics", "Operations Support"],
            "Security": ["Security Compliance"],
            "Engineering": ["Engineering Planner"]
        }
    },

    # --- 5. Executive Decision Support (24-29) ---
    {
        "family": "executive_decision_support",
        "route": ["Executive", "Research", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Legal", "Executive Governance"],
            "Research": ["Research Scientist", "Research Analyst", "Research Reviewer"]
        }
    },
    {
        "family": "executive_decision_support",
        "route": ["Executive", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Finance", "Executive Governance"],
            "Engineering": ["Engineering Planner", "Engineering Architect", "Engineering Release Manager"]
        }
    },
    {
        "family": "executive_decision_support",
        "route": ["Executive", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Legal", "Executive Governance"],
            "Security": ["Security Analyst", "Security Auditor", "Security Risk"]
        }
    },
    {
        "family": "executive_decision_support",
        "route": ["Executive", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Finance", "Executive Governance"],
            "Operations": ["Operations Procurement", "Operations Vendor Manager", "Operations Continuity"]
        }
    },
    {
        "family": "executive_decision_support",
        "route": ["Executive", "Research", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Research": ["Research Scientist", "Research Analyst"],
            "Engineering": ["Engineering Planner", "Engineering Architect"]
        }
    },
    {
        "family": "executive_decision_support",
        "route": ["Executive", "Research", "Security", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Research": ["Research Scientist"],
            "Security": ["Security Analyst"],
            "Operations": ["Operations Support"]
        }
    },

    # --- 6. Multi-Department Compliance (30-35) ---
    {
        "family": "multi_department_compliance",
        "route": ["Executive", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Legal", "Executive Governance"],
            "Security": ["Security Auditor", "Security Compliance"]
        }
    },
    {
        "family": "multi_department_compliance",
        "route": ["Executive", "Security", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Legal", "Executive Governance"],
            "Security": ["Security Compliance", "Security Risk"],
            "Operations": ["Operations Procurement", "Operations Vendor Manager"]
        }
    },
    {
        "family": "multi_department_compliance",
        "route": ["Security", "Operations", "Executive"],
        "base_roles": {
            "Security": ["Security Compliance", "Security Auditor"],
            "Operations": ["Operations Vendor Manager", "Operations Logistics"],
            "Executive": ["Executive Legal", "Executive Strategy"]
        }
    },
    {
        "family": "multi_department_compliance",
        "route": ["Executive", "Security", "Engineering", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Legal", "Executive Governance"],
            "Security": ["Security Compliance", "Security Auditor"],
            "Engineering": ["Engineering QA", "Engineering Release Manager"],
            "Operations": ["Operations Vendor Manager"]
        }
    },
    {
        "family": "multi_department_compliance",
        "route": ["Executive", "Research", "Security", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Legal", "Executive Governance"],
            "Research": ["Research Analyst", "Research Data Steward"],
            "Security": ["Security Compliance"],
            "Operations": ["Operations Vendor Manager"]
        }
    },
    {
        "family": "multi_department_compliance",
        "route": ["Executive", "Research", "Security", "Engineering", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Legal", "Executive Governance"],
            "Research": ["Research Data Steward"],
            "Security": ["Security Compliance"],
            "Engineering": ["Engineering QA"],
            "Operations": ["Operations Vendor Manager"]
        }
    },

    # --- 7. Infrastructure Deployment (36-41) ---
    {
        "family": "infrastructure_deployment",
        "route": ["Executive", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Finance"],
            "Engineering": ["Engineering Architect", "Engineering Developer", "Engineering DevOps"]
        }
    },
    {
        "family": "infrastructure_deployment",
        "route": ["Executive", "Engineering", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Engineering": ["Engineering Architect", "Engineering Developer", "Engineering DevOps"],
            "Operations": ["Operations Logistics", "Operations Support"]
        }
    },
    {
        "family": "infrastructure_deployment",
        "route": ["Engineering", "Operations", "Executive"],
        "base_roles": {
            "Engineering": ["Engineering Architect", "Engineering DevOps", "Engineering Release Manager"],
            "Operations": ["Operations Logistics", "Operations Continuity"],
            "Executive": ["Executive Strategy"]
        }
    },
    {
        "family": "infrastructure_deployment",
        "route": ["Executive", "Operations", "Security", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Operations": ["Operations Logistics", "Operations Support"],
            "Security": ["Security Analyst"],
            "Engineering": ["Engineering Architect", "Engineering DevOps"]
        }
    },
    {
        "family": "infrastructure_deployment",
        "route": ["Executive", "Engineering", "Operations", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Engineering": ["Engineering Architect", "Engineering DevOps"],
            "Operations": ["Operations Logistics", "Operations Continuity"],
            "Security": ["Security Compliance"]
        }
    },
    {
        "family": "infrastructure_deployment",
        "route": ["Executive", "Research", "Engineering", "Operations", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy"],
            "Research": ["Research Analyst"],
            "Engineering": ["Engineering Architect", "Engineering DevOps"],
            "Operations": ["Operations Logistics"],
            "Security": ["Security Analyst"]
        }
    },

    # --- 8. Risk Assessment (42-47) ---
    {
        "family": "risk_assessment",
        "route": ["Executive", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Legal", "Executive Governance"],
            "Security": ["Security Analyst", "Security Risk", "Security Auditor"]
        }
    },
    {
        "family": "risk_assessment",
        "route": ["Executive", "Research", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Research": ["Research Analyst", "Research Reviewer"],
            "Security": ["Security Analyst", "Security Risk"]
        }
    },
    {
        "family": "risk_assessment",
        "route": ["Research", "Security", "Executive"],
        "base_roles": {
            "Research": ["Research Scientist", "Research Analyst"],
            "Security": ["Security Analyst", "Security Risk"],
            "Executive": ["Executive Governance"]
        }
    },
    {
        "family": "risk_assessment",
        "route": ["Executive", "Research", "Security", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Research": ["Research Analyst"],
            "Security": ["Security Analyst", "Security Risk"],
            "Engineering": ["Engineering Planner", "Engineering QA"]
        }
    },
    {
        "family": "risk_assessment",
        "route": ["Executive", "Research", "Security", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Research": ["Research Analyst"],
            "Security": ["Security Analyst", "Security Risk"],
            "Operations": ["Operations Continuity"]
        }
    },
    {
        "family": "risk_assessment",
        "route": ["Executive", "Research", "Security", "Engineering", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Research": ["Research Analyst"],
            "Security": ["Security Analyst", "Security Risk"],
            "Engineering": ["Engineering QA"],
            "Operations": ["Operations Continuity"]
        }
    },

    # --- 9. Financial Planning (48-53) ---
    {
        "family": "financial_planning",
        "route": ["Executive", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Finance"],
            "Operations": ["Operations Finance", "Operations Procurement", "Operations Vendor Manager"]
        }
    },
    {
        "family": "financial_planning",
        "route": ["Executive", "Operations", "Research", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Finance"],
            "Operations": ["Operations Finance", "Operations Procurement"],
            "Research": ["Research Analyst", "Research Data Steward"]
        }
    },
    {
        "family": "financial_planning",
        "route": ["Operations", "Research", "Executive"],
        "base_roles": {
            "Operations": ["Operations Finance", "Operations Procurement"],
            "Research": ["Research Analyst", "Research Reviewer"],
            "Executive": ["Executive Finance"]
        }
    },
    {
        "family": "financial_planning",
        "route": ["Executive", "Operations", "Research", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Finance"],
            "Operations": ["Operations Finance", "Operations Procurement"],
            "Research": ["Research Analyst"],
            "Engineering": ["Engineering Planner"]
        }
    },
    {
        "family": "financial_planning",
        "route": ["Executive", "Operations", "Research", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Finance"],
            "Operations": ["Operations Finance", "Operations Procurement"],
            "Research": ["Research Analyst"],
            "Security": ["Security Compliance"]
        }
    },
    {
        "family": "financial_planning",
        "route": ["Executive", "Research", "Engineering", "Security", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Finance"],
            "Research": ["Research Analyst"],
            "Engineering": ["Engineering Planner"],
            "Security": ["Security Compliance"],
            "Operations": ["Operations Finance"]
        }
    },

    # --- 10. AI Governance (54-59) ---
    {
        "family": "ai_governance",
        "route": ["Executive", "Research", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Legal", "Executive Governance"],
            "Research": ["Research Scientist", "Research Analyst", "Research Reviewer"]
        }
    },
    {
        "family": "ai_governance",
        "route": ["Executive", "Research", "Engineering", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Research": ["Research Scientist", "Research Analyst", "Research Reviewer"],
            "Engineering": ["Engineering Planner", "Engineering Developer", "Engineering QA"]
        }
    },
    {
        "family": "ai_governance",
        "route": ["Research", "Engineering", "Executive"],
        "base_roles": {
            "Research": ["Research Scientist", "Research Analyst", "Research Reviewer"],
            "Engineering": ["Engineering Architect", "Engineering QA"],
            "Executive": ["Executive Governance"]
        }
    },
    {
        "family": "ai_governance",
        "route": ["Executive", "Research", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Legal", "Executive Governance"],
            "Research": ["Research Scientist", "Research Analyst"],
            "Security": ["Security Risk", "Security Compliance"]
        }
    },
    {
        "family": "ai_governance",
        "route": ["Executive", "Research", "Engineering", "Security", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Research": ["Research Scientist", "Research Analyst"],
            "Engineering": ["Engineering QA"],
            "Security": ["Security Risk", "Security Compliance"]
        }
    },
    {
        "family": "ai_governance",
        "route": ["Executive", "Research", "Engineering", "Security", "Operations", "Executive"],
        "base_roles": {
            "Executive": ["Executive Strategy", "Executive Governance"],
            "Research": ["Research Scientist"],
            "Engineering": ["Engineering QA"],
            "Security": ["Security Risk", "Security Compliance"],
            "Operations": ["Operations Support"]
        }
    }
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


def classify_workflow_family(prompt: str) -> str:
    """Classify a prompt into one of 10 enterprise workflow families."""
    prompt_lower = prompt.lower()
    
    if any(k in prompt_lower for k in ["ai", "model", "autonomous", "generative"]):
        return "ai_governance"
    if any(k in prompt_lower for k in ["finance", "cost", "budget", "savings", "billing", "transaction"]):
        return "financial_planning"
    if any(k in prompt_lower for k in ["risk", "exposure", "vulnerability"]):
        return "risk_assessment"
    if any(k in prompt_lower for k in ["compliance", "audit", "soc 2", "gdpr", "pci", "hipaa", "policy", "regulation"]):
        return "multi_department_compliance"
    if any(k in prompt_lower for k in ["infrastructure", "cloud", "landing zone", "network", "datacenter", "migration", "gateway"]):
        return "infrastructure_deployment"
    if any(k in prompt_lower for k in ["ransomware", "attack", "breach", "incident", "ioc", "forensic", "phishing", "exfiltration", "compromise"]):
        return "security_incident_response"
    if any(k in prompt_lower for k in ["operations", "procurement", "vendor", "logistics", "support", "continuity"]):
        return "operations_planning"
    if any(k in prompt_lower for k in ["executive", "strategy", "board", "governance", "decision", "leader"]):
        return "executive_decision_support"
    if any(k in prompt_lower for k in ["build", "code", "developer", "implement", "deployment", "microservices", "refactor", "service"]):
        return "engineering_intensive"
    return "research_intensive"


def select_department_roles(prompt: str, department: str, base_roles: list[str]) -> set[str]:
    """Select active workers according to the workflow template and task semantics."""
    active_roles = set(base_roles)
    prompt_lower = prompt.lower()
    
    # Keyword-based heuristics to activate additional contextual roles:
    # Finance / Cost
    if any(k in prompt_lower for k in ["cost", "finance", "budget", "dollar", "price", "spend", "$", "expense", "saving"]):
        if department == "Executive":
            active_roles.add("Executive Finance")
        elif department == "Operations":
            active_roles.add("Operations Finance")
            
    # Legal / Compliance / Governance
    if any(k in prompt_lower for k in ["legal", "regulation", "law", "compliance", "governance", "audit", "soc 2", "gdpr", "pci", "hipaa", "policy"]):
        if department == "Executive":
            active_roles.add("Executive Legal")
            active_roles.add("Executive Governance")
        elif department == "Security":
            active_roles.add("Security Compliance")
            active_roles.add("Security Auditor")
            
    # Communications
    if any(k in prompt_lower for k in ["communication", "public", "pr", "media", "customer", "vendor"]):
        if department == "Executive":
            active_roles.add("Executive Communications")
        elif department == "Operations":
            active_roles.add("Operations Vendor Manager")
            active_roles.add("Operations Support")
            
    # Strategy / Architecture / Planning
    if any(k in prompt_lower for k in ["strategy", "plan", "roadmap", "migration", "architecture", "system design"]):
        if department == "Executive":
            active_roles.add("Executive Strategy")
        elif department == "Engineering":
            active_roles.add("Engineering Planner")
            active_roles.add("Engineering Architect")
            
    # Security / Risk / Incidents
    if any(k in prompt_lower for k in ["security", "incident", "ransomware", "attack", "breach", "threat", "compromise", "risk"]):
        if department == "Security":
            active_roles.add("Security Analyst")
            active_roles.add("Security Risk")
            active_roles.add("Security Incident Response")
            
    # Code / Build / DevOps / Cloud
    if any(k in prompt_lower for k in ["build", "code", "developer", "implement", "deploy", "platform", "gateway", "infrastructure", "cloud", "devops"]):
        if department == "Engineering":
            active_roles.add("Engineering Developer")
            active_roles.add("Engineering Architect")
            active_roles.add("Engineering QA")
            active_roles.add("Engineering DevOps")
            
    # Research / Analysis
    if any(k in prompt_lower for k in ["research", "study", "feasibility", "analyze", "assess", "report", "brief"]):
        if department == "Research":
            active_roles.add("Research Scientist")
            active_roles.add("Research Analyst")
            active_roles.add("Research Writer")
            active_roles.add("Research Reviewer")
            
    # Data / Logistics
    if any(k in prompt_lower for k in ["data", "database", "analytics", "steward", "collect", "logistics", "supply-chain"]):
        if department == "Research":
            active_roles.add("Research Data Steward")
        elif department == "Operations":
            active_roles.add("Operations Logistics")
            active_roles.add("Operations Continuity")
            
    # Filter only to valid agents belonging to this department
    valid_agents = set(DEPARTMENTS[department]["agents"])
    active_roles = active_roles.intersection(valid_agents)
    
    return active_roles


def compute_graph_hash(graph: nx.DiGraph) -> str:
    """Generate a SHA-256 fingerprint for a runtime graph based on its sorted nodes and edges."""
    import hashlib
    nodes = sorted(list(graph.nodes()))
    edges = sorted(list(graph.edges()))
    graph_str = f"nodes:{nodes}|edges:{edges}"
    return hashlib.sha256(graph_str.encode("utf-8")).hexdigest()


def route_prompt_departments(prompt: str) -> list[str]:
    """Return a deterministic varied department route activated by a prompt."""
    family = classify_workflow_family(prompt)
    
    families = [
        "research_intensive",
        "engineering_intensive",
        "security_incident_response",
        "operations_planning",
        "executive_decision_support",
        "multi_department_compliance",
        "infrastructure_deployment",
        "risk_assessment",
        "financial_planning",
        "ai_governance"
    ]
    family_idx = families.index(family)
    start_idx = family_idx * 6
    end_idx = start_idx + 6
    
    templates = WORKFLOW_TEMPLATES[start_idx:end_idx]
    
    # Hash the prompt to deterministically select a template from the slice
    selector = sum(ord(character) for character in prompt)
    route = templates[selector % len(templates)]["route"]
    
    return list(route)


def contract_department_graph(dept: str, active_nodes: set[str]) -> list[tuple[str, str]]:
    """Contract the department's full internal topology to include only active nodes.
    
    Retains only supervisor and active agents, shortcutting paths through inactive agents.
    """
    g = nx.DiGraph()
    supervisor = DEPARTMENTS[dept]["supervisor"]
    g.add_node(supervisor)
    for agent in DEPARTMENTS[dept]["agents"]:
        g.add_node(agent)
    g.add_edges_from(DEPARTMENTS[dept]["internal_edges"])
    
    # Contract any node that is NOT in active_nodes
    all_dept_nodes = list(g.nodes())
    for node in all_dept_nodes:
        if node not in active_nodes:
            predecessors = list(g.predecessors(node))
            successors = list(g.successors(node))
            for pred in predecessors:
                for succ in successors:
                    if pred != succ:
                        g.add_edge(pred, succ)
            g.remove_node(node)
            
    return list(g.edges())


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
    
    # 1. Classify workflow family and select the specific template
    family = classify_workflow_family(prompt)
    families = [
        "research_intensive",
        "engineering_intensive",
        "security_incident_response",
        "operations_planning",
        "executive_decision_support",
        "multi_department_compliance",
        "infrastructure_deployment",
        "risk_assessment",
        "financial_planning",
        "ai_governance"
    ]
    family_idx = families.index(family)
    start_idx = family_idx * 6
    end_idx = start_idx + 6
    templates = WORKFLOW_TEMPLATES[start_idx:end_idx]
    
    selector = sum(ord(character) for character in prompt)
    template = templates[selector % len(templates)]
    
    # 2. Find mandatory nodes for the route (supervisors and cross-department endpoints)
    mandatory_nodes = set()
    for dept in active_departments:
        mandatory_nodes.add(DEPARTMENTS[dept]["supervisor"])
        
    for source_dept, target_dept in zip(route, route[1:]):
        if source_dept == target_dept:
            continue
        edge = ROUTE_CROSS_DEPARTMENT_EDGES.get((source_dept, target_dept))
        if edge:
            mandatory_nodes.add(edge[0])
            mandatory_nodes.add(edge[1])
            
    # 3. Determine active nodes for each department in the route
    active_nodes = set()
    for dept in active_departments:
        base_roles = template.get("base_roles", {}).get(dept, [])
        dept_active_agents = select_department_roles(prompt, dept, base_roles)
        
        active_nodes.add(DEPARTMENTS[dept]["supervisor"])
        active_nodes.update(dept_active_agents)
        for node in DEPARTMENTS[dept]["agents"]:
            if node in mandatory_nodes:
                active_nodes.add(node)
                
    # 4. Build runtime graph
    runtime_graph = nx.DiGraph()
    runtime_graph.graph["prompt_type"] = classify_prompt(prompt)
    runtime_graph.graph["department_route"] = route
    
    for node in active_nodes:
        if node in static_graph:
            runtime_graph.add_node(node, **static_graph.nodes[node])
            
    # Add active internal edges using contraction
    for department in sorted(active_departments):
        dept_active = {n for n in active_nodes if static_graph.nodes[n].get("department") == department}
        dept_edges = contract_department_graph(department, dept_active)
        runtime_graph.add_edges_from(dept_edges)
                
    # Add active cross-department transition edges
    for source_department, target_department in zip(route, route[1:]):
        if source_department == target_department:
            continue
        route_edge = ROUTE_CROSS_DEPARTMENT_EDGES.get((source_department, target_department))
        if route_edge:
            runtime_graph.add_edge(*route_edge)
            
    return runtime_graph
