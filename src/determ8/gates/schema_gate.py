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

"""Schema Gate.

Question it answers: is the candidate the exact shape the next system expects?

The cheapest gate. Validates a candidate against a JSON Schema. Anything that
does not match the declared structure is rejected before any expensive gate
runs. This is almost always the first gate in a pipeline.
"""

from __future__ import annotations

from typing import Any

from ..core.gate import Gate
from ..core.verdict import Verdict

try:
    import jsonschema
    from jsonschema import Draft7Validator

    _HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover - exercised only without the extra
    _HAS_JSONSCHEMA = False


class SchemaGate(Gate):
    """Validate a candidate against a JSON Schema.

    The spec for this gate is a JSON Schema dict. Validation is deterministic:
    errors are sorted by path so the same candidate always yields the same
    ordered error list.

    Args:
        schema: Optional default schema. If given, it is used whenever the
            pipeline does not pass a per-gate spec.
    """

    name = "schema"

    def __init__(self, schema: dict | None = None) -> None:
        if not _HAS_JSONSCHEMA:
            raise ImportError(
                "SchemaGate requires jsonschema. Install with: pip install determ8[schema]"
            )
        self.schema = schema

    def check(self, candidate: Any, spec: Any) -> Verdict:
        schema = spec if spec is not None else self.schema
        if schema is None:
            return Verdict(
                passed=False,
                gate=self.name,
                reason="No schema provided to SchemaGate.",
            )

        validator = Draft7Validator(schema)
        errors = sorted(
            validator.iter_errors(candidate),
            key=lambda e: (list(e.absolute_path), e.message),
        )

        if not errors:
            return Verdict(
                passed=True,
                gate=self.name,
                reason="Candidate matches schema.",
            )

        messages = [
            {"path": list(e.absolute_path), "message": e.message} for e in errors
        ]
        return Verdict(
            passed=False,
            gate=self.name,
            reason=f"Candidate failed schema validation: {len(messages)} error(s).",
            proof={"errors": messages},
        )
