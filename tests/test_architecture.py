"""Guard for the architecture decision: the library depends on the stdlib only."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

PACKAGE_NAME = "crm_prospect_qualifier"
PACKAGE_DIR = Path(__file__).resolve().parent.parent / "src" / PACKAGE_NAME

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="sys.stdlib_module_names requires Python 3.10+",
)


def find_non_stdlib_imports(package_dir: Path, package_name: str) -> list[str]:
    stdlib = set(sys.stdlib_module_names) if sys.version_info >= (3, 10) else set()
    violations: list[str] = []

    for path in sorted(package_dir.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    continue  # relative import within the package
                modules = [node.module or ""]
            else:
                continue

            for module in modules:
                top_level = module.split(".")[0]
                if top_level in stdlib or top_level == package_name:
                    continue
                violations.append(f"{path.name}:{node.lineno} imports {module!r}")

    return violations


def test_package_imports_only_stdlib() -> None:
    py_files = list(PACKAGE_DIR.rglob("*.py"))
    assert py_files, f"no Python files found under {PACKAGE_DIR}"
    assert find_non_stdlib_imports(PACKAGE_DIR, PACKAGE_NAME) == []


def test_guard_detects_non_stdlib_imports(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text(
        "import os\n"
        "import requests\n"
        "from sqlalchemy.orm import Session\n"
        "from . import models\n"
        f"from {PACKAGE_NAME}.models import Prospect\n",
        encoding="utf-8",
    )

    violations = find_non_stdlib_imports(tmp_path, PACKAGE_NAME)

    assert violations == [
        "bad.py:2 imports 'requests'",
        "bad.py:3 imports 'sqlalchemy.orm'",
    ]
