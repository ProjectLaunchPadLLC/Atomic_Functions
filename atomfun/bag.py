# atomfun/bag.py
"""
Bag skeleton for atomfun.

Usage:
    bag = Bag.from_spec({
        "name": "dev",
        "functions": {
            "tokenize_text": "atomfun.text:tokenize",
            "corr": "mylib.math:correlation_matrix"
        }
    })

    # lazy resolve on first access
    bag.tokenize_text("hello world")
"""

from typing import Any, Callable, Dict, Optional
import threading

from .loader import resolve, ResolveError


class ResolutionError(Exception):
    pass


class Bag:
    """
    Bag holds a mapping of attribute names to module_path strings.
    Attributes are resolved lazily via atomfun.loader.resolve and cached.
    """

    def __init__(self, name: str, mapping: Dict[str, str]):
        """
        :param name: Bag name for debugging
        :param mapping: dict attribute_name -> module_path (module:callable)
        """
        self._name = name
        self._mapping = dict(mapping)  # attribute -> module_path
        self._cache: Dict[str, Callable] = {}
        self._lock = threading.RLock()

    @classmethod
    def from_spec(cls, spec: Dict[str, Any]) -> "Bag":
        """
        Create a Bag from a spec dict.

        Expected spec shape:
        {
            "name": "bagname",
            "functions": {
                "alias": "module:callable",
                "other": "package.module:fn"
            }
        }

        The spec may be extended later to accept libraries, categories, or function names.
        """
        name = spec.get("name", "bag")
        functions = spec.get("functions", {})
        if not isinstance(functions, dict):
            raise ValueError("spec['functions'] must be a dict of alias -> module_path")
        return cls(name=name, mapping=functions)

    def __repr__(self) -> str:
        return f"<Bag {self._name} functions={list(self._mapping.keys())}>"

    def _resolve_attr(self, attr: str) -> Callable:
        """
        Resolve attribute to a callable using loader.resolve and cache it.
        """
        if attr not in self._mapping:
            raise AttributeError(f"Bag has no attribute '{attr}'")

        # fast path
        if attr in self._cache:
            return self._cache[attr]

        module_path = self._mapping[attr]
        with self._lock:
            # double-check after acquiring lock
            if attr in self._cache:
                return self._cache[attr]
            try:
                res = resolve(module_path)
            except ResolveError as exc:
                raise ResolutionError(f"Failed to resolve '{module_path}' for attribute '{attr}': {exc}") from exc

            callable_obj = res.get("callable")
            if not callable(callable_obj):
                raise ResolutionError(f"Resolved object for '{attr}' is not callable")

            # cache and return
            self._cache[attr] = callable_obj
            return callable_obj

    def __getattr__(self, attr: str) -> Any:
        """
        Lazily resolve attributes to callables. Returns a wrapper that calls the resolved callable.
        """
        # Only intercept mapped attributes
        if attr in self._mapping:
            fn = self._resolve_attr(attr)

            # Return the callable directly so users can call bag.fn(...)
            return fn

        raise AttributeError(f"{self.__class__.__name__!s} object has no attribute {attr!s}")

    def list_functions(self) -> Dict[str, str]:
        """Return the mapping of attribute -> module_path."""
        return dict(self._mapping)

    def resolved_functions(self) -> Dict[str, Callable]:
        """Return cached resolved callables (may be empty if none resolved yet)."""
        return dict(self._cache)

    def clear_cache(self) -> None:
        """Clear the resolution cache (force re-resolve on next access)."""
        with self._lock:
            self._cache.clear()

