from factory.factory import WorkStation
from factory.factory import Tool


class Config:
    def __init__(self):
        pass

    def requirements(self):
        return {'a': ['1'], 'b': ['1', '2']}


class ExampleTool(Tool):

    def requirements(self):
        return {req: self.option for req in self.req}

    def build(self, resource):
        for req in self.req:
            if req not in set(list(resource)):
                print(resource)
                print(req)
                raise ValueError('Missing input')
        print(f'Built {self} with {resource}')


class Tool1(ExampleTool):
    req = ['a', 'b', 'e']


class Tool2(ExampleTool):
    req = ['b']


class Tool3(ExampleTool):
    req = ['a', 'c']


class Tool4(ExampleTool):
    req = ['c']


class Tool5(ExampleTool):
    req = ['f']


class StartProcess(WorkStation):

    def _build(self):
        # build in order of dict, ie prioritise
        print(f'--> Building: {self}')
        for tool_name, tool in self._tools.items():
            if tool_name in self.requirements():
                self._resources[tool_name] = self._tools[tool_name](self._gather_resources)


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


class EndProcess(WorkStation):
    _tools = None

    def _build(self):
        print('Building final')

        return {
            'a': 'A',
            'b': 'B',
            'c': 'C',
            'd': 'D',
            'e': 'E',
            'f': 'F',
        }