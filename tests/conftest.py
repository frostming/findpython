from __future__ import annotations

import os
import shlex
import sys
import venv
from pathlib import Path
from unittest.mock import PropertyMock

import pytest
from packaging.version import parse

from findpython.providers import ALL_PROVIDERS, PathProvider
from findpython.python import PythonVersion


class _MockRegistry:
    def __init__(self) -> None:
        self.versions: dict[Path, PythonVersion] = {}

    def add_python(
        self,
        executable,
        version=None,
        architecture="64bit",
        interpreter=None,
        keep_symlink=False,
        freethreaded=False,
    ) -> PythonVersion:
        if version is not None:
            version = parse(version)
        executable = Path(executable)
        if interpreter is None:
            interpreter = executable
        executable.parent.mkdir(parents=True, exist_ok=True)
        executable.touch(exist_ok=True)
        executable.chmod(0o744)
        py_ver = PythonVersion(
            executable, version, architecture, interpreter, keep_symlink, freethreaded
        )
        if version is not None:
            py_ver._get_version = lambda: version  # type:ignore[method-assign]
        self.versions[executable] = py_ver
        return py_ver

    def version_maker(self, executable, *args, **kwargs) -> PythonVersion:
        return self.versions[executable]


@pytest.fixture()
def mocked_python(tmp_path, monkeypatch) -> _MockRegistry:
    mocked = _MockRegistry()
    for python in [
        (tmp_path / "python3.7", "3.7.0"),
        (tmp_path / "python3.8", "3.8.0"),
        (tmp_path / "python3.9", "3.9.0"),
    ]:
        mocked.add_python(*python)
    monkeypatch.setattr(
        "findpython.providers.base.BaseProvider.version_maker", mocked.version_maker
    )
    monkeypatch.setattr(
        "findpython.python.PythonVersion.implementation",
        PropertyMock(return_value="cpython"),
    )
    ALL_PROVIDERS.clear()
    ALL_PROVIDERS["path"] = PathProvider
    monkeypatch.setenv("PATH", str(tmp_path))
    return mocked


@pytest.fixture(params=[False, True])
def switch(request) -> bool:
    return request.param


@pytest.fixture()
def python_shims(tmp_path, monkeypatch):
    if os.name == "nt":
        pytest.skip("Shell wrappers and symlinks require POSIX")

    independent_install = tmp_path / "independent install"
    venv.EnvBuilder(with_pip=False).create(independent_install)
    interpreters = [
        Path(sys.executable),
        Path(sys.executable),
        independent_install / "bin" / "python",
    ]
    paths = [tmp_path / f"wrapper {index}" for index in range(len(interpreters))]
    executables = []
    for path, interpreter in zip(paths, interpreters, strict=True):
        path.mkdir()
        executable = path / "python3"
        executable.write_text(f'#!/bin/sh\nexec {shlex.quote(str(interpreter))} "$@"\n')
        executable.chmod(0o755)
        executables.append(executable)

    alias = paths[0] / "python"
    alias.symlink_to("python3")
    executables.append(alias)
    broken = paths[0] / "python3.13"
    broken.write_text("#!/bin/sh\nexit 1\n")
    broken.chmod(0o755)
    monkeypatch.setenv("PATH", os.pathsep.join(str(path) for path in paths))
    return executables, executables[2]
