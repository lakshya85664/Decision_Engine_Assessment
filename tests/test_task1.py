import pytest

from decision_engine.models import Candidate


def test_candidate_contains_required_fields():
    candidate = Candidate(
        name="draft",
        benefit=7,
        risk=1,
        cost=2,
        authorization="approved",
        required_evidence=[
            "draft_content",
        ],
        allowed=True,
    )

    assert candidate.name == "draft"
    assert candidate.benefit == 7
    assert candidate.risk == 1
    assert candidate.cost == 2
    assert candidate.authorization == "approved"
    assert candidate.required_evidence == [
        "draft_content",
    ]
    assert candidate.allowed is True


def test_candidate_defaults():
    candidate = Candidate(
        name="review",
        benefit=5,
        risk=2,
        cost=1,
        authorization="approved",
    )

    assert candidate.required_evidence == []
    assert candidate.allowed is True


def test_candidate_rejects_negative_numeric_values():
    with pytest.raises(ValueError):
        Candidate(
            name="draft",
            benefit=-1,
            risk=1,
            cost=1,
            authorization="approved",
        )


def test_candidate_rejects_invalid_numeric_types():
    with pytest.raises(TypeError):
        Candidate(
            name="draft",
            benefit="high",
            risk=1,
            cost=1,
            authorization="approved",
        )


def test_candidate_rejects_empty_name():
    with pytest.raises(ValueError):
        Candidate(
            name="",
            benefit=5,
            risk=1,
            cost=1,
            authorization="approved",
        )


def test_candidate_is_immutable():
    candidate = Candidate(
        name="draft",
        benefit=7,
        risk=1,
        cost=2,
        authorization="approved",
    )

    with pytest.raises(AttributeError):
        candidate.benefit = 10