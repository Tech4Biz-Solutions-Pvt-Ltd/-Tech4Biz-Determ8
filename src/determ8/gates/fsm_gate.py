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

"""Finite State Machine Gate.

Question it answers: did the agent move through its steps in a legal order?

Many agent workflows must follow a fixed sequence: verify identity, then check
credit, then decide. This gate takes the sequence of states the agent actually
visited and checks every transition against an allowed-transition map. Any
illegal jump is rejected deterministically.
"""

from __future__ import annotations

from typing import Any

from ..core.gate import Gate
from ..core.verdict import Verdict


class FSMGate(Gate):
    """Validate a sequence of states against an allowed-transition map.

    The spec is a dict with:
        - "transitions": mapping of state -> list of states reachable from it.
        - "start": the required first state (optional).
        - "accept": list of valid final states (optional).

    The candidate is expected to expose its visited states. By default the gate
    reads candidate["states"]; override `state_key` to read a different field.

    Args:
        transitions: Optional default transition map.
        start: Optional required start state.
        accept: Optional list of valid end states.
        state_key: Key under which the candidate stores its visited states.
    """

    name = "fsm"

    def __init__(
        self,
        transitions: dict[str, list[str]] | None = None,
        start: str | None = None,
        accept: list[str] | None = None,
        state_key: str = "states",
    ) -> None:
        self.transitions = transitions
        self.start = start
        self.accept = accept
        self.state_key = state_key

    def check(self, candidate: Any, spec: Any) -> Verdict:
        cfg = spec if isinstance(spec, dict) else {}
        transitions = cfg.get("transitions", self.transitions)
        start = cfg.get("start", self.start)
        accept = cfg.get("accept", self.accept)

        if transitions is None:
            return Verdict(
                passed=False,
                gate=self.name,
                reason="No transition map provided to FSMGate.",
            )

        states = self._extract_states(candidate)
        if states is None:
            return Verdict(
                passed=False,
                gate=self.name,
                reason=f"Candidate has no '{self.state_key}' sequence to validate.",
            )
        if not states:
            return Verdict(
                passed=False,
                gate=self.name,
                reason="State sequence is empty.",
            )

        if start is not None and states[0] != start:
            return Verdict(
                passed=False,
                gate=self.name,
                reason=f"Sequence must start at '{start}', started at '{states[0]}'.",
                proof={"states": states},
            )

        for i in range(len(states) - 1):
            src, dst = states[i], states[i + 1]
            allowed = transitions.get(src, [])
            if dst not in allowed:
                return Verdict(
                    passed=False,
                    gate=self.name,
                    reason=f"Illegal transition '{src}' -> '{dst}'.",
                    proof={"states": states, "at_index": i},
                )

        if accept is not None and states[-1] not in accept:
            return Verdict(
                passed=False,
                gate=self.name,
                reason=f"Sequence ended at '{states[-1]}', not an accepting state.",
                proof={"states": states, "accept": accept},
            )

        return Verdict(
            passed=True,
            gate=self.name,
            reason="All transitions are legal.",
            proof={"states": states},
        )

    def _extract_states(self, candidate: Any) -> list[str] | None:
        if isinstance(candidate, dict):
            states = candidate.get(self.state_key)
            if isinstance(states, list):
                return [str(s) for s in states]
        return None
