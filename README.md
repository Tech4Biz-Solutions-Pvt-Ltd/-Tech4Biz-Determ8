<div align="center">

# Determ8

### The deterministic gate for agentic systems.

**The agent proposes. The pipeline proves. Same input, same verdict, every time.**

*by [Tech4Biz Solutions](mailto:contact@tech4biz.io)*

</div>

---

## The problem

AI agents are probabilistic. Ask the same question twice, you can get two answers. That is fine for a chatbot. It is unacceptable for a loan decision, a medical claim, a payment, or any regulated workflow.

Enterprises will not put agents into production where "usually right" is the only guarantee.

Determ8 fixes this. It wraps a probabilistic model in a **deterministic pipeline**. The model stays probabilistic. The correctness layer around it is pure algorithm. The agent proposes a candidate answer. The pipeline proves it or rejects it. The same input always produces the same verdict.

---

## How it works

![Determ8 architecture](docs/assets/architecture.svg)

A request comes in. The agent proposes a candidate. That candidate is **not trusted yet**. It enters the pipeline and passes through a series of gates, one at a time. Each gate answers exactly one question deterministically: pass or fail. Cheap gates run first. Expensive gates run last. The moment a gate fails, the pipeline stops and rejects the candidate. Only a candidate that clears every gate is shipped, and every run is logged so it can be replayed and audited.

The whole framework rests on **one contract**. Every gate, free or paid, implements the same interface:

```python
gate(candidate, spec) -> Verdict(passed, reason, proof)
```

Because every gate looks the same to the pipeline, you add gates one at a time, configure which run per project, and even write your own. The determinism guarantee is simple: **same input plus same gate config produces the same verdict, always.**

---

## One contract, two tiers

![Free vs Pro gates](docs/assets/tiers.svg)

Determ8 is **open core**. The free tier is a real, working deterministic pipeline. The paid tier adds the formal proof and compliance that regulated industries cannot ship without.

### Free (this repository)

| Gate | Question it answers | Algorithm |
|------|--------------------|-----------|
| **Schema Gate** | Is the output the exact required shape? | JSON Schema |
| **FSM Gate** | Did the agent follow the steps in legal order? | Finite state machine |
| **Idempotency Gate** | Did this exact request already run? | SHA-256 hashing |
| **Graph Gate** | Are tasks in valid order with no cycles? | DAG validation, topological sort |

Everything you need to wire up a deterministic pipeline, run it end to end, and trust the pattern.

### Determ8 Pro (commercial)

The hard, defensible gates. This is what banks, hospitals, and insurers pay for.

| Gate | What you get | Why it matters |
|------|-------------|----------------|
| **Formal Verification Gate** | Z3 / SMT solver proves the output is mathematically equivalent to the spec | Not "looks right", but *provably* right. Code generation, financial math, eligibility logic. |
| **Rule Engine + Domain Packs** | Prebuilt, maintained rule sets for banking, healthcare, insurance, KYC, and compliance | Stop hand-coding regulation. Drop in a pack that already encodes the policy. |
| **Constraint Gate** | Constraint solver validates that every number, limit, and relationship holds together | Catches the impossible combination a schema check never could. |
| **Audit Gate** | Cryptographically signed, Merkle-chained, regulator-grade replay of every decision | Prove to an auditor that nothing was altered. Turn incidents into forensics. |

**Determ8 Pro also includes** multi-agent orchestration across gates, managed hosting, support, and SLAs.

> **Free gets you a pipeline that runs. Pro gets you a pipeline a regulator will accept.**

Pricing, licensing, and full source: **contact@tech4biz.io**

---

## Install

```bash
pip install determ8
```

The Schema Gate needs the `jsonschema` extra:

```bash
pip install "determ8[schema]"
```

Requires Python 3.10 or newer.

---

## Quick start

Three gates, end to end. This runs as-is.

```python
from determ8 import Pipeline, SchemaGate, FSMGate, IdempotencyGate

# 1. Declare what a valid answer looks like.
schema = {
    "type": "object",
    "properties": {
        "decision": {"enum": ["approve", "reject", "escalate"]},
        "amount": {"type": "number", "minimum": 0},
        "states": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["decision", "amount", "states"],
}

# 2. Declare the legal order of steps the agent must follow.
workflow = {
    "verify_identity": ["check_credit"],
    "check_credit": ["decide"],
    "decide": [],
}

# 3. Build the pipeline. Cheap gates first.
pipeline = Pipeline(gates=[
    IdempotencyGate(),
    SchemaGate(schema=schema),
    FSMGate(transitions=workflow, start="verify_identity", accept=["decide"]),
])

# 4. Gate whatever the agent proposed.
agent_output = {
    "decision": "approve",
    "amount": 25000,
    "states": ["verify_identity", "check_credit", "decide"],
}

result = pipeline.run(agent_output)

if result.passed:
    print("Verified. Safe to act on.")
else:
    print(f"Blocked by '{result.failed_gate}' gate: {result.reason}")
```

