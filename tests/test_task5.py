from decision_engine.decision import (
    SafeFallback,
    decide,
)
from decision_engine.models import Candidate


def test_all_unauthorized_candidates_trigger_safe_fallback():
    candidates = [
        Candidate(
            name="send",
            benefit=100,
            risk=0,
            cost=0,
            authorization="not_approved",
            allowed=False,
        ),
        Candidate(
            name="publish",
            benefit=90,
            risk=1,
            cost=1,
            authorization="not_approved",
            allowed=False,
        ),
    ]

    result = decide(candidates)

    assert isinstance(result, SafeFallback)
    assert result.status == "no_safe_option"
    assert result.selected is None
    assert result.selected_utility is None
    assert result.action == "escalate"


def test_safe_fallback_explains_why_no_action_was_selected():
    candidates = [
        Candidate(
            name="send",
            benefit=100,
            risk=0,
            cost=0,
            authorization="not_approved",
            allowed=False,
        )
    ]

    result = decide(candidates)

    assert "No permitted candidate" in result.explanation
    assert "No action was selected" in result.explanation
    assert "authorization" in result.explanation


def test_safe_fallback_records_rejected_candidates():
    candidates = [
        Candidate(
            name="send",
            benefit=100,
            risk=0,
            cost=0,
            authorization="not_approved",
            allowed=False,
        ),
        Candidate(
            name="publish",
            benefit=80,
            risk=1,
            cost=1,
            authorization="not_approved",
            allowed=False,
        ),
    ]

    result = decide(candidates)

    assert len(result.rejected) == 2
    assert result.rejected[0]["name"] == "send"
    assert result.rejected[1]["name"] == "publish"


def test_mixed_candidates_selects_permitted_option():
    candidates = [
        Candidate(
            name="blocked",
            benefit=100,
            risk=0,
            cost=0,
            authorization="not_approved",
            allowed=False,
        ),
        Candidate(
            name="safe",
            benefit=7,
            risk=1,
            cost=1,
            authorization="approved",
            allowed=True,
        ),
    ]

    result = decide(candidates)

    assert result.status == "selected"
    assert result.selected.name == "safe"
    assert result.selected_utility == 5


def test_empty_candidates_use_safe_fallback():
    result = decide([])

    assert isinstance(result, SafeFallback)
    assert result.status == "no_safe_option"
    assert result.selected is None


def test_invalid_input_type_is_rejected():
    import pytest

    with pytest.raises(TypeError):
        decide("not a list")