from collections import defaultdict


class WorkStation:
    """
    Base Class for holding dictionary of Tool objects.
    """
    depth = 0
    tools = {}

    def __init__(self, config):
        self.resources = {}
        self.requirements = {}
        self.config = config
        self.managers = None
        self.suppliers = None

    def connect(self, managers: list, suppliers: list) -> None:
        """
        Connect workstations to their respective managers and suppliers to form a DAG.
        Note that arguments should be provided as lists.
        :param managers: list of managers
        :param suppliers: list of suppliers
        :return: None
        """
        self.managers = managers
        self.suppliers = suppliers

    def get_requirements(self):
        """
        Set own requirments by search backwards through managers chain gathering required tool
        requirements.

        Note that this caches requirements dict in self._requirements.

        If no managers then uses config requirements() method.

        Note that all tools are initiated for all required options and stored in
        self._resources.

        :return: dict of requirements {req: [options]}
        """
        if self.requirements:
            return self.requirements

        if not self.managers:
            # print(f'retrieving reqs from config at {self}: {self.config.requirements()}')
            return self.config.get_requirements()

        reqs = []
        for manager in self.managers:
            for manager_requirement, options in manager.get_requirements().items():
                if manager_requirement not in list(self.tools):  # ie tool not available
                    continue
                if options is None:
                    option = None
                    key = manager_requirement
                    self._build_manager_requirement(key, manager_requirement, option, reqs)
                else:
                    for option in options:
                        key = manager_requirement + ':' + option
                        self._build_manager_requirement(key, manager_requirement, option, reqs)

        # cache reqs
        self.requirements = combine_reqs(reqs)
        return self.requirements

    def _build_manager_requirement(
            self,
            key: str,
            manager_requirement,
            option,
            reqs: list
    ) -> None:
        """
        Helper method to reduce repetition. Initiates required tools, adds them to workstation
        resources, and builds list of requirements.
        :param key: str, unique key for .resource map
        :param manager_requirement: str, tool key
        :param option: required tool option
        :param reqs: full list of current requirements
        :return: None
        """
        if key in list(self.resources):
            return None
        tool = self.tools.get(manager_requirement)
        if not tool:
            return None
        resource = tool(option)
        tool_reqs = resource.get_requirements()
        reqs.append(tool_reqs)
        self.resources[key] = resource

    def _engage_suppliers(self):
        """
        Engage suppliers, initiating their tools and getting their requirements. Raises
        ValueError if suppliers have missing tools.
        :return:
        """
        requirements = self.get_requirements()

        supplier_tools = {}
        for supplier in self.suppliers:
            if not supplier.tools:
                continue
            supplier_tools.update(supplier.tools)

        # check for missing requirements
        missing = set(requirements) - set(supplier_tools)
        if missing:
            raise ValueError(
                f'Missing requirements: {missing} from suppliers: {self.suppliers}.'
            )

        # activate suppliers and validate options and set their requirements
        for supplier in self.suppliers:
            supplier_requirement_list = []
            # initiate in order
            if not supplier.tools:
                continue
            for tool_name, tool in supplier.tools.items():
                if not tool:
                    continue
                if tool_name in list(requirements):
                    options = requirements[tool_name]
                    if not options:
                        resource = tool(None)
                        key = tool_name
                        supplier.resources[key] = resource
                        supplier_requirement_list.append(resource.get_requirements())

                    else:
                        for option in options:
                            resource = tool(option)
                            key = tool_name + ':' + option
                            supplier.resources[key] = resource
                            supplier_requirement_list.append(resource.get_requirements())
            # update supplier req dict
            supplier.requirements.update(combine_reqs(supplier_requirement_list))

    def build(self):
        """
        Gather resources from suppliers for current workstation and build() all resources in
        order of .resources map.
        :return: None
        """
        # gather resources
        supplier_resources = {}
        if self.suppliers:
            for supplier in self.suppliers:
                supplier_resources.update(supplier.resources)
        if self.resources:
            for tool_name, tool in self.resources.items():
                tool.build(supplier_resources)


# Define tools to be used by Sub Processes
class Tool:
    """
    Base tool class.
    """
    req = None
    valid_options = [None]

    def __init__(self, option=None):
        """
        Initiate a tool instance with optional option (ie: 'bus'). Raise UserWarning if option is
        not in .valid_options.
        :param option: optional option, typically assumed to be str
        """
        if option not in self.valid_options:
            raise UserWarning(f'Unsupported option: {option} at tool: {self}')
        self.option = option

    def get_requirements(self) -> dict:
        """
        Default return requirements of tool for given .option.
        Returns None if .option is None.
        :return: dict of requirements
        """
        if not self.req:
            return None
        if self.option:
            return {req: [self.option] for req in self.req}
        return {req: None for req in self.req}

    def build(self, resource: dict) -> None:
        """
        Default build self.
        :param resource:
        :return: None
        """
        for requirement in convert_to_unique_keys(self.get_requirements()):
            if requirement not in list(resource):
                raise ValueError(f'Missing requirement: {requirement}')
        print(f'\tBuilt {self}')


