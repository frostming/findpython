from findpython.__main__ import cli


def test_cli_find_pythons(mocked_python, capsys):
    retcode = cli(["--all"])
    assert retcode == 0
    out, _ = capsys.readouterr()
    lines = out.strip().splitlines()
    for version, line in zip(("3.9", "3.8", "3.7"), lines):
        assert line.lstrip().startswith(f"cpython@{version}.0")


def test_cli_find_python_by_version(mocked_python, capsys, tmp_path):
    retcode = cli(["3.8"])
    assert retcode == 0
    out, _ = capsys.readouterr()
    line = out.strip()
    assert line.startswith("cpython@3.8.0")
    assert line.endswith(str(tmp_path / "python3.8"))


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
