import stat
import sys
from pathlib import Path

import pytest

from findpython import register_provider
from findpython.finder import Finder
from findpython.providers.asdf import AsdfProvider
from findpython.providers.pyenv import PyenvProvider
from findpython.providers.rye import RyeProvider

if sys.platform == "win32":
    pytest.skip("Skip POSIX tests on Windows", allow_module_level=True)


def test_find_python_resolve_symlinks(mocked_python, tmp_path, switch):
    link = Path(tmp_path / "python")
    link.symlink_to(Path(tmp_path / "python3.7"))
    python = mocked_python.add_python(link, "3.7.0")
    finder = Finder(resolve_symlinks=switch)
    all_pythons = finder.find_all()
    assert len(all_pythons) == (3 if switch else 4)
    assert (python in all_pythons) is not switch


def test_find_python_from_asdf(mocked_python, tmp_path, monkeypatch):
    register_provider(AsdfProvider)
    python = mocked_python.add_python(
        tmp_path / ".asdf/installs/python/3.8/bin/python", "3.8.0"
    )
    monkeypatch.setenv("ASDF_DATA_DIR", str(tmp_path / ".asdf"))
    pythons = Finder().find_all(3, 8)
    assert len(pythons) == 2
    assert python in pythons


def test_find_python_exclude_unreadable(mocked_python, tmp_path):
    python = Path(tmp_path / "python3.8")
    python.chmod(python.stat().st_mode & ~stat.S_IRUSR)
    try:
        finder = Finder()
        all_pythons = finder.find_all()
        assert len(all_pythons) == 2, all_pythons
        assert python not in [version.executable for version in all_pythons]
    finally:
        python.chmod(0o744)


def test_find_python_from_provider(mocked_python, tmp_path, monkeypatch):
    register_provider(AsdfProvider)
    register_provider(PyenvProvider)
    python38 = mocked_python.add_python(
        tmp_path / ".asdf/installs/python/3.8/bin/python", "3.8.0"
    )
    python381 = mocked_python.add_python(
        tmp_path / ".pyenv/versions/3.8.1/bin/python", "3.8.1"
    )
    python382 = mocked_python.add_python(
        tmp_path / ".asdf/installs/python/3.8.2/bin/python", "3.8.2"
    )
    monkeypatch.setenv("ASDF_DATA_DIR", str(tmp_path / ".asdf"))
    monkeypatch.setenv("PYENV_ROOT", str(tmp_path / ".pyenv"))

    pythons = Finder(selected_providers=["pyenv", "asdf"]).find_all(3, 8)
    assert len(pythons) == 3
    assert python38 in pythons
    assert python381 in pythons
    assert python382 in pythons

    asdf_pythons = Finder(selected_providers=["asdf"]).find_all(3, 8)
    assert len(asdf_pythons) == 2
    assert python38 in asdf_pythons
    assert python382 in asdf_pythons

    pyenv_pythons = Finder(selected_providers=["pyenv"]).find_all(3, 8)
    assert len(pyenv_pythons) == 1
    assert python381 in pyenv_pythons


def test_find_python_from_rye_provider(mocked_python, tmp_path, monkeypatch):
    python310 = mocked_python.add_python(
        tmp_path / ".rye/py/cpython@3.10.9/install/bin/python3", "3.10.9"
    )
    python311 = mocked_python.add_python(
        tmp_path / ".rye/py/cpython@3.11.8/bin/python3", "3.11.8"
    )
    monkeypatch.setenv("HOME", str(tmp_path))

    register_provider(RyeProvider)
    find_310 = Finder(selected_providers=["rye"]).find_all(3, 10)
    assert python310 in find_310

    find_311 = Finder(selected_providers=["rye"]).find_all(3, 11)
    assert python311 in find_311
