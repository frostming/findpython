from __future__ import annotations

import platform
from pathlib import Path
from typing import Iterable, Type

from findpython.providers.base import BaseProvider, T
from findpython.python import PythonVersion
from findpython.utils import WINDOWS

SYS_ARCHITECTURE = platform.architecture()[0]


class Pep514Provider(BaseProvider):
    """A provider that finds Python from the winreg."""

    @classmethod
    def create(cls: Type[T]) -> T | None:
        if not WINDOWS:
            return None
        return cls()

    def find_pythons(self) -> Iterable[PythonVersion]:
        from findpython.pep514tools import findall as pep514_findall

        env_versions = pep514_findall()
        for version in env_versions:
            install_path = getattr(version.info, "install_path", None)
            if install_path is None:
                continue
            try:
                path = Path(install_path.executable_path)
            except AttributeError:
                continue
            if path.exists():
                py_ver = self.version_maker(
                    path,
                    None,
                    getattr(version.info, "sys_architecture", SYS_ARCHITECTURE),
                    path,
                )
                yield py_ver
