# FindPython

_A utility to find python versions on your system._

[![Tests](https://github.com/frostming/findpython/actions/workflows/ci.yml/badge.svg)](https://github.com/frostming/findpython/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/findpython?logo=python&logoColor=%23cccccc&style=flat-square)](https://pypi.org/project/findpython)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/findpython?logo=python&logoColor=%23cccccc&style=flat-square)](https://pypi.org/project/findpython)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet?style=flat-square)](https://github.com/frostming/findpython)

## Description

This library is a rewrite of [pythonfinder] project by [@techalchemy][techalchemy].
It simplifies the whole code structure while preserving most of the original features.

[pythonfinder]: https://github.com/sarugaku/pythonfinder
[techalchemy]: https://github.com/techalchemy

## Installation

FindPython can be used in both Python and Rust projects.

To install FindPython in Python:

```bash
pip install findpython
```

To install FindPython in Rust:

```bash
cargo install findpyhton
```

Or use FindPython library in a Rust project:

```bash
cargo add findpython
```

<details>
<summary>Expand this section to see findpython's availability in the package ecosystem</summary>

<a href="https://repology.org/project/python:findpython/versions">
    <img src="https://repology.org/badge/vertical-allrepos/python:findpython.svg?header=python%3Afindpython" alt="Packaging status">
</a>
</details>

## Python Usage

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

## Rust Usage

```rust
use findpython::Finder;

fn main() {
    let finder = Finder::default();

    // Find by major and minor version
    let py = finder.find(3, 9).unwrap();
    println!("{:?}", py);
    // Find all matches
    let all_pythons = finder.find_all();
    println!("{:?}", all_pythons);
}
```

## CLI Usage

In addition, FindPython provides a CLI interface to find python versions:

```
Find python executables on your system

Usage: findpython [OPTIONS] [VERSION_SPEC]

Arguments:
  [VERSION_SPEC]  The version spec to find, e.g. 3|3.8|python3

Options:
  -a, --all                    Return all matching Python versions
      --resolve-symlinks       Resolve symlinks and remove duplicate results
      --no-same-file           Remove duplicate results that are the same binary
      --no-same-python         Remove duplicate results that wrap the same Python interpreter
      --providers <PROVIDERS>  Select provider names(comma-separated) to use
  -o, --output <OUTPUT>        The output format [default: default] [possible values: default, json, path]
  -h, --help                   Print help
  -V, --version                Print version
```

## Integration

FindPython finds Python from the following places:

-   `PATH` environment variable
-   pyenv
-   asdf
-   winreg (Windows) (🚧 WIP 🚧)
-   [Rye] project manager backed by [python-build-standalone]

[rye]: https://rye-up.com
[python-build-standalone]: https://github.com/indygreg/python-build-standalone

## License

FindPython is released under MIT License.
