import argparse
import json
from pathlib import Path
from typing import Any

from .decision import Decision, SafeFallback, decide
from .models import Candidate


def load_candidates(
    input_path: Path,
) -> list[Candidate]:
    """Load candidate actions from a JSON file."""

    if not input_path.exists():
        raise ValueError(
            f"input file does not exist: {input_path}"
        )

    try:
        data: dict[str, Any] = json.loads(
            input_path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid JSON: {exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "input must be a JSON object"
        )

    raw_candidates = data.get("candidates")

    if not isinstance(raw_candidates, list):
        raise ValueError(
            "input must contain a candidates list"
        )

    candidates: list[Candidate] = []

    for item in raw_candidates:
        if not isinstance(item, dict):
            raise ValueError(
                "each candidate must be a JSON object"
            )

        candidates.append(
            Candidate(
                name=item["name"],
                benefit=item["benefit"],
                risk=item["risk"],
                cost=item["cost"],
                authorization=item["authorization"],
                required_evidence=item.get(
                    "required_evidence",
                    [],
                ),
                allowed=item.get(
                    "allowed",
                    True,
                ),
            )
        )

    return candidates


def candidate_to_dict(
    candidate: Candidate,
) -> dict[str, Any]:
    """Convert a Candidate into JSON-compatible data."""

    return {
        "name": candidate.name,
        "benefit": candidate.benefit,
        "risk": candidate.risk,
        "cost": candidate.cost,
        "authorization": candidate.authorization,
        "required_evidence": list(
            candidate.required_evidence
        ),
        "allowed": candidate.allowed,
    }


def decision_to_dict(
    result: Decision | SafeFallback,
) -> dict[str, Any]:
    """Convert a decision result into JSON-compatible data."""

    selected = None

    if result.selected is not None:
        selected = candidate_to_dict(
            result.selected
        )

    return {
        "status": result.status,
        "selected": selected,
        "selected_utility": result.selected_utility,
        "explanation": result.explanation,
        "rejected": result.rejected,
        "action": getattr(
            result,
            "action",
            None,
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the decision engine."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    choose_parser = subparsers.add_parser(
        "choose",
        help="Choose the safest permitted candidate.",
    )

    choose_parser.add_argument(
        "--input",
        required=True,
        help="Input candidate JSON file.",
    )

    choose_parser.add_argument(
        "--output",
        required=True,
        help="Output decision JSON file.",
    )

    args = parser.parse_args()

    if args.command != "choose":
        parser.error(
            "unsupported command"
        )

    try:
        candidates = load_candidates(
            Path(args.input)
        )

        result = decide(candidates)

        output = decision_to_dict(result)

        output_path = Path(args.output)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json.dumps(
                output,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        parser.error(str(exc))

    print(
        f"Decision written to {args.output}"
    )
    print(
        f"Status: {result.status}"
    )

    if result.selected is not None:
        print(
            f"Selected: {result.selected.name}"
        )
        print(
            f"Utility: {result.selected_utility}"
        )
    else:
        print(
            "Selected: None"
        )
        print(
            f"Action: {result.action}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())