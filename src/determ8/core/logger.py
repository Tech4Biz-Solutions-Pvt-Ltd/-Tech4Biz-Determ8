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

"""Structured, replayable logging.

Every pipeline run emits one append-only JSON record per run. The record is
fully deterministic given the same input and gate config, so any run can be
replayed and audited. The free tier logs to JSONL on disk; the paid Audit
Gate adds cryptographic signing and Merkle chaining on top of this.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .verdict import PipelineResult


class RunLogger:
    """Append-only JSONL logger for pipeline runs.

    Args:
        path: File to append records to. If None, logging is disabled and
            records are kept in memory only (useful for tests).
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self.records: list[dict] = []

    def record(self, result: "PipelineResult") -> None:
        """Append one pipeline result as a structured record."""
        entry = result.to_dict()
        self.records.append(entry)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, sort_keys=True) + "\n")
