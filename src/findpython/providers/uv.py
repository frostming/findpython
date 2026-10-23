from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import platformdirs

from findpython.providers.rye import RyeProvider

if TYPE_CHECKING:
    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self


class UvProvider(RyeProvider):
    @classmethod
    def create(cls) -> Self | None:
        default_root_str = platformdirs.user_data_dir("uv", appauthor=False, roaming=True)
        root_str = os.getenv("UV_PYTHON_INSTALL_DIR")
        if root_str is None:
            root = Path(default_root_str).expanduser() / "python"
        else:
            root = Path(root_str).expanduser()
        return cls(root)
