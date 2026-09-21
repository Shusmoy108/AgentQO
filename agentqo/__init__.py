"""
AgentQO Prototype: Reliability-Aware Joint Logical and Physical Optimization

Runtime optimizer (proposal §V) plus the H1–H4 measurement suite:

- Runtime: joint logical/physical serving (edits + AgentIconq placement + KV + stopping)
- H1: Epistemic criticality varies across workflow nodes
- H2: EC can be predicted cheaply from structure + embeddings
- H3: Spending GPU resources by predicted EC beats uniform allocation
- H4: Two-sided interaction cost model (AgentIconq)

Author: Shusmoy Chowdhury
"""

__version__ = "0.1.0"
