import sys

import pytest
from packaging.version import Version

from findpython import Finder
from findpython.__main__ import cli
from findpython.utils import parse_major


@pytest.mark.parametrize(
    "value", ["3.10.0.dev1", "3.10dev1", "3.10.post1.dev2", "3.10rc1.dev2"]
)
def test_development_criteria_flags(value):
    parsed = parse_major(value)
    assert parsed is not None
    expected = Version(value)
    assert parsed["pre"] == expected.is_prerelease
    assert parsed["dev"] == expected.is_devrelease


@pytest.mark.parametrize("value", ["3.10.0.dev1", "3.10dev1", "3.10.post1.dev2"])
def test_development_criteria_select_development_build(mocked_python, tmp_path, value):
    expected = mocked_python.add_python(tmp_path / "python3.10", value)
    mocked_python.add_python(tmp_path / "python310", "3.10.0rc1")
    mocked_python.add_python(tmp_path / "python3", "3.10.0")
    assert Finder().find(value) == expected


@pytest.mark.parametrize("value", ["3.8junk", "3.8-64junk", "3.8-128"])
def test_version_criteria_do_not_accept_prefixes(mocked_python, value, capsys):
    assert parse_major(value) is None
    assert Finder().find(value) is None
    assert cli([value]) == 1
    assert "No matching python version found" in capsys.readouterr().err


def test_complete_version_criteria_controls():
    parsed = parse_major("cpython@3.13t-64")
    assert parsed is not None
    assert parsed["implementation"] == "cpython"
    assert parsed["architecture"] == "64bit"
    assert parsed["freethreaded"] is True
    assert parsed["pre"] is False
    assert parsed["dev"] is False


def test_real_cli_rejects_trailing_version_text(python_shims, capsys):
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert cli(["--providers", "path", version]) == 0
    capsys.readouterr()
    assert cli(["--providers", "path", f"{version}junk"]) == 1
    assert "No matching python version found" in capsys.readouterr().err
