# CRM Prospect Qualification Module (Prototype)

A standalone prototype for qualifying sales prospects for a fictional
chemical distributor. Pure in-memory logic — **no database, API, SAP,
Odoo, or network integration of any kind.**

## Qualification rules

A `Prospect` qualifies when **all** of the following hold:

1. `annual_turnover >= R5,000,000`
2. `years_in_operation >= 3`
3. `credit_check_status == PASSED` (both `FAILED` and `PENDING` disqualify)

## Setup

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install pytest   # Windows
# or: source .venv/bin/activate && pip install pytest   # macOS/Linux
```

## Running the tests

```bash
./.venv/Scripts/python.exe -m pytest -v
```

## Usage example

```python
from decimal import Decimal

from crm_prospect_qualifier import (
    CreditCheckStatus,
    Prospect,
    Province,
    qualify_prospect,
)

prospect = Prospect(
    company_name="Acme Chemicals",
    annual_turnover=Decimal("6000000"),
    years_in_operation=5,
    industry="Manufacturing",
    province=Province.GAUTENG,
    credit_check_status=CreditCheckStatus.PASSED,
)

result = qualify_prospect(prospect)
print(result.qualified)  # True
print(result.reasons)    # []

disqualified = Prospect(
    company_name="Fledgling Chemicals",
    annual_turnover=Decimal("2000000"),
    years_in_operation=1,
    industry="Agriculture",
    province=Province.WESTERN_CAPE,
    credit_check_status=CreditCheckStatus.PENDING,
)

result = qualify_prospect(disqualified)
print(result.qualified)  # False
print(result.reasons)
# [
#   "annual_turnover 2000000 is below minimum 5000000",
#   "years_in_operation 1 is below minimum 3",
#   "credit_check_status 'pending' is not 'passed'",
# ]
```

## Project structure

```
projects/crm-prospect-qualifier/
├── README.md
├── pyproject.toml
├── src/
│   └── crm_prospect_qualifier/
│       ├── __init__.py
│       ├── models.py           # Province, CreditCheckStatus, Prospect, QualificationResult
│       └── qualification.py    # MIN_ANNUAL_TURNOVER, MIN_YEARS_IN_OPERATION, qualify_prospect()
└── tests/
    ├── test_models.py
    └── test_qualification.py
```
