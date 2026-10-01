from __future__ import annotations

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest
from conftest import ProspectFactory

from crm_prospect_qualifier import CreditCheckStatus, Province


@pytest.mark.parametrize("province", list(Province))
def test_valid_construction_with_each_province(
    make_prospect: ProspectFactory, province: Province
) -> None:
    prospect = make_prospect(province=province)
    assert prospect.province is province


@pytest.mark.parametrize("status", list(CreditCheckStatus))
def test_valid_construction_with_each_credit_check_status(
    make_prospect: ProspectFactory, status: CreditCheckStatus
) -> None:
    prospect = make_prospect(credit_check_status=status)
    assert prospect.credit_check_status is status


def test_negative_annual_turnover_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(ValueError):
        make_prospect(annual_turnover=Decimal(-1))


def test_negative_years_in_operation_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(ValueError):
        make_prospect(years_in_operation=-1)


def test_empty_company_name_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(ValueError):
        make_prospect(company_name="")


def test_whitespace_only_company_name_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(ValueError):
        make_prospect(company_name="   ")


def test_empty_industry_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(ValueError):
        make_prospect(industry="")


def test_whitespace_only_industry_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(ValueError):
        make_prospect(industry="   ")


def test_company_name_is_stripped_of_surrounding_whitespace(
    make_prospect: ProspectFactory,
) -> None:
    prospect = make_prospect(company_name="  Acme Chemicals  ")
    assert prospect.company_name == "Acme Chemicals"


def test_industry_is_stripped_of_surrounding_whitespace(
    make_prospect: ProspectFactory,
) -> None:
    prospect = make_prospect(industry="  Manufacturing  ")
    assert prospect.industry == "Manufacturing"


def test_prospect_is_immutable(make_prospect: ProspectFactory) -> None:
    prospect = make_prospect()
    with pytest.raises(FrozenInstanceError):
        prospect.annual_turnover = Decimal(-1)  # type: ignore[misc]


def test_invalid_province_type_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(TypeError):
        make_prospect(province="Gauteng")  # type: ignore[arg-type]


def test_invalid_credit_check_status_type_raises(
    make_prospect: ProspectFactory,
) -> None:
    with pytest.raises(TypeError):
        make_prospect(credit_check_status="passed")  # type: ignore[arg-type]


def test_invalid_company_name_type_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(TypeError):
        make_prospect(company_name=123)  # type: ignore[arg-type]


def test_invalid_industry_type_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(TypeError):
        make_prospect(industry=123)  # type: ignore[arg-type]


def test_invalid_annual_turnover_type_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(TypeError):
        make_prospect(annual_turnover=6000000)  # type: ignore[arg-type]


def test_invalid_years_in_operation_type_raises(make_prospect: ProspectFactory) -> None:
    with pytest.raises(TypeError):
        make_prospect(years_in_operation="5")  # type: ignore[arg-type]
