from __future__ import annotations

import os
import typing as t
from pathlib import Path

from findpython.providers.base import BaseProvider
from findpython.python import PythonVersion
from findpython.utils import WINDOWS, safe_iter_dir


class UvProvider(BaseProvider):
    def __init__(self, root: Path) -> None:
        self.root = root

    @classmethod
    def create(cls) -> t.Self | None:
        # See uv#13877(https://github.com/astral-sh/uv/issues/13877)
        if WINDOWS:
            default_root_str = os.getenv("APPDATA")
        else:
            default_root_str = "~/.local/share"
        assert default_root_str is not None
        root_str = os.getenv("UV_PYTHON_INSTALL_DIR")
        if root_str is None:
            root_str = os.getenv("XDG_DATA_HOME")
            if root_str is None:
                root_str = default_root_str
            root = Path(root_str).expanduser() / "uv" / "python"
        else:
            root = Path(root_str).expanduser()
        print(f"{root = }")
        return cls(root)

    def find_pythons(self) -> t.Iterable[PythonVersion]:
        if not self.root.exists():
            return
        for child in safe_iter_dir(self.root):
            for intermediate in ("", "install/"):
                if WINDOWS:
                    python_bin = child / (intermediate + "python.exe")
                else:
                    python_bin = child / (intermediate + "bin/python3")
                if python_bin.exists():
                    yield self.version_maker(python_bin, _interpreter=python_bin)
                    break
