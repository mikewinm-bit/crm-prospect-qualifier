from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Province(Enum):
    EASTERN_CAPE = "Eastern Cape"
    FREE_STATE = "Free State"
    GAUTENG = "Gauteng"
    KWAZULU_NATAL = "KwaZulu-Natal"
    LIMPOPO = "Limpopo"
    MPUMALANGA = "Mpumalanga"
    NORTHERN_CAPE = "Northern Cape"
    NORTH_WEST = "North West"
    WESTERN_CAPE = "Western Cape"


class CreditCheckStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"


@dataclass(frozen=True)
class Prospect:
    company_name: str
    annual_turnover: Decimal
    years_in_operation: int
    industry: str
    province: Province
    credit_check_status: CreditCheckStatus

    def __post_init__(self) -> None:
        if not isinstance(self.company_name, str):
            raise TypeError(
                f"company_name must be a str, got {type(self.company_name).__name__}"
            )
        if not isinstance(self.industry, str):
            raise TypeError(
                f"industry must be a str, got {type(self.industry).__name__}"
            )
        if not isinstance(self.annual_turnover, Decimal):
            raise TypeError(
                f"annual_turnover must be a Decimal, got {type(self.annual_turnover).__name__}"
            )
        if not isinstance(self.years_in_operation, int):
            raise TypeError(
                f"years_in_operation must be an int, got {type(self.years_in_operation).__name__}"
            )
        if not isinstance(self.province, Province):
            raise TypeError(
                f"province must be a Province enum member, got {self.province!r}"
            )
        if not isinstance(self.credit_check_status, CreditCheckStatus):
            raise TypeError(
                "credit_check_status must be a CreditCheckStatus enum member, "
                f"got {self.credit_check_status!r}"
            )

        if not self.company_name.strip():
            raise ValueError("company_name must not be empty")
        if not self.industry.strip():
            raise ValueError("industry must not be empty")
        if self.annual_turnover < 0:
            raise ValueError("annual_turnover must not be negative")
        if self.years_in_operation < 0:
            raise ValueError("years_in_operation must not be negative")

        object.__setattr__(self, "company_name", self.company_name.strip())
        object.__setattr__(self, "industry", self.industry.strip())


@dataclass
class QualificationResult:
    qualified: bool
    reasons: list[str]
