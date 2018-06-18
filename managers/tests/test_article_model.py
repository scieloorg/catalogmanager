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
    checksum = hashlib.sha1(xml_file.content).hexdigest()
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


def test_update_href(test_package_A, test_packA_filenames):
    new_href = 'novo href'
    filename = '0034-8910-rsp-S01518-87872016050006741-gf01.jpg'
    xml_file = test_package_A[0]
    article = ArticleDocument('ID')
    article.xml_file = xml_file
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
