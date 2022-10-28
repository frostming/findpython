from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Type

from findpython.providers.base import BaseProvider, T
from findpython.python import PythonVersion


class PyenvProvider(BaseProvider):
    """A provider that finds python installed with pyenv"""

    def __init__(self, root: Path) -> None:
        self.root = root

    @classmethod
    def create(cls: Type[T]) -> T | None:
        pyenv_root = os.path.expanduser(
            os.path.expandvars(os.getenv("PYENV_ROOT", "~/.pyenv"))
        )
        if not os.path.exists(pyenv_root):
            return None
        return cls(Path(pyenv_root))

    def find_pythons(self) -> Iterable[PythonVersion]:
        versions_path = self.root.joinpath("versions")
        if versions_path.exists():
            for version in versions_path.iterdir():
                if version.is_dir():
                    bindir = version / "bin"
                    if not bindir.exists():
                        bindir = version
                    yield from self.find_pythons_from_path(bindir, True)
