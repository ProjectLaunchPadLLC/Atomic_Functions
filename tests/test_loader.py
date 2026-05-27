# tests/test_loader.py
import sys
import importlib
import textwrap
from pathlib import Path
import tempfile
import types

import pytest

from atomfun.loader import resolve, ResolveError, validate_signature


def _make_temp_module(tmp_path, module_name="temp_mod"):
    """
    Create a temporary python module file under tmp_path and add tmp_path to sys.path.
    Returns module import name.
    """
    module_file = tmp_path / f"{module_name}.py"
    module_code = textwrap.dedent(
        """
        def simple(a, b=2):
            return a + b

        def main(x):
            return x

        class C:
            @staticmethod
            def stat(y):
                return y*2
        """
    )
    module_file.write_text(module_code, encoding="utf-8")
    sys.path.insert(0, str(tmp_path))
    return module_name


def test_resolve_module_colon(tmp_path):
    name = _make_temp_module(tmp_path, "mod_colon")
    mod = importlib.import_module(name)
    # resolve explicit function
    res = resolve(f"{name}:simple")
    assert callable(res["callable"])
    assert res["attr_path"] == "simple"
    assert res["resolved_path"].endswith(":simple")


def test_resolve_module_dot(tmp_path):
    name = _make_temp_module(tmp_path, "mod_dot")
    # resolve class staticmethod
    res = resolve(f"{name}.C.stat")
    assert callable(res["callable"])
    assert res["attr_path"] == "C.stat"
    assert res["resolved_path"].endswith(":C.stat")


def test_resolve_module_no_attr_uses_main(tmp_path):
    name = _make_temp_module(tmp_path, "mod_main")
    res = resolve(name)  # module only, should pick main
    assert callable(res["callable"])
    assert res["attr_path"] == "main"


def test_resolve_missing_module(tmp_path):
    with pytest.raises(Exception):
        resolve("nonexistent_module:foo")


def test_resolve_missing_attr(tmp_path):
    name = _make_temp_module(tmp_path, "mod_missing_attr")
    with pytest.raises(Exception):
        resolve(f"{name}:no_such_attr")


def test_validate_signature_ok(tmp_path):
    name = _make_temp_module(tmp_path, "mod_sig_ok")
    res = resolve(f"{name}:simple")
    callable_obj = res["callable"]
    signature = {
        "inputs": [
            {"name": "a", "type": "int", "required": True},
            {"name": "b", "type": "int", "required": False},
        ],
        "output": {"type": "int"},
    }
    ok, msg = validate_signature(callable_obj, signature)
    assert ok is True
    assert msg is None


def test_validate_signature_missing_param(tmp_path):
    name = _make_temp_module(tmp_path, "mod_sig_missing")
    res = resolve(f"{name}:simple")
    callable_obj = res["callable"]
    signature = {
        "inputs": [
            {"name": "x", "type": "int", "required": True},
        ],
        "output": {"type": "int"},
    }
    ok, msg = validate_signature(callable_obj, signature)
    assert ok is False
    assert "missing" in msg or "not described" in msg

