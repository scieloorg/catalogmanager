
import pytest
from webtest import TestApp

from catalogmanager_api import main


@pytest.fixture
def testapp():
    settings = {'ini_filename': 'development.ini'}
    test_app = main(settings)
    return TestApp(test_app)


@pytest.fixture
def test_xml_file():
    return """
    <article>
        </text>
    </article>
    """
