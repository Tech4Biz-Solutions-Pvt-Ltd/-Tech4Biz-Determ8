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

"""Tests for the four free gates."""

from determ8 import FSMGate, GraphGate, IdempotencyGate, SchemaGate


# --- SchemaGate ---------------------------------------------------------

LOAN_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {"enum": ["approve", "reject", "escalate"]},
        "amount": {"type": "number"},
    },
    "required": ["decision", "amount"],
}


def test_schema_pass():
    g = SchemaGate(schema=LOAN_SCHEMA)
    v = g.check({"decision": "approve", "amount": 1000}, None)
    assert v.passed


def test_schema_fail_wrong_enum():
    g = SchemaGate(schema=LOAN_SCHEMA)
    v = g.check({"decision": "maybe", "amount": 1000}, None)
    assert not v.passed
    assert v.proof["errors"]


def test_schema_fail_missing_field():
    g = SchemaGate(schema=LOAN_SCHEMA)
    v = g.check({"decision": "approve"}, None)
    assert not v.passed


def test_schema_deterministic_error_order():
    g = SchemaGate(schema=LOAN_SCHEMA)
    bad = {"decision": "maybe"}
    assert g.check(bad, None).proof == g.check(bad, None).proof


# --- FSMGate ------------------------------------------------------------

WORKFLOW = {
    "transitions": {
        "verify_identity": ["check_credit"],
        "check_credit": ["decide"],
        "decide": [],
    },
    "start": "verify_identity",
    "accept": ["decide"],
}


def test_fsm_legal_sequence():
    g = FSMGate()
    cand = {"states": ["verify_identity", "check_credit", "decide"]}
    assert g.check(cand, WORKFLOW).passed


def test_fsm_illegal_jump():
    g = FSMGate()
    cand = {"states": ["verify_identity", "decide"]}
    v = g.check(cand, WORKFLOW)
    assert not v.passed
    assert "Illegal transition" in v.reason


def test_fsm_wrong_start():
    g = FSMGate()
    cand = {"states": ["check_credit", "decide"]}
    assert not g.check(cand, WORKFLOW).passed


def test_fsm_non_accepting_end():
    g = FSMGate()
    cand = {"states": ["verify_identity", "check_credit"]}
    assert not g.check(cand, WORKFLOW).passed


# --- IdempotencyGate ----------------------------------------------------

def test_idempotency_first_seen_passes():
    g = IdempotencyGate()
    assert g.check({"id": 1}, None).passed


def test_idempotency_duplicate_fails():
    g = IdempotencyGate()
    g.check({"id": 1}, None)
    assert not g.check({"id": 1}, None).passed


def test_idempotency_different_inputs_both_pass():
    g = IdempotencyGate()
    assert g.check({"id": 1}, None).passed
    assert g.check({"id": 2}, None).passed


# --- GraphGate ----------------------------------------------------------

def test_graph_acyclic_passes():
    g = GraphGate()
    cand = {"dependencies": {"b": ["a"], "c": ["b"], "a": []}}
    assert g.check(cand, None).passed


def test_graph_cycle_fails():
    g = GraphGate()
    cand = {"dependencies": {"a": ["b"], "b": ["a"]}}
    v = g.check(cand, None)
    assert not v.passed
    assert v.proof["cycle"]


def test_graph_bad_order_fails():
    g = GraphGate()
    cand = {"dependencies": {"b": ["a"], "a": []}, "order": ["b", "a"]}
    v = g.check(cand, None)
    assert not v.passed
    assert v.proof["missing_dependency"] == "a"


def test_graph_good_order_passes():
    g = GraphGate()
    cand = {"dependencies": {"b": ["a"], "a": []}, "order": ["a", "b"]}
    assert g.check(cand, None).passed


def test_graph_absent_map_passes():
    # No dependency graph to judge means nothing to violate.
    g = GraphGate()
    assert g.check({"decision": "approve"}, None).passed
