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

"""The Verdict: the single result type every gate returns.

A Verdict is deterministic. Given the same candidate and spec, a gate must
always produce an identical Verdict. This is the contract the whole framework
rests on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Verdict:
    """The outcome of a single gate evaluation.

    Attributes:
        passed: True if the candidate cleared the gate.
        gate: Name of the gate that produced this verdict.
        reason: Human-readable explanation of the outcome.
        proof: Structured evidence for the verdict. For a passing formal
            gate this might hold the proof object; for a failing schema gate
            it holds the list of validation errors. Always a plain dict so
            verdicts are serializable and replayable.
    """

    passed: bool
    gate: str
    reason: str = ""
    proof: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for logging and replay."""
        return {
            "passed": self.passed,
            "gate": self.gate,
            "reason": self.reason,
            "proof": self.proof,
        }


@dataclass(frozen=True)
class PipelineResult:
    """The final result of running a candidate through a pipeline.

    Attributes:
        passed: True only if every gate passed.
        verdicts: Ordered list of every Verdict produced, including the
            failing one. Gives a full, replayable trace of the run.
        candidate: The candidate that was evaluated.
        input_hash: Deterministic hash of the candidate, used as the
            idempotency key and replay anchor.
    """

    passed: bool
    verdicts: list[Verdict]
    candidate: Any
    input_hash: str

    @property
    def failed_gate(self) -> str | None:
        """Name of the first gate that failed, or None if all passed."""
        for v in self.verdicts:
            if not v.passed:
                return v.gate
        return None

    @property
    def reason(self) -> str:
        """Reason from the failing gate, or a success message."""
        for v in self.verdicts:
            if not v.passed:
                return v.reason
        return "All gates passed."

    def to_dict(self) -> dict[str, Any]:
        """Serialize the full result for logging and audit."""
        return {
            "passed": self.passed,
            "input_hash": self.input_hash,
            "failed_gate": self.failed_gate,
            "reason": self.reason,
            "verdicts": [v.to_dict() for v in self.verdicts],
        }
