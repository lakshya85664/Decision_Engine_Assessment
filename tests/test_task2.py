import pytest

from decision_engine.decision import (
    calculate_utility,
    choose_highest_utility,
    filter_authorized,
)
from decision_engine.models import Candidate


def test_filter_removes_unauthorized_candidates():
    candidates = [
        Candidate(
            name="draft",
            benefit=7,
            risk=1,
            cost=1,
            authorization="approved",
            allowed=True,
        ),
        Candidate(
            name="send",
            benefit=10,
            risk=1,
            cost=1,
            authorization="not_approved",
            allowed=False,
        ),
    ]

    result = filter_authorized(candidates)

    assert [candidate.name for candidate in result] == [
        "draft",
    ]


def test_unauthorized_candidate_is_not_scored():
    unauthorized = Candidate(
        name="send",
        benefit=100,
        risk=0,
        cost=0,
        authorization="not_approved",
        allowed=False,
    )

    with pytest.raises(ValueError):
        calculate_utility(unauthorized)


def test_unauthorized_high_utility_candidate_cannot_win():
    candidates = [
        Candidate(
            name="safe",
            benefit=7,
            risk=1,
            cost=1,
            authorization="approved",
            allowed=True,
        ),
        Candidate(
            name="unauthorized",
            benefit=100,
            risk=0,
            cost=0,
            authorization="not_approved",
            allowed=False,
        ),
    ]

    winner, utility = choose_highest_utility(candidates)

    assert winner.name == "safe"
    assert utility == 5


def test_utility_is_benefit_minus_risk_and_cost():
    candidate = Candidate(
        name="draft",
        benefit=8,
        risk=2,
        cost=1,
        authorization="approved",
        allowed=True,
    )

    assert calculate_utility(candidate) == 5


def test_no_permitted_option_raises():
    candidates = [
        Candidate(
            name="blocked",
            benefit=10,
            risk=1,
            cost=1,
            authorization="not_approved",
            allowed=False,
        )
    ]

    with pytest.raises(ValueError, match="no permitted option"):
        choose_highest_utility(candidates)


def test_candidates_must_be_a_list():
    with pytest.raises(TypeError):
        filter_authorized("not a list")


def test_filter_requires_candidate_objects():
    with pytest.raises(TypeError):
        filter_authorized(["draft"])