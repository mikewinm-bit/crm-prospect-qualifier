"""Acceptance tests for qualify_prospects (ECC decision mem_20261002_a3c91e5b7d2f4086b1e4)."""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from typing import get_type_hints

import pytest
from conftest import ProspectFactory

import crm_prospect_qualifier
from crm_prospect_qualifier import (
    MIN_ANNUAL_TURNOVER,
    MIN_YEARS_IN_OPERATION,
    CreditCheckStatus,
    Prospect,
    QualificationResult,
    qualify_prospect,
    qualify_prospects,
)


def test_empty_input_returns_empty_list() -> None:
    result = qualify_prospects([])
    assert result == []
    assert isinstance(result, list)


def test_single_item_matches_qualify_prospect(make_prospect: ProspectFactory) -> None:
    prospect = make_prospect()
    assert qualify_prospects([prospect]) == [qualify_prospect(prospect)]


def test_all_qualifying_batch(make_prospect: ProspectFactory) -> None:
    results = qualify_prospects(
        [make_prospect(company_name=f"Co {i}") for i in range(3)]
    )
    assert len(results) == 3
    assert all(r.qualified is True and r.reasons == [] for r in results)


def test_all_failing_batch(make_prospect: ProspectFactory) -> None:
    results = qualify_prospects([make_prospect(years_in_operation=0) for _ in range(3)])
    assert len(results) == 3
    assert all(r.qualified is False for r in results)


def test_mixed_batch_preserves_input_order(make_prospect: ProspectFactory) -> None:
    prospects = [
        make_prospect(company_name="A"),
        make_prospect(company_name="B", years_in_operation=0),
        make_prospect(company_name="C"),
        make_prospect(company_name="D", credit_check_status=CreditCheckStatus.FAILED),
    ]
    results = qualify_prospects(prospects)
    assert [r.qualified for r in results] == [True, False, True, False]


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (CreditCheckStatus.PASSED, True),
        (CreditCheckStatus.FAILED, False),
        (CreditCheckStatus.PENDING, False),
    ],
)
def test_only_passed_credit_status_qualifies(
    make_prospect: ProspectFactory, status: CreditCheckStatus, expected: bool
) -> None:
    (result,) = qualify_prospects([make_prospect(credit_check_status=status)])
    assert result.qualified is expected


def test_reasons_accumulate_in_single_prospect_order(
    make_prospect: ProspectFactory,
) -> None:
    prospect = make_prospect(
        annual_turnover=Decimal(1000),
        years_in_operation=0,
        credit_check_status=CreditCheckStatus.FAILED,
    )
    (result,) = qualify_prospects([prospect])
    assert len(result.reasons) == 3
    assert result.reasons == qualify_prospect(prospect).reasons


def test_results_match_qualify_prospect_for_each_item(
    make_prospect: ProspectFactory,
) -> None:
    prospects = [
        make_prospect(),
        make_prospect(annual_turnover=Decimal(1)),
        make_prospect(credit_check_status=CreditCheckStatus.PENDING),
    ]
    results = qualify_prospects(prospects)
    assert len(results) == len(prospects)
    for prospect, result in zip(prospects, results):
        assert result == qualify_prospect(prospect)


def test_delegates_each_item_to_qualify_prospect(
    make_prospect: ProspectFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[Prospect] = []

    def fake(prospect: Prospect) -> QualificationResult:
        seen.append(prospect)
        return QualificationResult(qualified=True, reasons=["stub"])

    monkeypatch.setattr("crm_prospect_qualifier.qualification.qualify_prospect", fake)
    prospects = [make_prospect(company_name="A"), make_prospect(company_name="B")]
    results = qualify_prospects(prospects)
    assert seen == prospects
    assert [r.reasons for r in results] == [["stub"], ["stub"]]


def test_threshold_boundaries(make_prospect: ProspectFactory) -> None:
    at_limit = make_prospect(
        annual_turnover=MIN_ANNUAL_TURNOVER, years_in_operation=MIN_YEARS_IN_OPERATION
    )
    below_turnover = make_prospect(annual_turnover=MIN_ANNUAL_TURNOVER - Decimal(1))
    below_years = make_prospect(years_in_operation=MIN_YEARS_IN_OPERATION - 1)
    results = qualify_prospects([at_limit, below_turnover, below_years])
    assert [r.qualified for r in results] == [True, False, False]


def test_duplicate_prospect_yields_independent_results(
    make_prospect: ProspectFactory,
) -> None:
    prospect = make_prospect(years_in_operation=0)
    first, second = qualify_prospects([prospect, prospect])
    assert first == second
    assert first is not second
    first.reasons.append("mutated")
    assert "mutated" not in second.reasons


@pytest.mark.parametrize("wrap", [list, tuple, iter, lambda ps: (p for p in ps)])
def test_accepts_any_iterable(make_prospect: ProspectFactory, wrap) -> None:  # type: ignore[no-untyped-def]
    prospects = [make_prospect(), make_prospect(years_in_operation=0)]
    results = qualify_prospects(wrap(prospects))
    assert [r.qualified for r in results] == [True, False]


def test_input_list_is_not_mutated(make_prospect: ProspectFactory) -> None:
    prospects = [make_prospect(company_name="A"), make_prospect(company_name="B")]
    snapshot = list(prospects)
    qualify_prospects(prospects)
    assert prospects == snapshot


@pytest.mark.parametrize("bad", [None, {"company_name": "X"}, "text", 42])
def test_non_prospect_element_raises_type_error_with_index(
    make_prospect: ProspectFactory, bad: object
) -> None:
    with pytest.raises(TypeError, match=r"index 1"):
        qualify_prospects([make_prospect(), bad])  # type: ignore[list-item]


@pytest.mark.parametrize("bad_input", ["abc", b"ab"])
def test_str_and_bytes_input_raise_type_error(bad_input: object) -> None:
    with pytest.raises(TypeError, match=r"index 0"):
        qualify_prospects(bad_input)  # type: ignore[arg-type]


def test_fails_fast_without_consuming_past_bad_element(
    make_prospect: ProspectFactory,
) -> None:
    consumed: list[int] = []

    def source() -> Iterator[object]:
        consumed.append(0)
        yield make_prospect()
        consumed.append(1)
        yield "not a prospect"
        consumed.append(2)
        yield make_prospect()

    with pytest.raises(TypeError):
        qualify_prospects(source())  # type: ignore[arg-type]
    assert consumed == [0, 1]


def test_generator_is_consumed_once(make_prospect: ProspectFactory) -> None:
    pulled: list[int] = []

    def source() -> Iterator[Prospect]:
        for i in range(3):
            pulled.append(i)
            yield make_prospect(company_name=f"Co {i}")

    assert len(qualify_prospects(source())) == 3
    assert pulled == [0, 1, 2]


def test_exported_from_package_root() -> None:
    assert "qualify_prospects" in crm_prospect_qualifier.__all__
    assert crm_prospect_qualifier.qualify_prospects is qualify_prospects


def test_signature_is_annotated() -> None:
    hints = get_type_hints(qualify_prospects)
    assert hints["return"] == list[QualificationResult]
    assert "prospects" in hints
