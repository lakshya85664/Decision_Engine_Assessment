from dataclasses import dataclass

from .models import Candidate


@dataclass(frozen=True)
class Decision:
    """Structured result of a successful decision."""

    selected: Candidate
    selected_utility: int
    explanation: str
    rejected: list[dict[str, str]]
    status: str = "selected"


@dataclass(frozen=True)
class SafeFallback:
    """Structured result when no safe option can be selected."""

    selected: None
    selected_utility: None
    explanation: str
    rejected: list[dict[str, str]]
    status: str = "no_safe_option"
    action: str = "escalate"


def filter_authorized(
    candidates: list[Candidate],
) -> list[Candidate]:
    """Remove candidates that are not permitted."""

    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")

    if not all(
        isinstance(candidate, Candidate)
        for candidate in candidates
    ):
        raise TypeError(
            "candidates must contain Candidate objects"
        )

    return [
        candidate
        for candidate in candidates
        if candidate.allowed
    ]


def calculate_utility(candidate: Candidate) -> int:
    """Calculate benefit minus risk and cost."""

    if not isinstance(candidate, Candidate):
        raise TypeError(
            "candidate must be a Candidate"
        )

    if not candidate.allowed:
        raise ValueError(
            "utility cannot be calculated for an unauthorized candidate"
        )

    return (
        candidate.benefit
        - candidate.risk
        - candidate.cost
    )


def _selection_key(
    candidate: Candidate,
) -> tuple[int, int, int, str]:
    """Return the deterministic candidate selection key."""

    utility = calculate_utility(candidate)

    return (
        -utility,
        candidate.risk,
        candidate.cost,
        candidate.name,
    )


def choose_highest_utility(
    candidates: list[Candidate],
) -> tuple[Candidate, int]:
    """Choose the highest-utility permitted candidate."""

    safe_candidates = filter_authorized(candidates)

    if not safe_candidates:
        raise ValueError(
            "no permitted option"
        )

    winner = min(
        safe_candidates,
        key=_selection_key,
    )

    return (
        winner,
        calculate_utility(winner),
    )


def make_decision(
    candidates: list[Candidate],
) -> Decision:
    """
    Select the best permitted candidate and explain the result.

    This function preserves the existing successful-decision contract.
    Use decide() when a safe fallback is required.
    """

    if not candidates:
        raise ValueError(
            "no candidates provided"
        )

    permitted = filter_authorized(candidates)

    if not permitted:
        raise ValueError(
            "no permitted option"
        )

    winner, winner_utility = choose_highest_utility(
        permitted
    )

    rejected: list[dict[str, str]] = []

    for candidate in candidates:
        if not candidate.allowed:
            rejected.append(
                {
                    "name": candidate.name,
                    "reason": (
                        "rejected because authorization "
                        "was not granted"
                    ),
                }
            )
            continue

        if candidate.name == winner.name:
            continue

        candidate_utility = calculate_utility(candidate)

        if candidate_utility < winner_utility:
            reason = (
                f"lower utility ({candidate_utility}) "
                f"than selected utility "
                f"({winner_utility})"
            )
        elif candidate.risk > winner.risk:
            reason = "same utility but higher risk"
        elif candidate.cost > winner.cost:
            reason = (
                "same utility and risk but higher cost"
            )
        else:
            reason = "lost deterministic tie-break"

        rejected.append(
            {
                "name": candidate.name,
                "reason": reason,
            }
        )

    explanation = (
        f"Selected '{winner.name}' because it is the "
        f"highest-ranked permitted candidate with utility "
        f"{winner_utility}. "
        f"Ties are resolved by lower risk, lower cost, "
        f"then alphabetical name order."
    )

    return Decision(
        selected=winner,
        selected_utility=winner_utility,
        explanation=explanation,
        rejected=rejected,
    )


def decide(
    candidates: list[Candidate],
) -> Decision | SafeFallback:
    """
    Make a safe decision or return an explicit fallback.

    If no permitted candidate exists, no action is selected.
    """

    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")

    if not candidates:
        return SafeFallback(
            selected=None,
            selected_utility=None,
            explanation=(
                "No candidates were provided. "
                "No action can be selected safely."
            ),
            rejected=[],
        )

    permitted = filter_authorized(candidates)

    if not permitted:
        rejected = [
            {
                "name": candidate.name,
                "reason": (
                    "rejected because authorization "
                    "was not granted"
                ),
            }
            for candidate in candidates
        ]

        return SafeFallback(
            selected=None,
            selected_utility=None,
            explanation=(
                "No permitted candidate is available. "
                "No action was selected. "
                "Escalation or additional authorization "
                "is required."
            ),
            rejected=rejected,
        )

    return make_decision(candidates)