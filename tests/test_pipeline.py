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

"""Tests for the core contract, runner, and determinism guarantee."""

from determ8 import Gate, Pipeline, Verdict, canonical_hash


class AlwaysPass(Gate):
    name = "always_pass"

    def check(self, candidate, spec):
        return Verdict(passed=True, gate=self.name, reason="ok")


class AlwaysFail(Gate):
    name = "always_fail"

    def check(self, candidate, spec):
        return Verdict(passed=False, gate=self.name, reason="nope")


class Exploding(Gate):
    name = "exploding"

    def check(self, candidate, spec):
        raise RuntimeError("boom")


def test_all_pass():
    result = Pipeline([AlwaysPass(), AlwaysPass()]).run({"x": 1})
    assert result.passed
    assert result.failed_gate is None
    assert len(result.verdicts) == 2


def test_stops_on_first_failure():
    result = Pipeline([AlwaysPass(), AlwaysFail(), AlwaysPass()]).run({"x": 1})
    assert not result.passed
    assert result.failed_gate == "always_fail"
    # third gate never ran
    assert len(result.verdicts) == 2


def test_collect_all_failures():
    result = Pipeline(
        [AlwaysFail(), AlwaysFail()], stop_on_first_failure=False
    ).run({"x": 1})
    assert not result.passed
    assert len(result.verdicts) == 2


def test_gate_exception_becomes_failure():
    result = Pipeline([Exploding()]).run({"x": 1})
    assert not result.passed
    assert "boom" in result.reason


def test_empty_pipeline_rejected():
    try:
        Pipeline([])
    except ValueError:
        return
    raise AssertionError("empty pipeline should raise")


def test_determinism_same_input_same_result():
    p = Pipeline([AlwaysPass()])
    r1 = p.run({"a": 1, "b": 2})
    r2 = p.run({"b": 2, "a": 1})  # same data, different key order
    assert r1.input_hash == r2.input_hash
    assert r1.to_dict() == r2.to_dict()


def test_canonical_hash_is_order_independent():
    assert canonical_hash({"a": 1, "b": 2}) == canonical_hash({"b": 2, "a": 1})
    assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})
