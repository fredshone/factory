from factory.factory import WorkStation
from factory.factory import Tool
from factory.factory import convert_to_unique_keys


class Config:
    def __init__(self):
        pass

    def requirements(self):
        return {'a': ['1'], 'b': ['1', '2']}


class ExampleTool(Tool):
    valid_options = ['1', '2', '3']

    def requirements(self):
        if self.option:
            return {req: [self.option] for req in self.req}
        return {req: None for req in self.req}

    def build(self, resource):
        for requirement in convert_to_unique_keys(self.requirements()):
            if requirement not in list(resource):
                raise ValueError(f'Missing requirement: {requirement}')
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

    _tools = None

    # def build(self):
    #     # build in order of dict, ie prioritise
    #     print(f'--> Building: {self}')
    #     for tool_name, tool in self._tools.items():
    #         if tool_name in self.requirements():
    #             self._resources[tool_name] = self._tools[tool_name](self._gather_resources)


class BProcess(WorkStation):
    _tools = {
        'a': Tool1,
        'f': Tool4,
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
    _tools = {
        'a': None,
        'b': None,
        'c': None,
        'd': None,
        'e': None,
        'f': None,
    }

    def build(self):
        print('Building final')
        self._resources = {
            'a:1': 'A1',
            'a:2': 'A2',
            'b:1': 'B1',
            'b:2': 'B2',
            'c:1': 'C',
            'e:1': 'E1',
            'e:2': 'E2',
            'f:1': 'F1',
            'f:2': 'F2',
        }
