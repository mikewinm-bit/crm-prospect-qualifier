from __future__ import annotations

from decimal import Decimal

from .models import CreditCheckStatus, Prospect, QualificationResult

MIN_ANNUAL_TURNOVER = Decimal(5000000)
MIN_YEARS_IN_OPERATION = 3


def qualify_prospect(prospect: Prospect) -> QualificationResult:
    reasons: list[str] = []

    if prospect.annual_turnover < MIN_ANNUAL_TURNOVER:
        reasons.append(
            f"annual_turnover {prospect.annual_turnover} is below minimum {MIN_ANNUAL_TURNOVER}"
        )

    if prospect.years_in_operation < MIN_YEARS_IN_OPERATION:
        reasons.append(
            f"years_in_operation {prospect.years_in_operation} is below minimum "
            f"{MIN_YEARS_IN_OPERATION}"
        )

    if prospect.credit_check_status != CreditCheckStatus.PASSED:
        reasons.append(
            f"credit_check_status {prospect.credit_check_status.value!r} is not "
            f"{CreditCheckStatus.PASSED.value!r}"
        )

    return QualificationResult(qualified=not reasons, reasons=reasons)
