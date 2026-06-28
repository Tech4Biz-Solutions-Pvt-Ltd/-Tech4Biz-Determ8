# ---------------------------------------------------------------------------
# Determ8 - The deterministic gate for agentic systems.
#
# Copyright (c) 2026 Tech4Biz Solutions. All rights reserved.
#
# This file is part of the Determ8 open core, released under the Apache
# License, Version 2.0. See the LICENSE file in the project root for terms.
#
# Determ8 (TM) and Tech4Biz Solutions (TM) are trademarks of Tech4Biz Solutions.
# The agent proposes. The pipeline proves.
#
# Determ8 Pro (formal verification, domain rule packs, audit-grade replay) is a
# commercial product and is NOT included in this file. Contact: contact@tech4biz.io
# ---------------------------------------------------------------------------

"""Graph Gate.

Question it answers: are the agent's planned tasks in a valid order with no
cycles?

When an agent produces a plan of tasks with dependencies, that plan must form
a Directed Acyclic Graph. This gate detects cycles and, if an execution order
is given, verifies every task runs only after its dependencies. Pure graph
algorithms, fully deterministic.
"""

from __future__ import annotations

from typing import Any

from ..core.gate import Gate
from ..core.verdict import Verdict


class GraphGate(Gate):
    """Validate a task dependency graph is acyclic and correctly ordered.

    The candidate is expected to provide a dependency map and, optionally, a
    proposed execution order. By default the gate reads:
        - candidate["dependencies"]: {task: [tasks it depends on]}
        - candidate["order"]: optional list giving execution order

    Override the keys via the constructor.

    Args:
        deps_key: Candidate key holding the dependency map.
        order_key: Candidate key holding the proposed execution order.
    """

    name = "graph"

    def __init__(self, deps_key: str = "dependencies", order_key: str = "order") -> None:
        self.deps_key = deps_key
        self.order_key = order_key

    def check(self, candidate: Any, spec: Any) -> Verdict:
        if not isinstance(candidate, dict) or self.deps_key not in candidate:
            # No graph to judge. A gate only rules on what the candidate
            # actually provides, so an absent graph is a clean pass.
            return Verdict(
                passed=True,
                gate=self.name,
                reason=f"No '{self.deps_key}' map present; nothing to validate.",
            )

        deps: dict[str, list[str]] = candidate[self.deps_key]

        cycle = self._find_cycle(deps)
        if cycle is not None:
            return Verdict(
                passed=False,
                gate=self.name,
                reason=f"Dependency cycle detected: {' -> '.join(cycle)}.",
                proof={"cycle": cycle},
            )

        order = candidate.get(self.order_key)
        if order is not None:
            violation = self._check_order(deps, order)
            if violation is not None:
                task, missing = violation
                return Verdict(
                    passed=False,
                    gate=self.name,
                    reason=(
                        f"Task '{task}' runs before its dependency '{missing}'."
                    ),
                    proof={"order": order, "task": task, "missing_dependency": missing},
                )

        return Verdict(
            passed=True,
            gate=self.name,
            reason="Graph is acyclic and ordering is valid.",
        )

    @staticmethod
    def _find_cycle(deps: dict[str, list[str]]) -> list[str] | None:
        """Return a cycle as a list of nodes, or None if the graph is acyclic.

        Depth-first search with deterministic node ordering so the same graph
        always reports the same cycle.
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {}
        nodes = sorted(set(deps) | {d for ds in deps.values() for d in ds})
        for n in nodes:
            color[n] = WHITE

        path: list[str] = []

        def visit(node: str) -> list[str] | None:
            color[node] = GRAY
            path.append(node)
            for nxt in sorted(deps.get(node, [])):
                if color[nxt] == GRAY:
                    idx = path.index(nxt)
                    return path[idx:] + [nxt]
                if color[nxt] == WHITE:
                    found = visit(nxt)
                    if found is not None:
                        return found
            color[node] = BLACK
            path.pop()
            return None

        for n in nodes:
            if color[n] == WHITE:
                found = visit(n)
                if found is not None:
                    return found
        return None

    @staticmethod
    def _check_order(
        deps: dict[str, list[str]], order: list[str]
    ) -> tuple[str, str] | None:
        """Verify each task appears after all its dependencies.

        Returns (task, missing_dependency) for the first violation, or None.
        """
        position = {task: i for i, task in enumerate(order)}
        for task in order:
            for dep in deps.get(task, []):
                if dep not in position or position[dep] > position[task]:
                    return (task, dep)
        return None
