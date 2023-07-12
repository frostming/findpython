from __future__ import annotations

import abc

from .findpython import *


class BaseProvider(abc.ABC):
    @abc.abstractmethod
    def find_pythons(self):
        pass

    def find_pythons_from_path(self, path, as_interpreter=False):
        return find_pythons_from_path(path, as_interpreter)
