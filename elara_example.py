from factory.factory import WorkStation
from factory.factory import Tool, convert_to_unique_keys


class Config:
    def __init__(self):
        pass

    def requirements(self):
        return {'volume_counts': ['car'], 'vkt': ['bus']}


class ExampleTool(Tool):
    pass


# Tools
class VKT(ExampleTool):
    req = ['volume_counts']
    valid_options = ['car', 'bus']


class VolumeCounts(ExampleTool):
    req = ['network', 'events']
    valid_options = ['car', 'bus']

    def requirements(self):
        return {req: None for req in self.req}


class ModeShare(ExampleTool):
    req = ['network', 'events']
    valid_options = ['all']

    def requirements(self):
        return {req: None for req in self.req}


class Network(ExampleTool):
    req = ['network_path']


class Events(ExampleTool):
    req = ['events_path']


class Plans(ExampleTool):
    req = ['plans_path']


class GetPath(ExampleTool):
    req = None


# Work stations
class StartProcess(WorkStation):
    _tools = None


class PostProcess(WorkStation):
    _tools = {
        'vkt': VKT,
    }


class HandlerProcess(WorkStation):
    _tools = {
        'volume_counts': VolumeCounts,
        'mode_share': ModeShare,
    }


class InputProcess(WorkStation):
    _tools = {
        'events': Events,
        'plans': Plans,
        'network': Network
    }


class PathProcess(WorkStation):
    _tools = {
        'network_path': GetPath,
        'events_path': GetPath,
        'plans_path': GetPath,
    }
