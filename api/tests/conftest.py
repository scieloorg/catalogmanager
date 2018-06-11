
from pathlib import Path

import pytest
from pyramid import testing


"""
        'database_uri': 'http://localhost:6789',
        'database_username': 'username',
        'database_password': 'password',
"""

@pytest.fixture
def dummy_request():
    request = testing.DummyRequest()
    request.db_settings = {
        'host': 'http://localhost',
        'port': '12345',
    }
    return request


@pytest.fixture
def test_xml_file():
    return """
    <article article-type="research-article"
             dtd-version="1.0"
             specific-use="sps-1.2"
             xml:lang="en"
             xmlns:mml="http://www.w3.org/1998/Math/MathML"
             xmlns:xlink="http://www.w3.org/1999/xlink">
        <graphic xlink:href="0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg"/>
        <graphic xlink:href="0034-8910-rsp-S01518-87872016050006741-gf01.jpg"/>
    </article>
    """


@pytest.fixture
def test_assets_filenames():
    return (
        '0034-8910-rsp-S01518-87872016050006741.xml',
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
    )


@pytest.fixture
def test_article_files(test_assets_filenames):
    fixture_dir = Path(str(Path(__file__).parent)) / 'test_files' / '741a'
    return tuple(
        fixture_dir.joinpath(filename).absolute()
        for filename in test_assets_filenames
    )
