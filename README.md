# Topic 3 — Decision Engine Assessment

## Project Overview

This project implements a deterministic decision engine for selecting the safest permitted action from a set of candidate actions.

The implementation covers five core requirements:

1. Represent candidate actions with validated typed data.
2. Filter unauthorized candidates before utility calculation.
3. Select candidates deterministically using utility and tie-breaking rules.
4. Produce structured explanations and decision evidence.
5. Return an explicit safe fallback when no permitted option exists.

The project uses synthetic JSON inputs and does not require external APIs, credentials, or network access.

## Project Structure

```text
Decision_Engine_Assessment/
├── decision_engine/
│   ├── __init__.py
│   ├── cli.py
│   ├── decision.py
│   └── models.py
├── tests/
│   ├── fixtures/
│   ├── test_task1.py
│   ├── test_task2.py
│   ├── test_task3.py
│   ├── test_task4.py
│   └── test_task5.py
├── examples/
│   ├── action_candidates.json
│   └── no_safe_options.json
├── evidence/
│   ├── traces/
│   └── state_snapshots/
├── outputs/
│   ├── decision.json
│   ├── no_safe_decision.json
│   └── evidence_summary.json
├── generate_evidence.py
├── HARDENING.md
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

## Environment Setup

Tested with Python 3.13.9, pytest 8.4.2, and Windows CMD.

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Running Tests

```cmd
python -m pytest -q
```

Final result:

```text
31 passed
```

## Running the Decision Engine

### Authorized Candidate Scenario

```cmd
python -m decision_engine.cli choose --input examples\action_candidates.json --output outputs\decision.json
```

Result:

```text
Status: selected
Selected: draft
Utility: 6
```

The `send` candidate has benefit 100 but is unauthorized, so it is rejected before selection.

### No-Safe-Option Scenario

```cmd
python -m decision_engine.cli choose --input examples\no_safe_options.json --output outputs\no_safe_decision.json
```

Result:

```text
Status: no_safe_option
Selected: None
Action: escalate
```

## Decision Policy

Utility is calculated as:

```text
utility = benefit - risk - cost
```

Only candidates with `allowed = true` are considered.

Selection order:

1. Highest utility
2. Lower risk
3. Lower cost
4. Alphabetical candidate name

This makes decisions deterministic and independent of input ordering.

## Evidence

Generate reproducible evidence with:

```cmd
python generate_evidence.py
```

Generated artifacts:

- `evidence/traces/authorized_selection_trace.json`
- `evidence/traces/no_safe_option_trace.json`
- `evidence/state_snapshots/authorized_selection_state.json`
- `evidence/state_snapshots/no_safe_option_state.json`
- `outputs/decision.json`
- `outputs/no_safe_decision.json`
- `outputs/evidence_summary.json`

## Hardening and Safety

`HARDENING.md` documents authorization-before-utility behavior, deterministic selection, explicit fallback, input validation, residual risks, utility-model limitations, and a safe next extension.

The engine only selects an action; it does not execute external actions. This keeps decision selection separate from external side effects.

## Reflection

This assessment helped me understand that decision making in an AI agent is not simply about calculating which option has the highest numerical score. A reliable decision engine must first establish which actions are actually permitted. I therefore treated authorization as a hard constraint rather than another factor in the utility calculation. This was demonstrated with a candidate that had a very high benefit but was not authorized; the engine correctly rejected it before selection.

I also learned the importance of deterministic behavior. Instead of relying on input order, the engine applies explicit tie-breaking rules based on risk, cost, and candidate name. This makes decisions reproducible and easier to test and audit.

Another important lesson was the need for an explicit failure path. When all available candidates are unauthorized, selecting the least bad option would violate the safety requirement. The engine instead returns a structured `no_safe_option` result and recommends escalation.

Finally, generating traces and state snapshots showed how implementation evidence can support evaluation. The project separates decision selection from external execution, validates inputs, records rejected alternatives, and documents residual risks. These practices make the system more predictable, testable, and easier to extend into a larger agent workflow.
