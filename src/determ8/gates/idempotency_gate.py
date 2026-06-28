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

"""Idempotency Gate.

Question it answers: has this exact request already been processed?

Hashes the candidate deterministically and checks it against a store of seen
hashes. On first sight the hash is recorded and the gate passes. On a repeat
the gate reports the duplicate so the caller can return the cached result
instead of running side effects (a payment, a write) twice.

The free tier ships an in-memory store. Swap in any object implementing the
Store protocol (Redis, a database) for production.
"""

from __future__ import annotations

from typing import Any, Protocol

from ..core.gate import Gate, canonical_hash
from ..core.verdict import Verdict


class Store(Protocol):
    """Minimal interface an idempotency store must implement."""

    def has(self, key: str) -> bool: ...

    def add(self, key: str) -> None: ...


class InMemoryStore:
    """A simple in-process set-backed store. Not shared across processes."""

    def __init__(self) -> None:
        self._seen: set[str] = set()

    def has(self, key: str) -> bool:
        return key in self._seen

    def add(self, key: str) -> None:
        self._seen.add(key)


class IdempotencyGate(Gate):
    """Reject a candidate that has already been seen.

    Args:
        store: Backing store for seen hashes. Defaults to an in-memory store.
        record_on_pass: If True (default), a newly seen hash is recorded so the
            next identical candidate is caught. Set False for a pure read-only
            check.
    """

    name = "idempotency"

    def __init__(self, store: Store | None = None, record_on_pass: bool = True) -> None:
        self.store = store if store is not None else InMemoryStore()
        self.record_on_pass = record_on_pass

    def check(self, candidate: Any, spec: Any) -> Verdict:
        key = canonical_hash(candidate)

        if self.store.has(key):
            return Verdict(
                passed=False,
                gate=self.name,
                reason="Duplicate request: this candidate was already processed.",
                proof={"input_hash": key},
            )

        if self.record_on_pass:
            self.store.add(key)

        return Verdict(
            passed=True,
            gate=self.name,
            reason="First time this candidate has been seen.",
            proof={"input_hash": key},
        )
