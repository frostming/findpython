# FindPython

_A utility to find python versions on your system._

[![Tests](https://github.com/frostming/findpython/actions/workflows/ci.yml/badge.svg)](https://github.com/frostming/findpython/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pdm?logo=python&logoColor=%23cccccc?style=flat-square)](https://pypi.org/project/findpython)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/findpython?style=flat-square)](https://pypi.org/project/findpython)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet?style=flat-square)](https://github.com/frostming/findpython)

## Description

This library is a rewrite of [pythonfinder] project by [@techalchemy][techalchemy].
It simplifies the whole code structure while preserving most of the original features.

[pythonfinder]: https://github.com/sarugaku/pythonfinder
[techalchemy]: https://github.com/techalchemy

## Installation

FindPython is installable via any kind of package manager including `pip`:

```bash
pip install findpython
```

## Usage

```python
>>> import findpython
>>> findpython.find(3, 9)  # Find by major and minor version
<PythonVersion executable=PosixPath('/opt/homebrew/bin/python3.9'), version=<Version('3.9.10')>, architecture='64bit', major=3, minor=9, patch=10>
>>> findpython.find("3.9")  # Find by version string
<PythonVersion executable=PosixPath('/opt/homebrew/bin/python3.9'), version=<Version('3.9.10')>, architecture='64bit', major=3, minor=9, patch=10>
>>> findpython.find("3.9-32")  # Find by version string and architecture
<PythonVersion executable=WindowsPath('C:\\Python\\3.9-32\\python.exe'), version=<Version('3.9.10')>, architecture='32bit', major=3, minor=9, patch=10>
>>> findpython.find(name="python3")  # Find by executable name
<PythonVersion executable=PosixPath('/Users/fming/Library/PythonUp/bin/python3'), version=<Version('3.10.2')>, architecture='64bit', major=3, minor=10, patch=2>
>>> findpython.find("python3")  # Find by executable name without keyword argument, same as above
<PythonVersion executable=PosixPath('/Users/fming/Library/PythonUp/bin/python3'), version=<Version('3.10.2')>, architecture='64bit', major=3, minor=10, patch=2>
>>> findpython.find_all(major=3, minor=9)  # Same arguments as `find()`, but return all matches
[<PythonVersion executable=PosixPath('/opt/homebrew/bin/python3.9'), version=<Version('3.9.10')>, architecture='64bit', major=3, minor=9, patch=10>, <PythonVersion executable=PosixPath('/opt/homebrew/bin/python3'), version=<Version('3.9.10')>, architecture='64bit', major=3, minor=9, patch=10>, <PythonVersion executable=PosixPath('/Users/fming/Library/PythonUp/cmd/python3.9'), version=<Version('3.9.9')>, architecture='64bit', major=3, minor=9, patch=9>, <PythonVersion executable=PosixPath('/usr/local/bin/python3.9'), version=<Version('3.9.5')>, architecture='64bit', major=3, minor=9, patch=5>, <PythonVersion executable=PosixPath('/usr/local/bin/python3'), version=<Version('3.9.5')>, architecture='64bit', major=3, minor=9, patch=5>]
```

## CLI Usage

In addition, FindPython provides a CLI interface to find python versions:

```
usage: findpython [-h] [-V] [-a] [--resolve-symlink] [-v] [--no-same-file] [--no-same-python] [version_spec]

Find python files in a directory

positional arguments:
  version_spec       Python version spec or name

options:
  -h, --help         show this help message and exit
  -V, --version      show program's version number and exit
  -a, --all          Show all matching python versions
  --resolve-symlink  Resolve all symlinks
  -v, --verbose      Verbose output
  --no-same-file     Eliminate the duplicated results with the same file contents
  --no-same-python   Eliminate the duplicated results with the same sys.executable
```

## Integration

FindPython finds Python from the following places:

-   `PATH` environment variable
-   pyenv
-   asdf
-   `/Library/Frameworks/Python.framework/Versions` (MacOS)
-   winreg (Windows)

## License

FindPython is released under MIT License.
