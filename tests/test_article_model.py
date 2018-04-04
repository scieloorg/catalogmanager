import os

from catalogmanager.models.article_model import (
    Article,
)


def get_article(file_path):
    path = os.path.dirname(file_path)
    files = [path+'/'+item for item in os.listdir(path) if not item.endswith('.xml')]
    xml_file_path = file_path
    return Article(xml_file_path, files)


def test_article():
    xml_file_path = './packages/0034-8910-rsp-S01518-87872016050006741/0034-8910-rsp-S01518-87872016050006741.xml'
    article = get_article(xml_file_path)
    article.id = 'ID'

    assets = []
    assets.append(
        {'file_href': '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
        'file_id': '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'}
    )
    assets.append(
        {'file_href': '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
        'file_id': '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg'}
    )
    expected = {
            'assets': assets,
            'xml': '0034-8910-rsp-S01518-87872016050006741.xml',
        }
    assert article.xml_tree.file_name == os.path.basename(xml_file_path)
    assert article.xml_tree.file_fullpath == xml_file_path
    assert article.xml_tree.xml_error == None
    assert type(article.xml_tree.content) == type('')
    assert article.get_record_content() == expected


def test_unexpected_files_list():
    xml_file_path = './packages/741b/0034-8910-rsp-S01518-87872016050006741.xml'
    article = get_article(xml_file_path)

    assert len(article.assets) == 3
    assert sorted(article.assets.keys()) == sorted(
        ['0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf31.jpg',
        ])
    assert article.unexpected_files_list == []
    assert article.missing_files_list == ['0034-8910-rsp-S01518-87872016050006741-gf31.jpg']


def test_missing_files_list():
    xml_file_path = './packages/741c/0034-8910-rsp-S01518-87872016050006741.xml'
    article = get_article(xml_file_path)

    assert len(article.assets) == 2
    assert sorted(article.assets.keys()) == sorted(
        ['0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
        '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'])
    assert article.unexpected_files_list == ['fig.jpg']
    assert article.missing_files_list == []


def test_update_href():
    xml_file_path = './packages/0034-8910-rsp-S01518-87872016050006741/0034-8910-rsp-S01518-87872016050006741.xml'
    article = get_article(xml_file_path)
    content = article.xml_tree.content
    asset = article.assets.get('0034-8910-rsp-S01518-87872016050006741-gf01.jpg')
    asset.href = 'novo href'
    items = [item for name, item in article.assets.items() if name == '0034-8910-rsp-S01518-87872016050006741-gf01.jpg']
    print(article.assets)
    print(items)

    assert len(items) == 1
    assert items[0].href == 'novo href'
    assert items[0].name == '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'

    assert not article.xml_tree.content == content
