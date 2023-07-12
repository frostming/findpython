import abc
from pathlib import Path
from typing import Any, Sequence

from _typeshed import StrPath

ALL_PROVIDERS: list[str]

class Version:
    dev: Any
    epoch: Any
    post: Any
    pre: Any
    release: Any
    major: Any
    minor: Any
    micro: Any

    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...
    def any_prerelease(self, *args, **kwargs) -> Any: ...
    def parse_star(self, *args, **kwargs) -> Any: ...
    def __eq__(self, other) -> Any: ...
    def __ge__(self, other) -> Any: ...
    def __gt__(self, other) -> Any: ...
    def __hash__(self) -> Any: ...
    def __le__(self, other) -> Any: ...
    def __lt__(self, other) -> Any: ...
    def __ne__(self, other) -> Any: ...

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
    def add_provider(self, provider: BaseProvider, pos: int | None = None) -> None: ...

def find_all(
    major: str | int | None = None,
    minor: int | None = None,
    patch: int | None = None,
    pre: bool | None = None,
    dev: bool | None = None,
    name: str | None = None,
    architecture: str | None = None,
) -> list[PythonVersion]: ...
def find(
    major: str | int | None = None,
    minor: int | None = None,
    patch: int | None = None,
    pre: bool | None = None,
    dev: bool | None = None,
    name: str | None = None,
    architecture: str | None = None,
) -> PythonVersion | None: ...

class BaseProvider(abc.ABC):
    @abc.abstractmethod
    def find_pythons(self) -> list[PythonVersion]: ...
    def find_pythons_from_path(
        self, path: StrPath, as_interpreter: bool = False
    ) -> list[PythonVersion]: ...
