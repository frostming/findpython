import os
from pathlib import Path

import pytest
from packaging.version import Version

from findpython import Finder
from findpython.providers import ALL_PROVIDERS
from findpython.providers.pyenv import PyenvProvider


def test_find_pythons(mocked_python, tmp_path):
    finder = Finder()
    all_pythons = finder.find_all()
    assert len(all_pythons) == 3
    assert all_pythons[0].executable == Path(tmp_path / "python3.9")
    assert all_pythons[0].version == Version("3.9.0")
    assert all_pythons[1].executable == Path(tmp_path / "python3.8")
    assert all_pythons[1].version == Version("3.8.0")
    assert all_pythons[2].executable == Path(tmp_path / "python3.7")
    assert all_pythons[2].version == Version("3.7.0")


def test_find_python_by_version(mocked_python, tmp_path):
    finder = Finder()
    python = finder.find(3, 8)
    assert python.executable == Path(tmp_path / "python3.8")
    assert python.version == Version("3.8.0")

    assert finder.find("3.8") == python
    assert finder.find("3.8.0") == python
    assert finder.find("python3.8") == python


def test_find_python_by_version_not_found(mocked_python, tmp_path):
    finder = Finder()
    python = finder.find(3, 10)
    assert python is None


def test_find_python_by_architecture(mocked_python, tmp_path):
    python = mocked_python.add_python(
        tmp_path / "python38", "3.8.0", architecture="32bit"
    )
    finder = Finder()
    assert finder.find(3, 8, architecture="32bit") == python
    assert finder.find(3, 8, architecture="64bit").executable == tmp_path / "python3.8"


def test_find_python_with_prerelease(mocked_python, tmp_path):
    python = mocked_python.add_python(tmp_path / "python3.10", "3.10.0.a1")
    finder = Finder()
    assert python == finder.find(pre=True)


def test_find_python_with_devrelease(mocked_python, tmp_path):
    python = mocked_python.add_python(tmp_path / "python3.10", "3.10.0.dev1")
    finder = Finder()
    assert python == finder.find(dev=True)


def test_find_python_with_non_existing_path(mocked_python, monkeypatch):
    monkeypatch.setenv("PATH", "/non/existing/path" + os.pathsep + os.environ["PATH"])
    finder = Finder()
    all_pythons = finder.find_all()
    assert len(all_pythons) == 3


def test_find_python_exclude_invalid(mocked_python, tmp_path):
    python = mocked_python.add_python(tmp_path / "python3.10")
    finder = Finder()
    all_pythons = finder.find_all()
    assert len(all_pythons) == 3
    assert python not in all_pythons


def test_find_python_deduplicate_same_file(mocked_python, tmp_path, switch):
    for i, python in enumerate(mocked_python.versions):
        python.write_bytes(str(i).encode())

    new_python = mocked_python.add_python(tmp_path / "python3", "3.9.0")
    new_python.executable.write_bytes(b"0")

    finder = Finder(no_same_file=switch)
    all_pythons = finder.find_all()
    assert len(all_pythons) == (3 if switch else 4)
    assert (new_python in all_pythons) is not switch


@pytest.mark.skipif(os.name == "nt", reason="Not supported on Windows")
def test_find_python_deduplicate_symlinks(mocked_python, tmp_path):
    python = mocked_python.add_python(tmp_path / "python3.9", "3.9.0")
    (tmp_path / "python3").symlink_to(python.executable)
    symlink1 = mocked_python.add_python(tmp_path / "python3", "3.9.0")
    (tmp_path / "python").symlink_to(python.executable)
    symlink2 = mocked_python.add_python(tmp_path / "python", "3.9.0", keep_symlink=True)
    finder = Finder(resolve_symlinks=True)
    all_pythons = finder.find_all()
    assert python in all_pythons
    assert symlink1 not in all_pythons
    assert symlink2 in all_pythons


def test_find_python_deduplicate_same_interpreter(mocked_python, tmp_path, switch):
    if os.name == "nt":
        suffix = ".bat"
    else:
        suffix = ".sh"
    python = mocked_python.add_python(
        tmp_path / f"python{suffix}", "3.9.0", interpreter=tmp_path / "python3.9"
    )

    finder = Finder(no_same_interpreter=switch)
    all_pythons = finder.find_all()
    assert len(all_pythons) == (3 if switch else 4)
    assert (python in all_pythons) is not switch


def test_find_python_from_pyenv(mocked_python, tmp_path, monkeypatch):
    ALL_PROVIDERS.append(PyenvProvider)
    python = mocked_python.add_python(
        tmp_path / ".pyenv/versions/3.8/bin/python", "3.8.0"
    )
    monkeypatch.setenv("PYENV_ROOT", str(tmp_path / ".pyenv"))
    pythons = Finder().find_all(3, 8)
    assert len(pythons) == 2
    assert python in pythons


def test_find_python_skips_empty_pyenv(mocked_python, tmp_path, monkeypatch):
    ALL_PROVIDERS.append(PyenvProvider)
    pyenv_path = Path(tmp_path / ".pyenv")
    pyenv_path.mkdir()
    monkeypatch.setenv("PYENV_ROOT", str(pyenv_path))
    all_pythons = Finder().find_all()
    assert len(all_pythons) == 3
