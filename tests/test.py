import sys
import os
import pytest

sys.path.append(os.path.abspath('../factory'))
from factory import factory
sys.path.append(os.path.abspath('../tests'))


class Tool1(factory.Tool):
    req = ['a', 'b', 'e']


class Tool2(factory.Tool):
    req = ['b']


class Tool3(factory.Tool):
    req = ['a', 'c']


class Tool4(factory.Tool):
    req = ['c']


class Tool5(factory.Tool):
    req = ['f']


class AProcess(factory.WorkStation):

    def _build(self):
        # build in order of dict, ie prioritise
        print(f'--> Building: {self}')
        for tool_name, tool in self._tools.items():
            if tool_name in self._build_requirements():
                self._resources[tool_name] = self._tools[tool_name](self._gather_resources)

    def _build_requirements(self):
        req = {'a': ['1'], 'b': ['1', '2']}
        return req


class BProcess(factory.WorkStation):
    _tools = {
        'a': Tool1,
    }


class CProcess(factory.WorkStation):
    _tools = {
        'b': Tool3,
    }


class DProcess(factory.WorkStation):
    _tools = {
        'a': Tool1,
        'b': Tool3,
        'e': Tool2,
        'c': Tool5,
    }


class EProcess(factory.WorkStation):
    _tools = None

    def _build(self):
        print('Building final')

        self._resources = {
            'a': 'A',
            'b': 'B',
            'c': 'C',
            'd': 'D',
            'e': 'E',
            'f': 'F',
        }
