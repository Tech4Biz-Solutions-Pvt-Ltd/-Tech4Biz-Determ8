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

"""The Gate contract.

Every gate in Determ8, free or paid, implements this one interface. A gate
takes a candidate (the agent's proposed output) and a spec (what correctness
means for this step), and returns a Verdict: pass or fail, with a reason and
proof.

The rule that makes the framework deterministic: a gate MUST be a pure
function of (candidate, spec). No clocks, no randomness, no hidden state.
Same inputs, same Verdict, every time.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any

from .verdict import Verdict


class Gate(ABC):
    """Abstract base class for all gates.

    Subclasses implement `check`. The framework calls `evaluate`, which wraps
    `check` so every gate reports failures the same way instead of raising.
    """

    #: Stable, human-readable name. Used in verdicts, logs, and config.
    name: str = "gate"

    @abstractmethod
    def check(self, candidate: Any, spec: Any) -> Verdict:
        """Evaluate the candidate against the spec.

        Must be a pure function of its inputs. Implementations return a
        Verdict; they should not raise for ordinary validation failures.

        Args:
            candidate: The agent's proposed output.
            spec: The correctness specification for this gate.

        Returns:
            A Verdict describing pass or fail.
        """
        raise NotImplementedError

    def evaluate(self, candidate: Any, spec: Any) -> Verdict:
        """Run `check` and convert any unexpected error into a failing Verdict.

        This keeps the pipeline deterministic and crash-free: a buggy or
        defensive gate produces a clean failure rather than tearing down the
        whole run.
        """
        try:
            return self.check(candidate, spec)
        except Exception as exc:  # noqa: BLE001 - we deliberately catch all
            return Verdict(
                passed=False,
                gate=self.name,
                reason=f"Gate raised an error: {type(exc).__name__}: {exc}",
                proof={"error_type": type(exc).__name__},
            )


def canonical_hash(candidate: Any) -> str:
    """Deterministic SHA-256 hash of any JSON-serializable candidate.

    Keys are sorted and whitespace is normalized so logically equal inputs
    always hash to the same value. This is the idempotency key and the replay
    anchor for the whole pipeline.
    """
    try:
        serialized = json.dumps(candidate, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError):
        serialized = repr(candidate)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
