from findpython.utils import WINDOWS, looks_like_python
import pytest


matrix = [
    ("python", True),
    ("python3", True),
    ("python38", True),
    ("python3.8", True),
    ("python3.10", True),
    ("python310", True),
    ("python3.6m", True),
    ("python3.6.8m", False),
    ("anaconda3.3", True),
    ("python-3.8.10", False),
    ("unknown-2.0.0", False),
    ("python3.8.unknown", False),
    ("python38.bat", WINDOWS),
    ("python38.exe", WINDOWS),
    ("python38.sh", not WINDOWS),
    ("python38.csh", not WINDOWS),
]


@pytest.mark.parametrize("name, expected", matrix)
def test_looks_like_python(name, expected):
    assert looks_like_python(name) == expected