The agent guesses. The pipeline proves. You never ship a guess, only a proven answer.

---

## Using Determ8 in your project

You never edit the library. You give it your rules. There are three ways to do that.

### 1. Configure the built-in gates

The most common path. Pass your own schema, workflow, and limits as arguments. Your rules live in your code; Determ8 enforces them.

```python
from determ8 import Pipeline, SchemaGate, FSMGate

pipeline = Pipeline(gates=[
    SchemaGate(schema=my_schema),
    FSMGate(transitions=my_workflow, start="start", accept=["done"]),
])
```

### 2. Write your own gate

For logic the built-ins do not cover, implement the same `Gate` contract in your own project and drop it into the pipeline like any built-in. This is why the single contract matters: anyone extends Determ8 without touching its source.

```python
from determ8 import Gate, Verdict

class AmountCeilingGate(Gate):
    name = "amount_ceiling"

    def check(self, candidate, spec):
        limit = spec or 5000
        amount = candidate.get("amount", 0)
        if amount <= limit:
            return Verdict(passed=True, gate=self.name, reason="within limit")
        return Verdict(
            passed=False,
            gate=self.name,
            reason=f"amount {amount} exceeds limit {limit}",
            proof={"amount": amount, "limit": limit},
        )

# use it exactly like a built-in gate
from determ8 import Pipeline
pipeline = Pipeline(gates=[AmountCeilingGate()])
print(pipeline.run({"amount": 9000}, spec=5000).reason)
```

A gate must be a **pure function of `(candidate, spec)`**: no clocks, no randomness, no hidden state. That is what keeps the pipeline deterministic.

### 3. Buy a Pro gate

For formal proofs, domain rule packs, and audit trails, install `determ8-pro` and plug those gates in the same way. Same pipeline, same contract. Contact **contact@tech4biz.io**.

---

## Reading the result

`pipeline.run()` returns a `PipelineResult`:

```python
result = pipeline.run(agent_output)

result.passed        # True only if every gate passed
result.failed_gate   # name of the first gate that failed, or None
result.reason        # why it failed, or a success message
result.input_hash    # deterministic SHA-256 of the candidate
result.verdicts      # the full ordered trace, one Verdict per gate run
result.to_dict()     # serializable record, ready for logging or audit
```

Each `Verdict` in the trace carries `passed`, `gate`, `reason`, and a structured `proof` dict (the schema errors, the illegal transition, the detected cycle, and so on).

---

## Per-gate specs

When different gates need different specs, pass a dict keyed by gate name. Each gate receives its own entry.

```python
result = pipeline.run(candidate, spec={
    "schema": my_schema,
    "fsm": {"transitions": my_workflow, "start": "a", "accept": ["z"]},
})
```

---

## Logging and replay

Attach a `RunLogger` to persist every run as append-only JSONL. Each record is deterministic, so any run can be replayed and audited. (The Pro Audit Gate adds cryptographic signing and Merkle chaining on top of this.)

```python
from determ8 import Pipeline, SchemaGate, RunLogger

pipeline = Pipeline(
    gates=[SchemaGate(schema=my_schema)],
    logger=RunLogger("runs.jsonl"),
)
```

---

## Where Determ8 is used

Anywhere an agent makes a decision that must be correct, auditable, or regulated.

- **Banking and finance:** loans, payments, fraud, trading.
- **Healthcare:** diagnosis support, medical billing, claims.
- **Insurance:** claims approval, underwriting.
- **Legal and compliance:** contract checks, KYC, regulatory filing.
- **Government:** benefits and eligibility.
- **Critical infrastructure:** energy, automotive, manufacturing.

Low-stakes agents do not need this. High-stakes agents cannot ship without it.

---

## Run the examples and tests

```bash
git clone https://github.com/Tech4Biz-Solutions-Pvt-Ltd/-Tech4Biz-Determ8.git
cd -Tech4Biz-Determ8
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"

python -m pytest -q          # run the test suite
python examples/loan_agent.py   # see every gate catch a real mistake
```

---

## License

The open core is released under the **Apache License 2.0**. See [LICENSE](LICENSE).

Determ8 Pro gates, domain packs, and the managed service are commercially licensed and **not** included in this repository.

---

## Get the full engine (commercial)

The free tier in this repository is the open core. It runs, and it is yours to use.

**Determ8 Pro is a paid, commercial product. It is not free and is not included in this repository.**

If you need the full source code with the paid features:

- Formal Verification Gate (Z3 / SMT proof engine)
- Rule Engine with prebuilt banking, healthcare, insurance, and compliance domain packs
- Constraint Gate
- Audit Gate with cryptographic signing and signed regulator-grade replay
- Multi-agent orchestration
- Managed hosting, support, and SLAs

Contact us. We will share pricing, licensing terms, and access to the full engine.

### contact@tech4biz.io

---

<div align="center">

**Determ8 by Tech4Biz Solutions. Restore stuck delivery. Ship proven answers.**

Determ8™ and Tech4Biz Solutions™ are trademarks of Tech4Biz Solutions.

</div>
