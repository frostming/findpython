from __future__ import annotations

import os
import typing as t
from pathlib import Path

from findpython.providers.rye import RyeProvider
from findpython.utils import WINDOWS


class UvProvider(RyeProvider):
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
        return cls(root)
