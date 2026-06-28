# Determ8

**The deterministic gate for agentic systems.**

Determ8 by Tech4Biz

---

## The problem

AI agents are probabilistic. Ask the same question twice, you can get two answers. That is fine for chat. It is unacceptable for a loan decision, a medical claim, a payment, or any regulated workflow.

Enterprises will not put agents into production where "usually right" is the guarantee.

## What Determ8 does

Determ8 wraps a probabilistic model in a deterministic pipeline. The model proposes. The pipeline proves or rejects. Same input, same verdict, every time.

The intelligence stays probabilistic. The correctness layer is pure algorithm.

```
Request  ->  Agent proposes  ->  [ Gate -> Gate -> Gate ]  ->  Verdict (pass / fail)  ->  Signed audit log
```

Every gate answers one question deterministically. Cheap gates run first. Expensive gates run last. The pipeline stops at the first failure.

---

## How it works

Determ8 is built on one contract. Every gate is a plug-in that implements the same signature:

```
gate(candidate, spec) -> { pass: bool, reason: str, proof: object }
```

The pipeline runner chains gates in a declared order, stops on the first failure, and logs every result. You add gates one at a time. You configure which gates run per project.

The determinism guarantee is simple: same input plus same gate config produces the same verdict, always.

---

## Free vs Paid

Determ8 is open core. The free tier gives you a real, working deterministic pipeline. The paid tier gives you the proof and compliance that regulated industries cannot ship without.

### Free (Open Source)

The framework skeleton and the fast structural gates. Enough to build a working pipeline and run it end to end.

| Gate | Algorithm | Question it answers |
|------|-----------|---------------------|
| Pipeline Runner | Gate-chaining engine | Did the candidate clear every gate in order? |
| Schema Gate | JSON Schema, grammar, parsers | Is the output the exact required shape? |
| FSM Gate | Finite State Machine | Did the agent follow the steps in legal order? |
| Idempotency Gate | SHA-256 hashing, cache keys | Did this same request already run? |
| Graph Gate | DAG validation, topological sort | Are tasks in valid order with no cycles? |

This is everything you need to wire up a deterministic pipeline, see it run, and trust the pattern.

### Paid (Determ8 Pro)

The hard, defensible gates. Formal proof, domain compliance, and audit-grade trails. This is what banks, hospitals, and insurers pay for.

| Gate | Algorithm | Question it answers |
|------|-----------|---------------------|
| Formal Verification Gate | Z3 / SMT solvers | Is the output provably correct against the spec? |
| Rule Engine + Domain Packs | Drools, decision tables | Does it obey real-world regulation? |
| Constraint Gate | Constraint solvers | Do all numbers and limits hold together? |
| Audit Gate | Cryptographic signing, Merkle logs | Can we prove to a regulator nothing was altered? |

**Determ8 Pro also includes:**

- Prebuilt domain packs: banking, healthcare, insurance, compliance.
- Audit-grade signed replay for regulators.
- Multi-agent orchestration across gates.
- Managed hosting, support, and SLAs.

---

## Quick start (Free tier)

```bash
pip install determ8
```

```python
from determ8 import Pipeline, SchemaGate, FSMGate, IdempotencyGate

pipeline = Pipeline(gates=[
    IdempotencyGate(),
    SchemaGate(schema=loan_decision_schema),
    FSMGate(states=loan_workflow),
])

verdict = pipeline.run(candidate=agent_output, spec=loan_spec)

if verdict.passed:
    ship(candidate)
else:
    reject(verdict.reason)
```

The agent guesses. The pipeline proves. You never ship a guess, only a proven answer.

---

## Example: loan eligibility agent

A bank wants an agent to read a loan application and decide approve, reject, or escalate. Every decision must be correct, follow regulation, and survive an audit.

1. Application comes in. Hashed, idempotency key assigned. Never processed twice.
2. Agent reads it and proposes a decision.
3. **Schema Gate** (free): is the output the right shape?
4. **FSM Gate** (free): did the agent verify identity, then check credit, then decide?
5. **Rule Gate** (Pro): does the decision obey lending policy and KYC?
6. **Formal Verification Gate** (Pro): is the risk math provably correct?
7. **Audit Gate** (Pro): sign and log the full trail for the regulator.

Free gets you a pipeline that runs. Pro gets you a pipeline a regulator will accept.

---

## Where Determ8 is used

Anywhere an agent makes a decision that must be correct, auditable, or regulated.

- Banking and finance: loans, payments, fraud, trading.
- Healthcare: diagnosis support, medical billing, claims.
- Insurance: claims approval, underwriting.
- Legal and compliance: contract checks, KYC, regulatory filing.
- Government: benefits and eligibility.
- Critical infrastructure: energy, automotive, manufacturing.

Low-stakes agents do not need this. High-stakes agents cannot ship without it.

---

## License

The open core is released under [LICENSE](LICENSE).

Determ8 Pro gates, domain packs, and the managed service are commercially licensed and not included in this repository.

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

**contact@tech4biz.io**

---

Determ8 by Tech4Biz. Restore stuck delivery. Ship proven answers.
