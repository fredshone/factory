class WorkStation:
    """
    Base Class for holding dictionary of Tool objects.
    """
    _tools = {}

    def __init__(self, config):
        self._resources = {}
        self.config = config
        self.managers = None
        self.suppliers = None

    def connect(self, managers: list, suppliers: list) -> None:
        self.managers = managers
        self.suppliers = suppliers

    @property
    def tools(self):
        return list(self._tools)

    def validate_supply_chain(self):
        if self.suppliers:
            self._validate_suppliers()
            for supplier in self.suppliers:
                supplier.validate_supply_chain()

    def build_supply_chain(self, validate=True):
        if self.suppliers and not self._resources:
            if validate:
                self._validate_suppliers()
            for supplier in self.suppliers:
                supplier.build_supply_chain()
        self._build()

    def _validate_suppliers(self):
        print(f'\nValidating: {self} for requirements: {self._build_requirements()}')
        requirements = self._build_requirements()
        tools = set()
        for supplier in self.suppliers:
            tools.update(supplier.tools)
        missing = set(requirements) - tools
        if missing:
            raise ValueError(
                f'missing requirements: {missing} required for {type(self)} by {self.suppliers}.'
            )

    def _gather_manager_requirements(self):
        if self.managers:
            type_set = set()
            for manager in self.managers:
                type_set.add(type(manager._build_requirements()))

            if len(type_set) > 1:
                raise TypeError('managers cannot have different types of requirements')
            if type_set == {list}:
                requirements = set()
            elif type_set == {dict}:
                requirements = {}
            else:
                raise TypeError(f'managers cannot have requirements of type {type_set}')

            for manager in self.managers:
                requirements.update(manager._build_requirements())
            return requirements

    def _gather_resources(self):
        resources = {}
        for supplier in self.suppliers:
            resources.update(supplier._resources)
        return list(resources)

    def _build(self):
        # build in order of dict, ie prioritise
        print(f'\nBuilding: {self} with resources: {self._gather_resources()}')
        all_req = self._gather_manager_requirements()
        if isinstance(all_req, set):
            self._build_from_set(all_req)
        elif isinstance(all_req, dict):
            self._build_from_dict(all_req)

    def _build_from_set(self, all_req):
        for tool_name, tool in self._tools.items():
            if tool_name in all_req:
                self._resources[tool_name] = self._tools[tool_name](self._gather_resources())

    def _build_from_dict(self, all_req):
        for tool_name, tool in self._tools.items():
            if tool_name in list(all_req):
                for selection in all_req[tool_name]:
                    name = tool_name + ':' + selection
                    self._resources[name] = self._tools[tool_name](self._gather_resources())

    def _build_requirements(self):
        if self.managers:
            req = set()
            for manager in self.managers:
                for requirement in manager._build_requirements():
                    resource = self._tools.get(requirement)
                    if resource:
                        req.update(resource.req)
            return list(req)


# Define tools to be used by Sub Processes
class Tool:
    req = None

    def __init__(self, option=None):
        self.option = option

    def requirements(self):
        return {req: self.option for req in self.req}

    def build(self, resource):
        for req in self.req:
            if req not in set(list(resource)):
                print(resource)
                print(req)
                raise ValueError('Missing input')
        print(f'Built {self} with {resource}')


def combine_req(reqs: list) -> dict:
    if not reqs:
        return None
    tool_set = set()
    for req in reqs:
        tool_set.update(list(req))
    tools = {}
    for tool in tool_set:
        options = set()
        for req in reqs:
            if req.get(tool):
                options.update(req[tool])
        tools[tool] = list(options)
    return tools