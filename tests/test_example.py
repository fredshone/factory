import sys
import os
import pytest

sys.path.append(os.path.abspath('../factory'))
from example import *
from factory.factory import combine_reqs
sys.path.append(os.path.abspath('../tests'))


config = Config()


def equals(d1, d2):
    if not d1 and not d2:
        return True
    if not len(d1) == len(d2):
        return False
    if not sorted(list(d1)) == sorted(list(d2)):
        return False
    for d1k, d1v, in d1.items():
        if d1k not in list(d2):
            return False
        if not sorted(d1v) == sorted(d2[d1k]):
            return False
    return True


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
    assert equals(tool.requirements(), {'a': ['1'], 'b': ['1'], 'e': ['1']})


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
    ([], None),
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


def test_validate(start, b, c, d, end):
    start.connect(None, [b, c])
    b.connect([start], [d])
    c.connect([start], [d])
    d.connect([b, c], [end])
    end.connect([d], None)

    assert equals(start.requirements(), start.config.requirements())
    assert equals(b.requirements(), {'a': ['1'], 'b': ['1'], 'e': ['1']})
    assert start._validate_suppliers()

