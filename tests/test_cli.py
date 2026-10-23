import os

from findpython.__main__ import cli


def test_cli_find_pythons(mocked_python, capsys):
    retcode = cli(["--all"])
    assert retcode == 0
    out, _ = capsys.readouterr()
    lines = out.strip().splitlines()
    for version, line in zip(("3.9", "3.8", "3.7"), lines, strict=False):
        assert line.lstrip().startswith(f"cpython@{version}.0")


def test_cli_find_python_by_version(mocked_python, capsys, tmp_path):
    retcode = cli(["3.8"])
    assert retcode == 0
    out, _ = capsys.readouterr()
    line = out.strip()
    assert line.startswith("cpython@3.8.0")
    assert line.endswith(str(tmp_path / "python3.8"))


def test_cli_deduplicate_interpreters_skips_broken(python_shims, switch, capsys):
    executables, independent_python = python_shims
    args = ["--all", "--path", "--providers", "path"]
    if switch:
        args.append("--no-same-python")
    assert cli(args) == 0
    out, _ = capsys.readouterr()
    found = set(out.splitlines())
    assert len(found) == (2 if switch else 4)
    assert found <= {str(executable) for executable in executables}
    assert str(independent_python) in found


def test_cli_deduplicate_same_interpreter(mocked_python, tmp_path, switch, capsys):
    suffix = ".bat" if os.name == "nt" else ".sh"
    mocked_python.add_python(
        tmp_path / f"python{suffix}", "3.9.0", interpreter=tmp_path / "python3.9"
    )
    args = ["--all", "--providers", "path"]
    if switch:
        args.append("--no-same-python")
    assert cli(args) == 0
    out, _ = capsys.readouterr()
    assert len(out.splitlines()) == (3 if switch else 4)


def test_cli_find_python_freethreaded(mocked_python, capsys, tmp_path):
    mocked_python.add_python(tmp_path / "python3.13", "3.13.0")
    mocked_python.add_python(tmp_path / "python3.13t", "3.13.0", freethreaded=True)

    retcode = cli(["--all", "3.13"])
    assert retcode == 0
    out, _ = capsys.readouterr()
    line = out.strip()
    assert "\n" not in line
    assert line.lstrip().split(":")[0] == "cpython@3.13.0"

    retcode = cli(["--all", "3.13t"])
    assert retcode == 0
    out, _ = capsys.readouterr()
    line = out.strip()
    assert "\n" not in line
    assert line.lstrip().split(":")[0] == "cpython@3.13.0t"
