import hashlib

import pytest

from managers.models.article_model import (
    ArticleDocument,
    InvalidXMLContent
)
from managers.xml.article_xml_tree import ArticleXMLTree


def test_article_document(test_package_A, test_packA_filenames):
    article_document = ArticleDocument('ID')
    assert article_document.id == 'ID'
    assert article_document.versions == []
    assert article_document.get_record() == {
        'document_id': 'ID',
        'document_type': 'ART',
        'versions': []
    }


def test_article_invalid_xml():
    article_document = ArticleDocument('ID')
    with pytest.raises(InvalidXMLContent):
        article_document.add_version(
            'file.xml',
            b'<article id="a1">\n<text>\n</article>'
        )


def test_article_document_add_version(test_package_A, test_packA_filenames):
    xml_file = test_package_A[0]
    checksum = hashlib.sha1(
        ArticleXMLTree(xml_file.content).content).hexdigest()
    filename = '/'.join([checksum[:13], xml_file.name])
    expected = {
        'document_id': 'ID',
        'document_type': 'ART',
        'versions': [
            {
                'data': filename,
                'assets': []
            }
        ]
    }
    article_document = ArticleDocument('ID')
    article_document.add_version(file_id=xml_file.name,
                                 xml_content=xml_file.content)
    assert article_document.xml_file_id == filename
    assert article_document.xml_tree is not None
    assert isinstance(article_document.xml_tree, ArticleXMLTree)
    assert article_document.xml_tree.xml_error is None
    assert article_document.xml_tree.compare(xml_file.content)
    assert article_document.get_record() == expected


def test_article_update_asset_files(test_package_A, test_packA_filenames):
    article = ArticleDocument('ID')
    article.xml_file = test_package_A[0]
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
    article = ArticleDocument('ID')
    article.xml_file = test_package_B[0]
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
    article = ArticleDocument('ID')
    article.xml_file = test_package_C[0]
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
    article = ArticleDocument('ID')
    article.xml_file = test_package_A[0]
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


def test_v0_to_v1():
    record_v0 = {
        'document_id': '0034-8910-rsp-48-2-0275',
        'document_type': 'X',
        'created_date': 'Xc',
        'updated_date': 'X3',
        'document_rev': 'Xba',
        'attachments': [
            '0034-8910-rsp-48-2-0275.xml',
            '0034-8910-rsp-48-2-0275-gf01.gif'],
        'content': {'xml': '0034-8910-rsp-48-2-0275.xml'},
    }
    expected = {
      "id": "0034-8910-rsp-48-2-0275",
      "versions": [
        {"data":
         "/rawfiles/0034-8910-rsp-48-2-0275/0034-8910-rsp-48-2-0275.xml",
         "assets": [
           {"0034-8910-rsp-48-2-0275-gf01.gif": [
                "/rawfiles/0034-8910-rsp-48-2-0275/"
                "0034-8910-rsp-48-2-0275-gf01.gif"
                ]}
            ]
         }
      ]
    }
    article = ArticleDocument('ID')
    assert article._v0_to_v1(record_v0) == expected


def test_record_v0_set(test_package_A):
    article = ArticleDocument('ID')
    record = {
            'document_id': 'x',
            'document_type': 'X',
            'created_date': 'Xc',
            'updated_date': 'X3',
            'document_rev': 'Xba',
            'attachments': ['a.xml', 'a1.jpg'],
            'content': {'xml': 'a.xml'},
        }
    article.set_data(record)

    assert article.id == 'x'
    assert article.manifest == article._v0_to_v1(record)
    assert article.id == article.manifest['id']


def test_assets_last_version():
    manifest = {
      "id": "0034-8910-rsp-48-2-0275",
      "versions": [
        {
            "data": "/rawfiles/7ca9f9b2687cb/0034-8910-rsp-48-2-0275.xml",
            "assets": [
                {"0034-8910-rsp-48-2-0275-gf01.gif": [
                    "/rawfiles/8e644999a8fa4/0034-8910-rsp-48-2-0275-gf01.gif",
                    "/rawfiles/bf139b9aa3066/0034-8910-rsp-48-2-0275-gf01.gif"
                    ]
                },
            ]
        },
      ]
    }
    expected = [
        {
            "0034-8910-rsp-48-2-0275-gf01.gif": [
                "/rawfiles/bf139b9aa3066/0034-8910-rsp-48-2-0275-gf01.gif"]
        }
    ]

    article = ArticleDocument('ID')
    article.set_data(manifest)
    assert article.assets_last_version == expected
