import json
import time

infected_agents = []
REVOKED = {"researcher"}

open("runtime_edges.jsonl", "w").close()

def log_edge(src, dst):
    with open("runtime_edges.jsonl", "a") as f:
        f.write(
            json.dumps(
                {
                    "source": src,
                    "target": dst,
                    "timestamp": time.time()
                }
            )
            + "\n"
        )

def researcher(state):

    if "researcher" in REVOKED:

        print("Researcher revoked.")
        return None

    log_edge("researcher", "writer")

    return {
        "text":
        "[POISON] Apple has 12 employees."
    }

def writer(state):

    if "[POISON]" in state["text"]:
        infected_agents.append("writer")

    log_edge("writer", "reviewer")

    return {
        "text":
        f"REPORT: {state['text']}"
    }

def reviewer(state):

    if "[POISON]" in state["text"]:
        infected_agents.append("reviewer")

    log_edge("reviewer", "researcher")

    return {
        "text":
        f"REVIEWED: {state['text']}"
    }

def math_agent(state):
    log_edge("math", "END")

    return {
        "text":
        f"{state['text']} DOUBLE=328000"
    }

state = {}

state = researcher(state)

if state is not None:

    state = writer(state)

    state = reviewer(state)

print()

print("Infected Agents:")
print(infected_agents)

print()

print("K =", len(infected_agents))  

if state is None:
    print("Workflow stopped: researcher is revoked.")
else:
    print(state["text"])

