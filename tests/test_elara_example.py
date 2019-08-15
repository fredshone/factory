import sys
import os
import pytest

sys.path.append(os.path.abspath('../factory'))
from elara_example import *
from factory.factory import equals, operate_workstation_graph, build_graph_depth
sys.path.append(os.path.abspath('../tests'))


config = Config()


@pytest.fixture
def start():
    return StartProcess(config)


@pytest.fixture
def post_process():
    return PostProcess(config)


@pytest.fixture
def handler_process():
    return HandlerProcess(config)


@pytest.fixture
def inputs_process():
    return InputProcess(config)


@pytest.fixture
def config_paths():
    return PathProcess(config)


def test_pipeline_connection(start, post_process, handler_process, inputs_process, config_paths):
    start.connect(None, [post_process, handler_process])
    post_process.connect([start], [handler_process])
    handler_process.connect([start, post_process], [inputs_process])
    inputs_process.connect([handler_process], [config_paths])
    config_paths.connect([inputs_process], None)
    assert handler_process.managers == [start, post_process]


def test_requirements(start, post_process, handler_process, inputs_process, config_paths):
    start.connect(None, [post_process, handler_process])
    post_process.connect([start], [handler_process])
    handler_process.connect([start, post_process], [inputs_process])
    inputs_process.connect([handler_process], [config_paths])
    config_paths.connect([inputs_process], None)

    assert equals(start.get_requirements(), {'volume_counts': ['car'], 'vkt': ['bus']})
    assert equals(post_process.get_requirements(), {'volume_counts': ['bus']})
    assert equals(handler_process.get_requirements(), {'events': None, 'network': None})
    assert equals(inputs_process.get_requirements(), {'events_path': None, 'network_path': None})
    assert equals(config_paths.get_requirements(), {})


def test_engage_start_suppliers(start, post_process, handler_process, inputs_process, config_paths):
    start.connect(None, [post_process, handler_process])
    post_process.connect([start], [handler_process])
    handler_process.connect([start, post_process], [inputs_process])
    inputs_process.connect([handler_process], [config_paths])
    config_paths.connect([inputs_process], None)

    start._engage_suppliers()
    assert set(start.resources) == set()
    assert set(post_process.resources) == {'vkt:bus'}
    assert set(handler_process.resources) == {'volume_counts:car'}
    post_process._engage_suppliers()
    assert set(handler_process.resources) == {'volume_counts:car', 'volume_counts:bus'}


def test_dfs_distances(start, post_process, handler_process, inputs_process, config_paths):
    start.connect(None, [handler_process, post_process])
    post_process.connect([start], [handler_process])
    handler_process.connect([start, post_process], [inputs_process])
    inputs_process.connect([handler_process], [config_paths])
    config_paths.connect([inputs_process], None)

    build_graph_depth(start)

    assert start.depth == 0
    assert post_process.depth == 1
    assert handler_process.depth == 2
    assert inputs_process.depth == 3
    assert config_paths.depth == 4


def test_bfs(start, post_process, handler_process, inputs_process, config_paths):
    start.connect(None, [handler_process, post_process])
    post_process.connect([start], [handler_process])
    handler_process.connect([start, post_process], [inputs_process])
    inputs_process.connect([handler_process], [config_paths])
    config_paths.connect([inputs_process], None)

    sequence = operate_workstation_graph(start)
    assert sequence == [start, post_process, handler_process, inputs_process, config_paths,
                        config_paths, inputs_process, handler_process, post_process, start]


def test_engage_supply_chain(start, post_process, handler_process, inputs_process, config_paths):
    start.connect(None, [handler_process, post_process])
    post_process.connect([start], [handler_process])
    handler_process.connect([start, post_process], [inputs_process])
    inputs_process.connect([handler_process], [config_paths])
    config_paths.connect([inputs_process], None)

    operate_workstation_graph(start)
    assert set(start.resources) == set()
    assert set(post_process.resources) == {'vkt:bus'}
    assert set(handler_process.resources) == {'volume_counts:car', 'volume_counts:bus'}
    assert set(inputs_process.resources) == {'events', 'network'}
    assert set(config_paths.resources) == {'events_path', 'network_path'}




