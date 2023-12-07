from __future__ import annotations

import shutil
import typing as t
from pathlib import Path

from findpython.providers.base import BaseProvider
from findpython.python import PythonVersion
from findpython.utils import WINDOWS, safe_iter_dir


class RyeProvider(BaseProvider):
    def __init__(self) -> None:
        self.root = Path.home() / ".rye"
        self.rye_bin = shutil.which("rye")

    @classmethod
    def create(cls) -> t.Self | None:
        return cls()

    def find_pythons(self) -> t.Iterable[PythonVersion]:
        py_root = self.root / "py"
        if not py_root.exists():
            return
        for child in safe_iter_dir(py_root):
            if child.is_symlink():  # registered an existing python
                continue
            if WINDOWS:
                python_bin = child / "install/python.exe"
            else:
                python_bin = child / "install/bin/python3"
            if python_bin.exists():
                yield self.version_maker(python_bin, _interpreter=python_bin)
