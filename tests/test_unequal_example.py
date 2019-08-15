import sys
import os
import pytest

sys.path.append(os.path.abspath('../factory'))
from unequal_example import *
from factory.factory import equals, operate_workstation_graph
sys.path.append(os.path.abspath('../tests'))


config = Config()


@pytest.fixture
def start():
    return StartProcess(config)


@pytest.fixture
def b():
    return BProcess(config)


@pytest.fixture
def c():
    return CProcess(config)


@pytest.fixture
def end():
    return EndProcess(config)


def test_pipeline_connection(start, b, c, end):
    start.connect(None, [b, c])
    b.connect([start], [c])
    c.connect([start, b], [end])
    end.connect([c], None)
    assert c.managers == [start, b]


def test_requirements(start, b, c, end):
    start.connect(None, [b, c])
    b.connect([start], [c])
    c.connect([start, b], [end])
    end.connect([c], None)

    assert equals(start.get_requirements(), {'a': ['1'], 'b': ['2']})
    assert equals(b.get_requirements(), {'a': ['2']})
    assert equals(c.get_requirements(), {'a': ['1', '2'], 'b': ['2']})
    assert equals(end.get_requirements(), {})


def test_engage_start_suppliers(start, b, c, end):
    start.connect(None, [b, c])
    b.connect([start], [c])
    c.connect([start, b], [end])
    end.connect([c], None)

    start._engage_suppliers()
    assert set(start.resources) == set()
    assert set(b.resources) == {'b:2'}
    assert set(c.resources) == {'a:1', 'b:2'}
    b._engage_suppliers()
    assert set(c.resources) == {'a:1', 'a:2', 'b:2'}


def test_bfs(start, b, c, end):
    start.connect(None, [b, c])
    b.connect([start], [c])
    c.connect([start, b], [end])
    end.connect([c], None)

    sequence = operate_workstation_graph(start)
    assert sequence == [start, b, c, end, end, c, b, start]


def test_engage_supply_chain(start, b, c, end):
    start.connect(None, [b, c])
    b.connect([start], [c])
    c.connect([start, b], [end])
    end.connect([c], None)

    operate_workstation_graph(start)
    assert set(b.resources) == {'b:2'}
    assert set(c.resources) == {'a:1', 'a:2', 'b:2'}
    assert set(end.resources) == set(list(
        {
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
    )
    )


