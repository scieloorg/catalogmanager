#!/usr/bin/env python
import pytest
from webtest import TestApp

from catalog_persistence import main


@pytest.fixture
def app():
    return main({})


@pytest.fixture
def testapp(app):
    return TestApp(app)


def test_functional_home(testapp):
    resp = testapp.get('/', status=200)
    assert resp.status == '200 OK'
    assert resp.status_code == 200
