import sys

import pytest

import findpython
from findpython import Finder


def test_string_version_preserves_architecture(mocked_python, tmp_path):
    expected = mocked_python.add_python(
        tmp_path / "python38", "3.8.0", architecture="32bit"
    )
    finder = Finder()
    assert finder.find_all("3.8", architecture="32bit") == [expected]
    assert finder.find("3.8", architecture="32bit") == expected


@pytest.mark.parametrize("implementation", ["cpython", "pypy"])
def test_string_version_preserves_implementation(mocked_python, implementation):
    found = Finder().find_all("3.8", implementation=implementation)
    assert len(found) == (1 if implementation == "cpython" else 0)


@pytest.mark.parametrize("freethreaded", [None, False, True])
def test_string_version_preserves_threading_filter(mocked_python, tmp_path, freethreaded):
    threaded = mocked_python.add_python(
        tmp_path / "python3.8t", "3.8.0", freethreaded=True
    )
    found = Finder().find_all("3.8", freethreaded=freethreaded)
    expected = (
        threaded if freethreaded else mocked_python.versions[tmp_path / "python3.8"]
    )
    assert found == [expected]


@pytest.mark.parametrize("module_api", [False, True])
def test_find_accepts_threading_filter(mocked_python, tmp_path, module_api):
    expected = mocked_python.add_python(
        tmp_path / "python3.8t", "3.8.0", freethreaded=True
    )
    lookup = findpython.find if module_api else Finder().find
    assert lookup("3.8", freethreaded=True) == expected


def test_embedded_criteria_keep_precedence(mocked_python, tmp_path):
    threaded = mocked_python.add_python(
        tmp_path / "python3.8t", "3.8.0", freethreaded=True
    )
    narrow = mocked_python.add_python(
        tmp_path / "python38", "3.8.0", architecture="32bit"
    )
    finder = Finder()
    assert finder.find_all("3.8t", freethreaded=False) == [threaded]
    assert finder.find_all("3.8-32", architecture="64bit") == [narrow]
    assert finder.find_all("cpython@3.8", implementation="pypy")


def test_string_version_filters_real_interpreters(python_shims):
    finder = Finder(selected_providers=["path"])
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert finder.find_all(version, implementation="missing-implementation") == []
    assert finder.find(version, implementation="missing-implementation") is None
