from dataclasses import dataclass, field


@dataclass(frozen=True)
class Candidate:
    """
    Typed representation of one candidate action.

    A candidate contains the information required by the decision engine
    before a decision is made.
    """

    name: str
    benefit: int
    risk: int
    cost: int
    authorization: str
    required_evidence: list[str] = field(default_factory=list)
    allowed: bool = True

    def __post_init__(self) -> None:
        """Validate the candidate contract."""

        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("candidate name must be a non-empty string")

        numeric_fields = {
            "benefit": self.benefit,
            "risk": self.risk,
            "cost": self.cost,
        }

        for field_name, value in numeric_fields.items():
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
            ):
                raise TypeError(
                    f"{field_name} must be an integer"
                )

            if value < 0:
                raise ValueError(
                    f"{field_name} must be non-negative"
                )

        if not isinstance(self.authorization, str):
            raise TypeError(
                "authorization must be a string"
            )

        if not isinstance(self.required_evidence, list):
            raise TypeError(
                "required_evidence must be a list"
            )

        if not all(
            isinstance(item, str)
            for item in self.required_evidence
        ):
            raise TypeError(
                "required_evidence must contain strings"
            )

        if not isinstance(self.allowed, bool):
            raise TypeError(
                "allowed must be a boolean"
            )