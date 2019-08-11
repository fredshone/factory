from factory.factory import WorkStation
from factory.factory import Tool


class Tool1(Tool):
    req = ['a', 'b', 'e']


class Tool2(Tool):
    req = ['b']


class Tool3(Tool):
    req = ['a', 'c']


class Tool4(Tool):
    req = ['c']


class Tool5(Tool):
    req = ['f']


# define SubProcesses
class StartProcess(WorkStation):

    def _build(self):
        # build in order of dict, ie prioritise
        print(f'--> Building: {self}')
        for tool_name, tool in self._tools.items():
            if tool_name in self._build_requirements():
                self._resources[tool_name] = self._tools[tool_name](self._gather_resources)

    def _build_requirements(self):
        req = {'a': ['1'], 'b': ['1', '2']}
        return req


class BProcess(WorkStation):
    _tools = {
        'a': Tool1,
    }


class CProcess(WorkStation):
    _tools = {
        'b': Tool3,
    }


class DProcess(WorkStation):
    _tools = {
        'a': Tool1,
        'b': Tool3,
        'e': Tool2,
        'c': Tool5,
    }


class FinalProcess(WorkStation):
    _tools = {
        'a': 'A',
        'b': 'B',
        'c': 'C',
        'd': 'D',
        'e': 'E',
        'f': 'F',
    }

    def _build(self):
        print('building final')
        self._resources = self._tools