from _typeshed import StrPath
from pathlib import Path
from typing import Sequence

from pep440_rs import Version

class PythonVersion:
    def __init__(
        self,
        executable: StrPath,
        *,
        interpreter: StrPath | None = None,
        version: Version | None = None,
        architecture: str | None = None,
        keep_symlink: bool = False,
    ) -> None: ...
    @property
    def executable(self) -> Path: ...
    @property
    def interpreter(self) -> Path: ...
    @property
    def real_path(self) -> Path: ...
    @property
    def version(self) -> Version: ...
    @property
    def architecture(self) -> str: ...
    def is_valid(self) -> bool: ...
    def matches(
        self,
        major: int | None = None,
        minor: int | None = None,
        patch: int | None = None,
        pre: bool | None = None,
        dev: bool | None = None,
        name: str | None = None,
        architecture: str | None = None,
    ) -> bool: ...
    def __eq__(self, __value: object) -> bool: ...
    def __lt__(self, __value: object) -> bool: ...
    def __hash__(self) -> int: ...

class Finder:
    resolve_symlinks: bool
    same_file: bool
    same_interpreter: bool

    def __init__(
        self,
        resolve_symlinks: bool = False,
        no_same_file: bool = False,
        no_same_interpreter: bool = False,
        selected_providers: Sequence[str] | None = None,
    ) -> None: ...
    def find_all(
        self,
        major: str | int | None = None,
        minor: int | None = None,
        patch: int | None = None,
        pre: bool | None = None,
        dev: bool | None = None,
        name: str | None = None,
        architecture: str | None = None,
    ) -> list[PythonVersion]: ...
    def find(
        self,
        major: str | int | None = None,
        minor: int | None = None,
        patch: int | None = None,
        pre: bool | None = None,
        dev: bool | None = None,
        name: str | None = None,
        architecture: str | None = None,
    ) -> PythonVersion | None: ...
