
from managers.models.article_model import (
    ArticleDocument,
)
from managers.xml.xml_tree import (
    XMLTree,
)


def test_article(test_package_A, test_packA_filenames):
    article = ArticleDocument('ID', test_package_A[0])
    article.update_asset_files(test_package_A[1:])
    expected = {
        'assets': [asset for asset in test_packA_filenames[1:]],
        'xml': test_packA_filenames[0],
    }
    assert article.xml_file.name == test_packA_filenames[0]
    assert article.xml_file.content == test_package_A[0].content
    assert article.xml_tree.xml_error is None
    assert article.xml_tree.compare(test_package_A[0].content)
    assert article.get_record_content() == expected


def test_missing_files_list(test_package_B):
    article = ArticleDocument('ID', test_package_B[0])
    article.update_asset_files(test_package_B[1:])

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
    article = ArticleDocument('ID', test_package_C[0])
    article.update_asset_files(test_package_C[1:])

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


def test_update_href(test_package_A, test_packA_filenames):
    new_href = 'novo href'
    filename = '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
    article = ArticleDocument('ID', test_package_A[0])
    article.update_asset_files(test_package_A[1:])
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
