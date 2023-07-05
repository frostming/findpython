"""
This package contains all the providers for the pythonfinder module.
"""
from __future__ import annotations

from findpython.providers.asdf import AsdfProvider
from findpython.providers.base import BaseProvider
from findpython.providers.macos import MacOSProvider
from findpython.providers.path import PathProvider
from findpython.providers.pep514 import Pep514Provider
from findpython.providers.pyenv import PyenvProvider

_providers: list[type[BaseProvider]] = [
    # General:
    PathProvider,
    # Tool Specific:
    AsdfProvider,
    PyenvProvider,
    # Windows only:
    Pep514Provider,
    # MacOS only:
    MacOSProvider,
]

ALL_PROVIDERS = {cls.name(): cls for cls in _providers}

__all__ = [cls.__name__ for cls in _providers] + ["ALL_PROVIDERS", "BaseProvider"]
