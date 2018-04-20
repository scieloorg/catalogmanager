import os

from catalogmanager.models.article_model import (
    Article,
)
from catalogmanager.models.file import File
from catalogmanager.xml.xml_tree import (
    XMLTree,
)


def test_article(test_package_A):
    xml_file_path, files = test_package_A[0], test_package_A[1:]
    xml_filename = os.path.basename(xml_file_path)
    article = Article('ID')
    xml_file = File(xml_filename)
    xml_file.content = open(xml_file_path, 'rb').read()
    xml_file.size = os.stat(xml_file_path).st_size
    article.xml_file = xml_file
    assets_files = []
    for file_path in files:
        with open(file_path, 'rb') as asset_file:
            content = asset_file.read()
            assets_files.append(
                {
                    'filename': os.path.basename(file_path),
                    'content': content,
                    'content_size': len(content)
                }
            )
    article.update_asset_files(assets_files)
    assets = [
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg'
    ]
    expected = {
        'assets': assets,
        'xml': '0034-8910-rsp-S01518-87872016050006741.xml',
    }
    assert article.xml_file.name == xml_filename
    assert article.xml_tree.xml_error is None
    assert article.get_record_content() == expected
    assert article.xml_file.content == xml_file.content
    xml_from_file = XMLTree()
    xml_from_file.content = article.xml_file.content
    xml_from_tree = XMLTree()
    xml_from_tree.content = article.xml_tree.content
    assert xml_from_file.content == xml_from_tree.content


def test_missing_files_list(test_package_B):
    xml_file_path, files = test_package_B[0], test_package_B[1:]
    article = Article('ID')
    xml_file = File(xml_file_path)
    xml_file.content = open(xml_file_path, 'rb').read()
    xml_file.size = os.stat(xml_file_path).st_size
    article.xml_file = xml_file
    assets_files = []
    for file_path in files:
        with open(file_path, 'rb') as asset_file:
            content = asset_file.read()
            assets_files.append(
                {
                    'filename': file_path,
                    'content': content,
                    'content_size': len(content)
                }
            )
    article.update_asset_files(assets_files)

    assert len(article.assets) == 3
    assert sorted(article.assets.keys()) == sorted(
        [
            '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
            '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
            '0034-8910-rsp-S01518-87872016050006741-gf31.jpg',
        ]
    )
    assert article.unexpected_files_list == []
    assert article.missing_files_list == [
        '0034-8910-rsp-S01518-87872016050006741-gf31.jpg',
    ]


def test_unexpected_files_list(test_package_C):
    xml_file_path, files = test_package_C[0], test_package_C[1:]

    article = Article('ID')
    xml_file = File(xml_file_path)
    xml_file.content = open(xml_file_path, 'rb').read()
    xml_file.size = os.stat(xml_file_path).st_size
    article.xml_file = xml_file
    assets_files = []
    for file_path in files:
        with open(file_path, 'rb') as asset_file:
            content = asset_file.read()
            assets_files.append(
                {
                    'filename': file_path,
                    'content': content,
                    'content_size': len(content)
                }
            )
    article.update_asset_files(assets_files)

    assert len(article.assets) == 2
    assert sorted(article.assets.keys()) == sorted(
        [
            '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
            '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
        ]
    )
    assert article.unexpected_files_list == [
       files[2]
    ]
    assert article.missing_files_list == []


def test_update_href(test_package_A):
    xml_file_path, files = test_package_A[0], test_package_A[1:]

    article = Article('ID')
    xml_file = File(xml_file_path)
    xml_file.content = open(xml_file_path, 'rb').read()
    xml_file.size = os.stat(xml_file_path).st_size
    article.xml_file = xml_file
    assets_files = []
    for file_path in files:
        with open(file_path, 'rb') as asset_file:
            content = asset_file.read()
            assets_files.append(
                {
                    'filename': file_path,
                    'content': content,
                    'content_size': len(content)
                }
            )
    article.update_asset_files(assets_files)
    content = article.xml_tree.content
    asset = article.assets.get(
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg')
    asset.href = 'novo href'
    items = [
        item
        for name, item in article.assets.items()
        if name == '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
    ]

    assert len(items) == 1
    assert items[0].href == 'novo href'
    assert items[0].name == '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'

    assert not article.xml_tree.compare(content)
    assert b'novo href' in article.xml_tree.content
