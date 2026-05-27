# atomfun/loader.py
"""
Loader prototype for atomfun.

Responsibilities:
- Normalize module_path forms (module:callable and module.callable)
- Import module and resolve callable attribute
- Basic signature validation against registry signature object
- Return a small descriptor with callable and normalized path
"""

from typing import Any, Dict, Tuple, Optional
import importlib
import inspect
import types


class ResolveError(Exception):
    pass


def _normalize_module_path(module_path: str) -> Tuple[str, str]:
    """
    Normalize module_path into (module, attr_path).
    Accepts:
      - module:callable
      - module.callable
      - module (only if callable attribute is omitted; loader will attempt to find a single callable)
    Returns (module_name, attr_path) where attr_path may be empty string.
    """
    if ":" in module_path:
        module, attr = module_path.split(":", 1)
        return module.strip(), attr.strip()
    if "." in module_path:
        # treat last dot as attribute separator
        parts = module_path.rsplit(".", 1)
        return parts[0].strip(), parts[1].strip()
    # module only
    return module_path.strip(), ""


def resolve(module_path: str) -> Dict[str, Any]:
    """
    Resolve a module_path to a callable.

    Returns a dict:
      {
        "callable": callable_obj,
        "module": module_name,
        "attr_path": attr_path,
        "resolved_path": "module:attr" or "module" if no attr
      }

    Raises ResolveError on failure.
    """
    module_name, attr_path = _normalize_module_path(module_path)
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        raise ResolveError(f"Failed to import module '{module_name}': {exc}") from exc

    if not attr_path:
        # If no attribute specified, attempt to find a single top-level callable:
        # prefer `main`, `run`, or a single exported callable in module globals.
        candidates = []
        for name, val in vars(module).items():
            if callable(val) and not name.startswith("_"):
                candidates.append((name, val))
        # prefer explicit entrypoints
        for preferred in ("main", "run"):
            for name, val in candidates:
                if name == preferred:
                    return {
                        "callable": val,
                        "module": module_name,
                        "attr_path": name,
                        "resolved_path": f"{module_name}:{name}",
                    }
        if len(candidates) == 1:
            name, val = candidates[0]
            return {
                "callable": val,
                "module": module_name,
                "attr_path": name,
                "resolved_path": f"{module_name}:{name}",
            }
        raise ResolveError(
            f"No callable attribute specified and module '{module_name}' has {len(candidates)} public callables; please use module:callable form."
        )

    # resolve nested attributes (e.g., Class.method)
    target = module
    for part in attr_path.split("."):
        if not hasattr(target, part):
            raise ResolveError(f"Attribute '{part}' not found while resolving '{attr_path}' in module '{module_name}'")
        target = getattr(target, part)

    if not callable(target):
        raise ResolveError(f"Resolved attribute '{attr_path}' in module '{module_name}' is not callable")

    return {
        "callable": target,
        "module": module_name,
        "attr_path": attr_path,
        "resolved_path": f"{module_name}:{attr_path}",
    }


def validate_signature(callable_obj: Any, signature: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Basic validation of a registry signature object against the callable's Python signature.

    Checks:
      - All required input names exist in the callable parameters (by name).
      - Warns if callable has required parameters not described in signature.

    Returns (is_valid, message). message is None when valid, otherwise a short explanation.
    """
    if not callable(callable_obj):
        return False, "Provided object is not callable"

    try:
        sig = inspect.signature(callable_obj)
    except (ValueError, TypeError):
        return False, "Unable to obtain Python signature for callable"

    # collect parameter names that are positional-or-keyword or keyword-only
    param_map = {
        name: p for name, p in sig.parameters.items()
        if p.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
    }

    described_inputs = signature.get("inputs", [])
    described_names = [inp.get("name") for inp in described_inputs if "name" in inp]

    # check required inputs exist
    missing = []
    for inp in described_inputs:
        if inp.get("required"):
            name = inp.get("name")
            if name not in param_map:
                missing.append(name)

    if missing:
        return False, f"Signature missing required parameters in callable: {missing}"

    # check for required params in callable not described
    callable_required = []
    for name, p in param_map.items():
        if p.default is inspect._empty and name not in described_names:
            callable_required.append(name)

    if callable_required:
        # not fatal, but warn
        return False, f"Callable has required parameters not described in registry signature: {callable_required}"

    return True, None

