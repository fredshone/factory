from factory.factory import WorkStation
from factory.factory import Tool, convert_to_unique_keys


class Config:
    def __init__(self):
        pass

    def requirements(self):
        return {'a': ['1'], 'b': ['2']}


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
    req = ['a']


class Tool2(ExampleTool):
    req = ['a']


class Tool3(ExampleTool):
    req = ['b']


class Tool4(ExampleTool):
    req = ['c']


class Tool5(ExampleTool):
    req = ['f']


class StartProcess(WorkStation):

    _tools = None


class BProcess(WorkStation):
    _tools = {
        'b': Tool1,
    }


class CProcess(WorkStation):
    _tools = {
        'a': Tool2,
        'b': Tool3,
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
