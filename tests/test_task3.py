import pytest

from decision_engine.decision import choose_highest_utility
from decision_engine.models import Candidate


def test_higher_utility_wins():
    candidates = [
        Candidate(
            name="low",
            benefit=5,
            risk=1,
            cost=1,
            authorization="approved",
        ),
        Candidate(
            name="high",
            benefit=9,
            risk=1,
            cost=1,
            authorization="approved",
        ),
    ]

    winner, utility = choose_highest_utility(candidates)

    assert winner.name == "high"
    assert utility == 7


def test_equal_utility_prefers_lower_risk():
    candidates = [
        Candidate(
            name="risky",
            benefit=8,
            risk=3,
            cost=0,
            authorization="approved",
        ),
        Candidate(
            name="safer",
            benefit=6,
            risk=1,
            cost=1,
            authorization="approved",
        ),
    ]

    assert (
        choose_highest_utility(candidates)[0].name
        == "safer"
    )


def test_equal_utility_prefers_lower_risk():
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

    assert (
        choose_highest_utility(candidates)[0].name
        == "safer"
    )


def test_complete_tie_uses_name():
    candidates = [
        Candidate(
            name="zeta",
            benefit=8,
            risk=1,
            cost=1,
            authorization="approved",
        ),
        Candidate(
            name="alpha",
            benefit=8,
            risk=1,
            cost=1,
            authorization="approved",
        ),
    ]

    winner, utility = choose_highest_utility(candidates)

    assert winner.name == "alpha"
    assert utility == 6


def test_tie_breaking_is_independent_of_input_order():
    first_order = [
        Candidate(
            name="zeta",
            benefit=8,
            risk=1,
            cost=1,
            authorization="approved",
        ),
        Candidate(
            name="alpha",
            benefit=8,
            risk=1,
            cost=1,
            authorization="approved",
        ),
    ]

    reversed_order = list(reversed(first_order))

    first_winner = choose_highest_utility(
        first_order
    )[0].name

    second_winner = choose_highest_utility(
        reversed_order
    )[0].name

    assert first_winner == "alpha"
    assert second_winner == "alpha"


def test_single_candidate_is_valid_boundary_case():
    candidate = Candidate(
        name="only",
        benefit=5,
        risk=2,
        cost=1,
        authorization="approved",
    )

    winner, utility = choose_highest_utility(
        [candidate]
    )

    assert winner == candidate
    assert utility == 2


def test_empty_candidates_are_rejected():
    with pytest.raises(
        ValueError,
        match="no permitted option",
    ):
        choose_highest_utility([])