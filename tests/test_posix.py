from pathlib import Path
import sys

from findpython.finder import Finder
import pytest


pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="Skip POSIX tests on Windows"
)


def test_find_python_resolve_symlinks(mocked_python, tmp_path, switch):
    link = Path(tmp_path / "python")
    link.symlink_to(Path(tmp_path / "python3.7"))
    python = mocked_python.add_python(link, "3.7.0")
    finder = Finder(resolve_symlinks=switch)
    all_pythons = finder.find_all()
    assert len(all_pythons) == 3 if switch else 4
    assert (python in all_pythons) is not switch


def test_find_python_from_asdf(mocked_python, tmp_path, monkeypatch):
    python = mocked_python.add_python(
        tmp_path / ".asdf/installs/python/3.8/bin/python", "3.8.0"
    )
    monkeypatch.setenv("ASDF_DATA_DIR", str(tmp_path / ".asdf"))
    pythons = Finder().find_all(3, 8)
    assert len(pythons) == 2
    assert python in pythons
