from __future__ import annotations

import abc
import logging
from pathlib import Path
from typing import Callable, Iterable, Type, TypeVar

from findpython.python import PythonVersion
from findpython.utils import path_is_python, path_is_readable

T = TypeVar("T", bound="BaseProvider")
logger = logging.getLogger("findpython")


class BaseProvider(metaclass=abc.ABCMeta):
    """The base class for python providers"""

    version_maker: Callable[..., PythonVersion] = PythonVersion

    @abc.abstractclassmethod
    def create(cls: Type[T]) -> T | None:
        """Return an instance of the provider or None if it is not available"""
        pass

    @abc.abstractmethod
    def find_pythons(self) -> Iterable[PythonVersion]:
        """Return the python versions found by the provider"""
        pass

    @classmethod
    def find_pythons_from_path(
        cls, path: Path, as_interpreter: bool = False
    ) -> Iterable[PythonVersion]:
        """A general helper method to return pythons under a given path.

        :param path: The path to search for pythons
        :param as_interpreter: Use the path as the interpreter path.
            If the pythons might be a wrapper script, don't set this to True.
        :returns: An iterable of PythonVersion objects
        """
        if not path_is_readable(path) or not path.is_dir():
            logger.debug("Invalid path or unreadable: %s", path)
            return iter([])
        return (
            cls.version_maker(
                child.absolute(),
                _interpreter=child.absolute() if as_interpreter else None,
            )
            for child in path.iterdir()
            if path_is_python(child)
        )
