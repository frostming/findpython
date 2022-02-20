"""
This package contains all the providers for the pythonfinder module.
"""
from typing import List, Type

from findpython.providers.asdf import AsdfProvider
from findpython.providers.base import BaseProvider
from findpython.providers.macos import MacOSProvider
from findpython.providers.path import PathProvider
from findpython.providers.pep514 import Pep514Provider
from findpython.providers.pyenv import PyenvProvider

ALL_PROVIDERS: List[Type[BaseProvider]] = [
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

__all__ = [cls.__name__ for cls in ALL_PROVIDERS] + ["ALL_PROVIDERS", "BaseProvider"]
