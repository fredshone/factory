import sys
import os
import pytest

sys.path.append(os.path.abspath('../factory'))
from simple_example import *
from factory.factory import combine_reqs, operate_workstation_graph, equals
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
def d():
    return DProcess(config)


@pytest.fixture
def end():
    return EndProcess(config)


def test_tool_requirements():
    tool = Tool1(option='1')
    assert equals(tool.get_requirements(), {'a': ['1'], 'b': ['1'], 'e': ['1']})


req1 = {
    'a': ['1', '2'],
    'b': ['1'],
}
req2 = {
        'b': ['2'],
    }
req3 = {
    'b': ['3'],
    'c': ['1', '2'],
}


test_combine_data = [
    ([req1], req1),
    ([], {}),
    ([req1, req2], {'a': ['1', '2'], 'b': ['1', '2']}),
    ([req2, req3], {'b': ['2', '3'], 'c': ['1', '2']}),
    ([req1, req2, req3], {'a': ['1', '2'], 'b': ['1', '2', '3'], 'c': ['1', '2']}),
]


@pytest.mark.parametrize("reqs,req", test_combine_data)
def test_combine_req(reqs, req):
    assert equals(combine_reqs(reqs), req)


def test_pipeline_connection(start, b, c, d, end):
    start.connect(None, [b, c])
    b.connect([start], [d])
    c.connect([start], [d])
    d.connect([b, c], [end])
    end.connect([d], None)
    assert d.managers == [b, c]


def test_requirements(start, b, c, d, end):
    start.connect(None, [b, c])
    b.connect([start], [d])
    c.connect([start], [d])
    d.connect([b, c], [end])
    end.connect([d], None)

    assert equals(start.get_requirements(), {'a': ['1'], 'b': ['1', '2']})
    assert equals(b.get_requirements(), {'a': ['1'], 'b': ['1'], 'e': ['1']})
    assert equals(c.get_requirements(), {'a': ['1', '2'], 'c': ['1', '2']})
    assert equals(d.get_requirements(), {'a': ['1', '2'], 'b': ['1', '2'], 'c': ['1'],
                                     'e': ['1', '2'], 'f': ['1', '2']})


def test_engage_start_suppliers(start, b, c, d, end):
    start.connect(None, [b, c])
    b.connect([start], [d])
    c.connect([start], [d])
    d.connect([b, c], [end])
    end.connect([d], None)
    start._engage_suppliers()
    assert set(start.resources) == set()
    assert set(b.resources) == {'a:1'}
    assert set(c.resources) == {'b:1', 'b:2'}


def test_bfs(start, b, c, d, end):
    start.connect(None, [b, c])
    b.connect([start], [d])
    c.connect([start], [d])
    d.connect([b, c], [end])
    end.connect([d], None)

    sequence = operate_workstation_graph(start)
    assert sequence == [start, b, c, d, end, end, d, c, b, start]


def test_engage_supply_chain(start, b, c, d, end):
    start.connect(None, [b, c])
    b.connect([start], [d])
    c.connect([start], [d])
    d.connect([b, c], [end])
    end.connect([d], None)

    operate_workstation_graph(start)
    assert set(b.resources) == {'a:1'}
    assert set(c.resources) == {'b:1', 'b:2'}
    assert set(d.resources) == {'a:2', 'c:2', 'c:1', 'a:1', 'b:1', 'e:1'}
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



