"""Feedback vertex set analysis for small directed runtime graphs."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import networkx as nx


def is_fvs(graph: nx.DiGraph, nodes_to_remove: tuple[str, ...]) -> bool:
    """Return whether removing the supplied nodes makes the graph acyclic."""
    reduced_graph = graph.copy()
    reduced_graph.remove_nodes_from(nodes_to_remove)
    return nx.is_directed_acyclic_graph(reduced_graph)


def compute_fvs(graph: nx.DiGraph) -> tuple[int, list[str]]:
    """Find an exact minimum directed feedback vertex set by exhaustive search."""
    if nx.is_directed_acyclic_graph(graph):
        return 0, []

    # NetworkX preserves insertion order, making ties deterministic for a fixed trace.
    nodes = list(graph.nodes())
    for size in range(1, len(nodes) + 1):
        for subset in itertools.combinations(nodes, size):
            if is_fvs(graph, subset):
                return size, list(subset)

    raise RuntimeError("Unable to find an FVS for the supplied graph")


def load_jsonl_graph(path: str | Path) -> nx.DiGraph:
    """Build a directed graph from a JSONL runtime edge log."""
    graph = nx.DiGraph()
    with Path(path).open(encoding="utf-8") as log_file:
        for line in log_file:
            if line.strip():
                edge = json.loads(line)
                graph.add_edge(edge["source"], edge["target"])
    return graph


if __name__ == "__main__":
    runtime_graph = load_jsonl_graph("runtime_edges.jsonl")
    cycles = list(nx.simple_cycles(runtime_graph))
    tau_runtime, fvs_nodes = compute_fvs(runtime_graph)

    print("Nodes:")
    print(list(runtime_graph.nodes()))
    print("\nEdges:")
    print(list(runtime_graph.edges()))
    print("\nCycles:")
    print(cycles)
    print("\nRuntime tau_FVS =", tau_runtime)
    print("FVS =", fvs_nodes)
