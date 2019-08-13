import sys
import os
import pytest

sys.path.append(os.path.abspath('../factory'))
from unequal_example import *
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

    assert equals(start.requirements(), {'a': ['1'], 'b': ['2']})
    assert equals(b.requirements(), {'a': ['2']})
    assert equals(c.requirements(), {'a': ['1', '2'], 'b': ['2']})
    assert equals(end.requirements(), {})


def test_engage_start_suppliers(start, b, c, end):
    start.connect(None, [b, c])
    b.connect([start], [c])
    c.connect([start, b], [end])
    end.connect([c], None)
    start._engage_suppliers()
    assert set(start._resources) == set()
    assert set(b._resources) == {'b:2'}
    assert set(c._resources) == {'a:1', 'b:2'}
    b._engage_suppliers()
    assert set(c._resources) == {'a:1', 'a:2', 'b:2'}


def test_engage_supply_chain(start, b, c, end):
    start.connect(None, [b, c])
    b.connect([start], [c])
    c.connect([start, b], [end])
    end.connect([c], None)

    start.engage_supply_chain()
    assert set(b._resources) == {'b:2'}
    assert set(c._resources) == {'a:1', 'a:2', 'b:2'}
    assert set(end._resources) == set()


