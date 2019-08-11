import sys
import os
import pytest

sys.path.append(os.path.abspath('../factory'))
from example import *
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

    assert start.requirements ==
    assert start._validate_suppliers()

