# Hardening Notes — Decision Engine Assessment

## 1. Scope

This implementation demonstrates deterministic decision making over a small,
synthetic set of candidate actions. The engine evaluates only candidates that
are explicitly permitted and then ranks them using a deterministic utility
function and tie-breaking policy.

The implementation is intentionally bounded and does not execute external
actions.

## 2. Safety Controls

### Authorization Before Utility

Authorization filtering occurs before utility calculation.

Unauthorized candidates are therefore prevented from winning even when they
have a very high theoretical benefit or utility.

### Deterministic Selection

Permitted candidates are ranked using:

1. Highest utility
2. Lower risk
3. Lower cost
4. Alphabetical candidate name

This makes the result independent of input ordering.

### Explicit Fallback

If no permitted candidate exists, the engine does not select an action.

Instead, it returns:

- `status = no_safe_option`
- `selected = null`
- `selected_utility = null`
- `action = escalate`

This provides a safe boundary rather than silently bypassing authorization.

### Structured Explanations

The decision result records the selected candidate, utility, explanation,
and rejected alternatives. This provides traceable evidence for the decision.

## 3. Input Validation

Candidate data is validated using a typed dataclass.

The implementation rejects:

- Empty candidate names
- Negative benefit, risk, or cost values
- Invalid numeric types
- Invalid authorization types
- Invalid evidence lists
- Invalid `allowed` values
- Invalid candidate collections

The CLI also validates the input JSON structure before creating candidates.

## 4. Residual Risks

The current implementation does not provide:

- Real identity or access-control integration
- Cryptographic authorization verification
- External policy or permission service integration
- Human approval workflows
- Dynamic risk models
- Evidence authenticity verification
- Persistent audit logging
- Distributed concurrency protection
- Protection against maliciously constructed input beyond the implemented
  validation rules

The `allowed` field is therefore treated as trusted input within this
assessment rather than as a complete production authorization mechanism.

## 5. Decision-Model Limitations

Utility is intentionally simple:

`utility = benefit - risk - cost`

Real-world decision systems may require:

- Different weighting of risk and benefit
- Risk thresholds
- Hard safety constraints
- Context-dependent policies
- Confidence thresholds
- Time sensitivity
- Human approval
- Regulatory requirements

The current scoring function should therefore not be interpreted as a
production policy.

## 6. Safe Next Extension

A suitable next extension would be a policy layer that evaluates each
candidate against independently supplied authorization and safety rules before
the decision engine receives it.

The extension should preserve the existing invariant:

> An unauthorized candidate must never become the selected action.

The policy layer should produce a structured authorization decision that can be
stored alongside the existing decision trace.

## 7. External Action Boundary

The decision engine only recommends or selects an action. It does not execute
the selected action against an external system.

Keeping selection separate from execution reduces the consequences of an
incorrect decision and provides an opportunity for additional validation or
human approval before an external side effect occurs.

## 8. Evidence Reproducibility

Evidence is generated from synthetic input files using:

`python generate_evidence.py`

The generated artifacts include decision traces, state snapshots, decision
outputs, and an evidence summary.

The complete automated regression suite currently contains 31 passing tests.