def operate_workstation_graph(start_node: WorkStation, verbose=False) -> list:
    """
    Main function for validating graph requirements, then initiating and building minimum resources.

    Stage1: Traverse graph from starting workstation to suppliers with depth-first search,
    marking workstations with possible longest path.

    Stage 2: Traverse graph with breadth-first search, prioritising shallowest nodes, sequentially
    initiating required workstation .tools as .resources and building .requirements.

    Stage 3: Traverse graph along same path but backward, gathering resources from suppliers at
    each workstation and building all own resources.

    Note that circular dependencies are not supported.

    Note that the function should be given the workstation with the initial/final requirements
    for the factory.

    :param start_node: starting workstation
    :param verbose: bool, verbose behaviour
    :return: list, sequence of visits for stages 2 (initiation and validation) and 3 (building)
    """

    # stage 1:
    build_graph_depth(start_node)

    # stage 2:
    visited = []
    queue = []
    start_node._engage_suppliers()
    queue.append(start_node)
    visited.append(start_node)

    while queue:
        current = queue.pop(0)
        if current.suppliers:
            if verbose:
                print('VALIDATING: ', current)
            current._engage_suppliers()

            for supplier in order_by_distance(current.suppliers):
                if supplier not in visited:
                    queue.append(supplier)
                    visited.append(supplier)
    # stage 3:
    sequence = visited
    return_queue = visited[::-1]
    visited = []
    while return_queue:
        current = return_queue.pop(0)
        if verbose:
            print('BUILDING: ', current)
        current.build()
        visited.append(current)
    # return full sequence for testing
    return sequence + visited


def build_graph_depth(current: WorkStation, visited=None, depth=0) -> list:
    """
    Function to recursive depth-first traverse graph of suppliers, recording workstation depth in
    graph.
    :param current: starting workstation
    :param visited: list, visited workstations
    :param depth: current depth
    :return: list, visited workstations in order
    """
    if not visited:
        visited = []
    visited.append(current)

    # Recur for all the nodes supplying this node
    if current.suppliers:
        depth = depth + 1
        for supplier in current.suppliers:
            if supplier.depth < depth:
                supplier.depth = depth
            build_graph_depth(supplier, visited, depth)

    return visited


def order_by_distance(candidates: list) -> list:
    """
    Returns candidate list ordered by .depth.
    :param candidates: list, of workstations
    :return: list, of workstations
    """
    return sorted(candidates, key=lambda x: x.depth, reverse=False)


def combine_reqs(reqs: list) -> dict:
    """
    Helper function for combining lists of requirements (dicts of lists) into a single
    requirements dict:

    [{req1:[a,b], req2:[b]}, {req1:[a], req2:[a], req3:None}] -> {req1:[a,b], req2:[a,b], req3:None}

    Note that no requirements are returned as an empty dict.

    Note that no options are returned as None ie {requirment: None}
    :param reqs: list of dicts of lists
    :return: dict, of requirements
    """
    if not reqs:
        return {}
    tool_set = set()
    for req in reqs:
        if req:
            tool_set.update(list(req))
    combined_reqs = {}
    for tool in tool_set:
        options = set()
        for req in reqs:
            if req.get(tool):
                options.update(req[tool])
        if options:
            combined_reqs[tool] = list(options)
        else:
            combined_reqs[tool] = None
    return combined_reqs


def convert_to_unique_keys(d: dict) -> list:
    """
    Helper function to convert a requirements dictionary into a list of unique keys:

    {req1:[a,b], req2:[a], req3:None} -> ['req1:a', 'req1:b', 'req2:a', 'req3'}

    Note that if option is None, key will be returned as requirement key only.

    :param d: dict, of requirements
    :return: list
    """
    keys = []
    if not d:
        return []
    for name, options in d.items():
        if not options:
            keys.append(name)
            continue
        for option in options:
            keys.append(f'{name}:{option}')
    return keys


def list_equals(l1, l2):
    """
    Helper function to check for equality between two lists of options.
    :param l1: list
    :param l2: list
    :return: bool
    """
    if l1 is None:
        if l2 is None:
            return True
        return False
    if not len(l1) == len(l2):
        return False
    if not sorted(l1) == sorted(l2):
        return False
    return True


def equals(d1, d2):
    """
    Helper function to check for equality between two dictionaries of requirements.
    :param d1: dict
    :param d2: dict
    :return: bool
    """
    if not list_equals(list(d1), list(d2)):
        return False
    for d1k, d1v, in d1.items():
        if not list_equals(d1v, d2[d1k]):
            return False
    return True

