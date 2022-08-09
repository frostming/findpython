import stat
import sys
from pathlib import Path

import pytest

from findpython.finder import Finder
from findpython.providers import ALL_PROVIDERS
from findpython.providers.asdf import AsdfProvider

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
    ALL_PROVIDERS.append(AsdfProvider)
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
