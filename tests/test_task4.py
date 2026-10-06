from decision_engine.decision import make_decision
from decision_engine.models import Candidate


def test_decision_contains_selected_candidate():
    candidates = [
        Candidate(
            name="draft",
            benefit=8,
            risk=1,
            cost=1,
            authorization="approved",
        ),
        Candidate(
            name="review",
            benefit=5,
            risk=1,
            cost=1,
            authorization="approved",
        ),
    ]

    decision = make_decision(candidates)

    assert decision.selected.name == "draft"
    assert decision.selected_utility == 6


def test_decision_contains_explanation():
    candidates = [
        Candidate(
            name="draft",
            benefit=8,
            risk=1,
            cost=1,
            authorization="approved",
        )
    ]

    decision = make_decision(candidates)

    assert "draft" in decision.explanation
    assert "utility" in decision.explanation
    assert decision.explanation


def test_lower_utility_alternative_is_explained():
    candidates = [
        Candidate(
            name="draft",
            benefit=8,
            risk=1,
            cost=1,
            authorization="approved",
        ),
        Candidate(
            name="review",
            benefit=5,
            risk=1,
            cost=1,
            authorization="approved",
        ),
    ]

    decision = make_decision(candidates)

    assert decision.rejected == [
        {
            "name": "review",
            "reason": "lower utility (3) than selected utility (6)",
        }
    ]


def test_unauthorized_alternative_is_explained():
    candidates = [
        Candidate(
            name="draft",
            benefit=8,
            risk=1,
            cost=1,
            authorization="approved",
        ),
        Candidate(
            name="send",
            benefit=100,
            risk=0,
            cost=0,
            authorization="not_approved",
            allowed=False,
        ),
    ]

    decision = make_decision(candidates)

    assert decision.selected.name == "draft"
    assert decision.rejected == [
        {
            "name": "send",
            "reason": (
                "rejected because authorization "
                "was not granted"
            ),
        }
    ]


def test_equal_utility_lower_risk_is_explained():
    candidates = [
        Candidate(
            name="risky",
            benefit=9,
            risk=3,
            cost=1,
            authorization="approved",
        ),
        Candidate(
            name="safer",
            benefit=7,
            risk=1,
            cost=1,
            authorization="approved",
        ),
    ]

    decision = make_decision(candidates)

    assert decision.selected.name == "safer"
    assert decision.rejected == [
        {
            "name": "risky",
            "reason": "same utility but higher risk",
        }
    ]


def test_no_candidates_is_rejected():
    import pytest

    with pytest.raises(
        ValueError,
        match="no candidates provided",
    ):
        make_decision([])