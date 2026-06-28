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

"""Loan eligibility agent: a complete, runnable Determ8 example.

A bank's agent reads a loan application and proposes a decision. Determ8 gates
that decision through the four free structural gates before it can ship.

Run it:

    python examples/loan_agent.py
"""

from determ8 import (
    FSMGate,
    GraphGate,
    IdempotencyGate,
    Pipeline,
    RunLogger,
    SchemaGate,
)

# 1. What a valid decision must look like.
DECISION_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {"enum": ["approve", "reject", "escalate"]},
        "amount": {"type": "number", "minimum": 0},
        "states": {"type": "array", "items": {"type": "string"}},
        "dependencies": {"type": "object"},
        "order": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["decision", "amount", "states"],
}

# 2. The legal order of operations for the agent.
WORKFLOW = {
    "transitions": {
        "verify_identity": ["check_credit"],
        "check_credit": ["assess_risk"],
        "assess_risk": ["decide"],
        "decide": [],
    },
    "start": "verify_identity",
    "accept": ["decide"],
}


def build_pipeline() -> Pipeline:
    """Assemble the deterministic pipeline. Cheap gates first."""
    return Pipeline(
        gates=[
            IdempotencyGate(),
            SchemaGate(schema=DECISION_SCHEMA),
            FSMGate(transitions=WORKFLOW["transitions"], start="verify_identity",
                    accept=["decide"]),
            GraphGate(),
        ],
        logger=RunLogger("runs.jsonl"),
    )


def run(label: str, candidate: dict) -> None:
    pipeline = build_pipeline()
    result = pipeline.run(candidate)
    status = "PASS" if result.passed else "FAIL"
    print(f"[{status}] {label}")
    if not result.passed:
        print(f"        blocked by '{result.failed_gate}': {result.reason}")
    print(f"        input hash: {result.input_hash[:16]}...")
    print()


if __name__ == "__main__":
    # A clean, well-formed decision that followed the legal sequence.
    good = {
        "decision": "approve",
        "amount": 25000,
        "states": ["verify_identity", "check_credit", "assess_risk", "decide"],
        "dependencies": {
            "check_credit": ["verify_identity"],
            "assess_risk": ["check_credit"],
            "decide": ["assess_risk"],
            "verify_identity": [],
        },
        "order": ["verify_identity", "check_credit", "assess_risk", "decide"],
    }
    run("Well-formed approval", good)

    # The agent skipped the credit check. FSM gate catches it.
    skipped = {
        "decision": "approve",
        "amount": 25000,
        "states": ["verify_identity", "decide"],
    }
    run("Skipped credit check", skipped)

    # Malformed decision value. Schema gate catches it.
    malformed = {
        "decision": "probably yes",
        "amount": 25000,
        "states": ["verify_identity", "check_credit", "assess_risk", "decide"],
    }
    run("Malformed decision", malformed)

    # The exact same request twice. Idempotency gate catches the second.
    print("Submitting the same application twice:")
    pipeline = build_pipeline()
    twice = {
        "decision": "approve",
        "amount": 9000,
        "states": ["verify_identity", "check_credit", "assess_risk", "decide"],
    }
    r1 = pipeline.run(twice)
    r2 = pipeline.run(twice)
    print(f"        first:  {'PASS' if r1.passed else 'FAIL'}")
    print(f"        second: {'PASS' if r2.passed else 'FAIL'} "
          f"({r2.reason if not r2.passed else ''})")
