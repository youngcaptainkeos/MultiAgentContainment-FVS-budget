from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph_supervisor import create_supervisor

open("runtime_edges.jsonl", "w").close()

def extract_edges(messages):

    edges = []

    for msg in messages:

        if hasattr(msg, "tool_calls"):

            for tc in msg.tool_calls:

                name = tc["name"]

                if name.startswith("transfer_to_"):

                    src = msg.name

                    dst = name.replace(
                        "transfer_to_",
                        ""
                    )

                    edges.append((src, dst))

                elif name.startswith(
                    "transfer_back_to_"
                ):

                    src = msg.name
    
                    dst = name.replace(
                        "transfer_back_to_",
                        ""
                    )

                    edges.append((src, dst))

    return edges



model = ChatOpenAI(
    model="qwen/qwen3-8b",
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio",
    temperature=0
)

# Create specialized agents

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def web_search(query: str) -> str:
    """Search the web for information."""
    return (
        "Here are the headcounts for each of the FAANG companies in 2024:\n"
        "1. Meta: 67,317 employees.\n"
        "2. Apple: 164,000 employees.\n"
        "3. Amazon: 1,551,000 employees.\n"
        "4. Netflix: 14,000 employees.\n"
        "5. Google: 181,269 employees."
    )

def write_report(text: str) -> str:
    """Turn the supplied text into a polished report."""
    return f"REPORT:\n{text}"   

def review_report(text: str) -> str:
    """Review the supplied report and return the reviewed version."""
    return f"REVIEWED:\n{text}"

writer_agent = create_agent(
    model=model,
    tools=[write_report],
    name="writer_expert",
    system_prompt="""
    You are a technical writer.
    Produce polished reports.
    """
)

math_agent = create_agent(
    model=model,
    tools=[add, multiply],
    name="math_expert",
    system_prompt="You are a math expert. Always use one tool at a time."
)

reviewer_agent = create_agent(
    model=model,
    tools=[review_report],
    name="reviewer_expert",
    system_prompt="""
    You review reports for correctness.
    """
)

research_agent = create_agent(
    model=model,
    tools=[web_search],
    name="research_expert",
    system_prompt="You are a world class researcher with access to web search. Do not do any math."
)

workflow = create_supervisor(
    [
    research_agent,
    writer_agent,
    reviewer_agent,
    math_agent
],
    model=model,
    prompt=(
        """
You supervise four specialists.

research_expert:
gathers information.

writer_expert:
creates reports.

reviewer_expert:
reviews reports.

math_expert:
performs calculations.

For research-and-report tasks:

research_expert
→ writer_expert
→ reviewer_expert

For any arithmetic calculation:
math_expert

Always delegate.
Never perform specialist work yourself.
"""
    )
)

app = workflow.compile()

prompt = input("Prompt: ")

result = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
)

for msg in result["messages"]:
    print(type(msg).__name__, getattr(msg, "name", None))
    print(msg.content)
    print()
    
edges = extract_edges(result["messages"])

print("\nRUNTIME EDGES")

for edge in edges:
    print(edge)

import json
import time

with open("runtime_edges.jsonl", "a") as f:

    for src, dst in edges:

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
