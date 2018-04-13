
import pytest
from pyramid.paster import get_appsettings
from webtest import TestApp

from catalogmanager_api import main


@pytest.fixture
def db_settings():
    ini_settings = get_appsettings('development.ini')
    return {
        'db_host': ini_settings['catalogmanager.db.host'],
        'db_port': ini_settings['catalogmanager.db.port'],
        'username': ini_settings['catalogmanager.db.username'],
        'password': ini_settings['catalogmanager.db.password'],
    }


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
