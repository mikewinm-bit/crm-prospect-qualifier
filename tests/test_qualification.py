from __future__ import annotations

from decimal import Decimal

from conftest import ProspectFactory

from crm_prospect_qualifier import (
    MIN_ANNUAL_TURNOVER,
    MIN_YEARS_IN_OPERATION,
    CreditCheckStatus,
    qualify_prospect,
)


def test_fully_qualifying_prospect(make_prospect: ProspectFactory) -> None:
    result = qualify_prospect(make_prospect())
    assert result.qualified is True
    assert result.reasons == []


def test_turnover_below_threshold_fails(make_prospect: ProspectFactory) -> None:
    prospect = make_prospect(annual_turnover=MIN_ANNUAL_TURNOVER - Decimal(1))
    result = qualify_prospect(prospect)
    assert result.qualified is False
    assert len(result.reasons) == 1
    assert "annual_turnover" in result.reasons[0]


def test_years_below_threshold_fails(make_prospect: ProspectFactory) -> None:
    prospect = make_prospect(years_in_operation=MIN_YEARS_IN_OPERATION - 1)
    result = qualify_prospect(prospect)
    assert result.qualified is False
    assert len(result.reasons) == 1
    assert "years_in_operation" in result.reasons[0]


def test_credit_check_failed_fails(make_prospect: ProspectFactory) -> None:
    prospect = make_prospect(credit_check_status=CreditCheckStatus.FAILED)
    result = qualify_prospect(prospect)
    assert result.qualified is False
    assert len(result.reasons) == 1
    assert "credit_check_status" in result.reasons[0]


def test_credit_check_pending_fails(make_prospect: ProspectFactory) -> None:
    prospect = make_prospect(credit_check_status=CreditCheckStatus.PENDING)
    result = qualify_prospect(prospect)
    assert result.qualified is False
    assert len(result.reasons) == 1
    assert "credit_check_status" in result.reasons[0]


def test_all_three_rules_fail(make_prospect: ProspectFactory) -> None:
    prospect = make_prospect(
        annual_turnover=Decimal(1000),
        years_in_operation=0,
        credit_check_status=CreditCheckStatus.FAILED,
    )
    result = qualify_prospect(prospect)
    assert result.qualified is False
    assert len(result.reasons) == 3


def test_turnover_exactly_at_threshold_qualifies(
    make_prospect: ProspectFactory,
) -> None:
    prospect = make_prospect(annual_turnover=MIN_ANNUAL_TURNOVER)
    result = qualify_prospect(prospect)
    assert result.qualified is True


def test_years_exactly_at_threshold_qualifies(make_prospect: ProspectFactory) -> None:
    prospect = make_prospect(years_in_operation=MIN_YEARS_IN_OPERATION)
    result = qualify_prospect(prospect)
    assert result.qualified is True
