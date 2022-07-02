from pathlib import Path

import pytest
from packaging.version import parse

from findpython.providers import ALL_PROVIDERS, PathProvider
from findpython.python import PythonVersion


class _MockRegistry:
    def __init__(self) -> None:
        self.versions = {}

    def add_python(
        self,
        executable,
        version=None,
        architecture="64bit",
        interpreter=None,
        keep_symlink=False,
    ):
        if version is not None:
            version = parse(version)
        executable = Path(executable)
        if interpreter is None:
            interpreter = executable
        executable.parent.mkdir(parents=True, exist_ok=True)
        executable.touch(exist_ok=True)
        executable.chmod(0o744)
        py_ver = PythonVersion(
            executable, version, architecture, interpreter, keep_symlink
        )
        if version is not None:
            py_ver._get_version = lambda: version
        self.versions[executable] = py_ver
        return py_ver

    def version_maker(self, executable, *args, **kwargs):
        return self.versions[executable]


@pytest.fixture()
def mocked_python(tmp_path, monkeypatch):
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
    ALL_PROVIDERS[:] = [PathProvider]
    monkeypatch.setenv("PATH", str(tmp_path))
    return mocked


@pytest.fixture(params=[False, True])
def switch(request):
    return request.param
