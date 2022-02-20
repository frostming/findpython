"""
    FindPython
    ~~~~~~~~~~
    A utility to find python versions on your system
"""

__version__ = "0.1.0"

from findpython.finder import Finder
from findpython.python import PythonVersion


def find(*args, **kwargs) -> PythonVersion | None:
    """
    Return the Python version that is closest to the given version criteria.

    :param major: The major version or the version string or the name to match.
    :type major: int
    :param minor: The minor version to match.
    :type minor: int
    :param patch: The micro version to match.
    :type patch: int
    :param pre: Whether the python is a prerelease.
    :type pre: bool
    :param dev: Whether the python is a devrelease.
    :type dev: bool
    :param name: The name of the python.
    :type name: str
    :param architecture: The architecture of the python.
    :type architecture: str
    :return: a Python object or None
    :rtype: PythonVersion|None
    """
    return Finder().find(*args, **kwargs)


def find_all(*args, **kwargs) -> list[PythonVersion]:
    """
    Return all Python versions matching the given version criteria.

    :param major: The major version or the version string or the name to match.
    :type major: int
    :param minor: The minor version to match.
    :type minor: int
    :param patch: The micro version to match.
    :type patch: int
    :param pre: Whether the python is a prerelease.
    :type pre: bool
    :param dev: Whether the python is a devrelease.
    :type dev: bool
    :param name: The name of the python.
    :type name: str
    :param architecture: The architecture of the python.
    :type architecture: str
    :return: a list of PythonVersion objects
    :rtype: list
    """
    return Finder().find_all(*args, **kwargs)


__all__ = ["Finder", "find", "find_all", "PythonVersion"]
