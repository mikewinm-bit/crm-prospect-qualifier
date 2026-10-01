from __future__ import annotations

from decimal import Decimal
from typing import Protocol

import pytest

from crm_prospect_qualifier import CreditCheckStatus, Prospect, Province


class ProspectFactory(Protocol):
    def __call__(
        self,
        *,
        company_name: str = ...,
        annual_turnover: Decimal = ...,
        years_in_operation: int = ...,
        industry: str = ...,
        province: Province = ...,
        credit_check_status: CreditCheckStatus = ...,
    ) -> Prospect: ...


@pytest.fixture
def make_prospect() -> ProspectFactory:
    def _make_prospect(
        *,
        company_name: str = "Acme Chemicals",
        annual_turnover: Decimal = Decimal(6000000),
        years_in_operation: int = 5,
        industry: str = "Manufacturing",
        province: Province = Province.GAUTENG,
        credit_check_status: CreditCheckStatus = CreditCheckStatus.PASSED,
    ) -> Prospect:
        return Prospect(
            company_name=company_name,
            annual_turnover=annual_turnover,
            years_in_operation=years_in_operation,
            industry=industry,
            province=province,
            credit_check_status=credit_check_status,
        )

    return _make_prospect
