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

"""The Pipeline: the deterministic runner.

A Pipeline holds an ordered list of gates. It pushes a candidate through them
one at a time, stops at the first failure, records every verdict, and returns
a PipelineResult.

Determinism guarantee: the same candidate and the same ordered gate config
always produce the same PipelineResult. Order gates cheap-first, expensive-last
so the pipeline rejects bad candidates as early as possible.
"""

from __future__ import annotations

from typing import Any

from .gate import Gate, canonical_hash
from .logger import RunLogger
from .verdict import PipelineResult, Verdict


class Pipeline:
    """An ordered chain of gates that produces a deterministic verdict.

    Args:
        gates: Gates to run, in order. Put cheap structural gates first and
            expensive proof gates last.
        logger: Optional RunLogger. If omitted, runs are not persisted.
        stop_on_first_failure: If True (default), the pipeline halts at the
            first failing gate. If False, every gate runs and all verdicts are
            collected (useful for reporting all violations at once).
    """

    def __init__(
        self,
        gates: list[Gate],
        logger: RunLogger | None = None,
        stop_on_first_failure: bool = True,
    ) -> None:
        if not gates:
            raise ValueError("A pipeline needs at least one gate.")
        self.gates = gates
        self.logger = logger
        self.stop_on_first_failure = stop_on_first_failure

    def run(self, candidate: Any, spec: Any = None) -> PipelineResult:
        """Evaluate a candidate through every gate in order.

        Args:
            candidate: The agent's proposed output.
            spec: The specification passed to each gate. May be a single
                object shared by all gates, or a dict keyed by gate name so
                each gate gets its own spec.

        Returns:
            A PipelineResult with the overall verdict and a full trace.
        """
        verdicts: list[Verdict] = []
        all_passed = True

        for gate in self.gates:
            gate_spec = self._spec_for(gate, spec)
            verdict = gate.evaluate(candidate, gate_spec)
            verdicts.append(verdict)
            if not verdict.passed:
                all_passed = False
                if self.stop_on_first_failure:
                    break

        result = PipelineResult(
            passed=all_passed,
            verdicts=verdicts,
            candidate=candidate,
            input_hash=canonical_hash(candidate),
        )

        if self.logger is not None:
            self.logger.record(result)

        return result

    @staticmethod
    def _spec_for(gate: Gate, spec: Any) -> Any:
        """Resolve the spec for one gate.

        If spec is a dict containing the gate's name as a key, that entry is
        used. Otherwise the whole spec object is passed through.
        """
        if isinstance(spec, dict) and gate.name in spec:
            return spec[gate.name]
        return spec
