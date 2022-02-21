from findpython.__main__ import cli


def test_cli_find_pythons(mocked_python, capsys):
    retcode = cli(["--all"])
    assert retcode == 0
    out, _ = capsys.readouterr()
    lines = out.strip().splitlines()
    for version, line in zip(("3.9", "3.8", "3.7"), lines):
        assert line.startswith(f"python{version} {version}.0")


def test_cli_find_python_by_version(mocked_python, capsys, tmp_path):
    retcode = cli(["3.8"])
    assert retcode == 0
    out, _ = capsys.readouterr()
    line = out.strip()
    assert line.startswith("python3.8 3.8.0")
    assert line.endswith(str(tmp_path / "python3.8"))
