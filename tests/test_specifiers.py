import sys

import pytest
from packaging.specifiers import SpecifierSet
from packaging.version import Version

import findpython
from findpython import Finder


@pytest.mark.parametrize(
    ("specifier", "versions"),
    [
        (">=3.8,<3.10", ["3.9.0", "3.8.0"]),
        ("==3.8.*", ["3.8.0"]),
        ("!=3.8.0", ["3.9.0", "3.7.0"]),
        ("~=3.8.0", ["3.8.0"]),
        ("===3.8.0", ["3.8.0"]),
        (">3.7,<=3.9", ["3.9.0", "3.8.0"]),
        ("<3.7", []),
        ("", ["3.9.0", "3.8.0", "3.7.0"]),
    ],
)
def test_find_by_specifier_set(mocked_python, specifier, versions):
    specifier_set = SpecifierSet(specifier)
    expected = [Version(version) for version in versions]
    finder = Finder()

    assert [python.version for python in finder.find_all(specifier_set)] == expected
    best = finder.find(specifier_set)
    assert (best.version if best else None) == (expected[0] if expected else None)
    assert [python.version for python in findpython.find_all(specifier_set)] == expected
    best = findpython.find(specifier_set)
    assert (best.version if best else None) == (expected[0] if expected else None)


@pytest.mark.parametrize(
    ("specifier", "prereleases", "allow_prereleases", "expected"),
    [
        (">=3.7", None, False, ["3.9.0", "3.8.0", "3.7.0"]),
        (">=3.7", False, False, ["3.9.0", "3.8.0", "3.7.0"]),
        (">=3.7", True, False, ["3.10.0rc1", "3.10.0.dev1", "3.9.0", "3.8.0", "3.7.0"]),
        (">=3.7", None, True, ["3.10.0rc1", "3.10.0.dev1", "3.9.0", "3.8.0", "3.7.0"]),
        (">=3.7", False, True, ["3.10.0rc1", "3.10.0.dev1", "3.9.0", "3.8.0", "3.7.0"]),
        (">=3.10.0rc1", None, False, ["3.10.0rc1"]),
    ],
)
def test_specifier_set_prerelease_policy(
    mocked_python, tmp_path, specifier, prereleases, allow_prereleases, expected
):
    mocked_python.add_python(tmp_path / "python3.10", "3.10.0rc1")
    mocked_python.add_python(tmp_path / "python3.11", "3.10.0.dev1")
    specifier_set = SpecifierSet(specifier, prereleases=prereleases)

    found = Finder().find_all(specifier_set, allow_prereleases=allow_prereleases)

    assert [python.version for python in found] == [Version(v) for v in expected]
    assert (
        specifier_set.prereleases
        == SpecifierSet(specifier, prereleases=prereleases).prereleases
    )


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"minor": 8}, ["3.8.0"]),
        ({"patch": 0}, ["3.9.0", "3.8.0", "3.7.0"]),
        ({"name": "python3.8"}, ["3.8.0"]),
        ({"architecture": "32bit"}, ["3.9.1"]),
        ({"implementation": "pypy"}, []),
        ({"implementation": "cpython", "freethreaded": True}, ["3.9.2"]),
        ({"freethreaded": False}, ["3.9.1", "3.9.0", "3.8.0", "3.7.0"]),
    ],
)
def test_specifier_set_combines_other_criteria(mocked_python, tmp_path, kwargs, expected):
    mocked_python.add_python(tmp_path / "python3.9-32", "3.9.1", architecture="32bit")
    mocked_python.add_python(tmp_path / "python3.9t", "3.9.2", freethreaded=True)

    found = Finder().find_all(SpecifierSet(">=3.7,<3.10"), **kwargs)

    assert [python.version for python in found] == [Version(v) for v in expected]


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"pre": True}, ["3.10.0rc1", "3.10.0.dev1"]),
        ({"dev": True}, ["3.10.0.dev1"]),
        ({"pre": True, "dev": False}, ["3.10.0rc1"]),
        ({"pre": False, "dev": False}, ["3.9.0", "3.8.0", "3.7.0"]),
    ],
)
def test_specifier_set_combines_pre_and_dev(mocked_python, tmp_path, kwargs, expected):
    mocked_python.add_python(tmp_path / "python3.10", "3.10.0rc1")
    mocked_python.add_python(tmp_path / "python3.11", "3.10.0.dev1")

    found = Finder().find_all(SpecifierSet(">=3.7", prereleases=True), **kwargs)

    assert [python.version for python in found] == [Version(v) for v in expected]


def test_specifier_set_pre_filter_does_not_enable_prereleases(mocked_python, tmp_path):
    mocked_python.add_python(tmp_path / "python3.10", "3.10.0rc1")

    assert Finder().find_all(SpecifierSet(">=3.7", prereleases=False), pre=True) == []


@pytest.mark.parametrize("criteria", [{"pre": False}, {"dev": False}])
def test_specifier_set_preserves_conflicting_prerelease_error(mocked_python, criteria):
    with pytest.raises(ValueError, match="must not be False"):
        Finder().find_all(SpecifierSet(">=3.7"), allow_prereleases=True, **criteria)


@pytest.mark.parametrize("dedup", ["no_same_file", "no_same_interpreter"])
def test_specifier_set_keeps_deduplication(mocked_python, tmp_path, dedup):
    for path, python in mocked_python.versions.items():
        path.write_bytes(str(python.version).encode())
    original = mocked_python.versions[tmp_path / "python3.9"]
    duplicate = mocked_python.add_python(
        tmp_path / "python3", "3.9.0", interpreter=original.executable
    )
    duplicate.executable.write_bytes(original.executable.read_bytes())
    specifier = SpecifierSet(">=3.8,<3.10")

    assert len(Finder().find_all(specifier)) == 3
    assert [p.version for p in Finder(**{dedup: True}).find_all(specifier)] == [
        Version("3.9.0"),
        Version("3.8.0"),
    ]


def test_specifier_set_skips_invalid_interpreters(mocked_python, tmp_path):
    mocked_python.add_python(tmp_path / "python3.10")

    assert [p.version for p in Finder().find_all(SpecifierSet(">=3.8"))] == [
        Version("3.9.0"),
        Version("3.8.0"),
    ]


def test_specifier_set_with_actual_interpreters(python_shims):
    finder = Finder(selected_providers=["path"])
    found = finder.find(
        SpecifierSet(f"=={sys.version_info.major}.{sys.version_info.minor}.*")
    )

    assert found is not None
    assert found.version.release[:2] == sys.version_info[:2]
    assert finder.find(SpecifierSet("==0.*")) is None
