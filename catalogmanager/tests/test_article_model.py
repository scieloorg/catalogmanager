
from catalogmanager.models.article_model import (
    ArticleDocument,
)
from catalogmanager.xml.xml_tree import (
    XMLTree,
)


def test_article(test_package_A, test_packA_filenames,
                 test_packA_assets_files):
    article = ArticleDocument('ID')
    xml_file = test_package_A[0]
    article.xml_file = xml_file
    article.update_asset_files(test_packA_assets_files)
    expected = {
        'assets': [asset for asset in test_packA_filenames[1:]],
        'xml': test_packA_filenames[0],
    }
    assert article.xml_file.name == test_packA_filenames[0]
    assert article.xml_tree.xml_error is None
    assert article.get_record_content() == expected
    assert article.xml_file.content == xml_file.content
    xml_from_file = XMLTree()
    xml_from_file.content = article.xml_file.content
    xml_from_tree = XMLTree()
    xml_from_tree.content = article.xml_tree.content
    assert xml_from_file.content == xml_from_tree.content


def test_missing_files_list(test_package_B):
    article = ArticleDocument('ID')
    article.xml_file = test_package_B[0]
    assets_files = [
        {
            'filename': asset_file.name,
            'content': asset_file.content,
            'content_size': asset_file.size
        }
        for asset_file in test_package_B[1:]
    ]
    article.update_asset_files(assets_files)

    assert len(article.assets) == 3
    assert sorted(article.assets.keys()) == sorted(
        [
            '0034-8910-rsp-S01518-87872016050006741-gf01.jpg',
            '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
            '0034-8910-rsp-S01518-87872016050006741-gf31.jpg',
        ]
    )
    assert article.unexpected_files_list == []
    assert article.missing_files_list == [
        '0034-8910-rsp-S01518-87872016050006741-gf31.jpg',
    ]


def test_unexpected_files_list(test_package_C, test_packC_filenames):
    article = ArticleDocument('ID')
    article.xml_file = test_package_C[0]
    assets_files = [
        {
            'filename': asset_file.name,
            'content': asset_file.content,
            'content_size': asset_file.size
        }
        for asset_file in test_package_C[1:]
    ]
    article.update_asset_files(assets_files)

    assert len(article.assets) == 2
    assert sorted(article.assets.keys()) == sorted(
        [
            '0034-8910-rsp-S01518-87872016050006741-gf01-pt.jpg',
            '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
        ]
    )
    assert article.unexpected_files_list == [
       test_packC_filenames[3]
    ]
    assert article.missing_files_list == []


def test_update_href(test_package_A, test_packA_filenames,
                     test_packA_assets_files):
    new_href = 'novo href'
    filename = '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
    article = ArticleDocument('ID')
    article.xml_file = test_package_A[0]
    article.update_asset_files(test_packA_assets_files)
    content = article.xml_tree.content
    asset = article.assets.get(filename)
    asset.href = new_href
    items = [
        item
        for name, item in article.assets.items()
        if name == filename
    ]

    assert len(items) == 1
    assert not article.xml_tree.compare(content)
