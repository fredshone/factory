import sys
import os
import pytest

sys.path.append(os.path.abspath('../factory'))
from example import *
from factory.factory import combine_reqs
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


req1 = {
    'a': [1, 2],
    'b': [1],
}
req2 = {
        'b': [2],
    }
req3 = {
    'b': [3],
    'c': [1, 2],
}


test_combine_data = [
    ([req1], req1),
    ([], None),
    ([req1, req2], {'a': [1, 2], 'b': [1, 2]}),
    ([req2, req3], {'b': [2, 3], 'c': [1, 2]}),
    ([req1, req2, req3], {'a': [1, 2], 'b': [1, 2, 3], 'c': [1, 2]}),
]


@pytest.mark.parametrize("reqs,req", test_combine_data)
def test_combine_req(reqs, req):
    assert combine_reqs(reqs) == req


def test_pipeline_connection(start, b, c, d, end):
    start.connect(None, [b, c])
    b.connect([start], [d])
    c.connect([start], [d])
    d.connect([b, c], [end])
    end.connect([d], None)
    assert d.managers == [b, c]


def test_validate(start, b, c, d, end):
    start.connect(None, [b, c])
    b.connect([start], [d])
    c.connect([start], [d])
    d.connect([b, c], [end])
    end.connect([d], None)

    assert start.requirements() == start.config.requirements()
    assert b.requirements() == {'a': [1], 'b': [1], 'e': [1]}
    assert start._validate_suppliers()

