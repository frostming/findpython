from __future__ import annotations

import platform
import typing as t
from pathlib import Path

from packaging.version import Version

from findpython.providers.base import BaseProvider
from findpython.python import PythonVersion
from findpython.utils import WINDOWS

SYS_ARCHITECTURE = platform.architecture()[0]


class WinregProvider(BaseProvider):
    """A provider that finds Python from the winreg."""

    @classmethod
    def create(cls) -> t.Self | None:
        if not WINDOWS:
            return None
        return cls()

    def find_pythons(self) -> t.Iterable[PythonVersion]:
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
                version = getattr(version.info, "version", None)
                py_ver = self.version_maker(
                    path,
                    Version(version) if version else None,
                    getattr(version.info, "sys_architecture", SYS_ARCHITECTURE),
                    path,
                )
                yield py_ver
