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

"""Determ8: the deterministic gate for agentic systems.

The open core. The agent proposes. The pipeline proves. Same input, same
verdict, every time.

Basic usage:

    from determ8 import Pipeline, SchemaGate, FSMGate, IdempotencyGate

    pipeline = Pipeline(gates=[
        IdempotencyGate(),
        SchemaGate(schema=my_schema),
        FSMGate(transitions=my_workflow),
    ])

    result = pipeline.run(candidate=agent_output)
    if result.passed:
        ship(agent_output)
    else:
        reject(result.reason)
"""

from .core import (
    Gate,
    Pipeline,
    PipelineResult,
    RunLogger,
    Verdict,
    canonical_hash,
)
from .gates import (
    FSMGate,
    GraphGate,
    IdempotencyGate,
    InMemoryStore,
    SchemaGate,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # core
    "Gate",
    "Pipeline",
    "PipelineResult",
    "RunLogger",
    "Verdict",
    "canonical_hash",
    # gates
    "FSMGate",
    "GraphGate",
    "IdempotencyGate",
    "InMemoryStore",
    "SchemaGate",
]
