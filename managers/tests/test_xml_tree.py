
from managers.xml.xml_tree import (
    XMLTree
)


def test_good_xml():
    xml = b'<article id="a1">\n<text/>\n</article>'
    xml_tree = XMLTree()
    xml_tree.content = xml
    assert xml == xml_tree.content
    assert xml_tree.xml_error is None
    assert xml_tree.tree is not None


def test_bad_xml():
    xml = b'<article id="a1">\n<text>\n</article>'
    xml_tree = XMLTree()
    xml_tree.content = xml
    assert xml_tree.content is None
    assert xml_tree.xml_error is not None
    assert xml_tree.tree is None


def test_compare_equal_xml():
    xml = b'<article id="a2">\n<text/>\n</article>'
    xml_tree = XMLTree()
    xml_tree.content = xml
    assert xml_tree.content is not None
    assert xml_tree.compare(
        b'<article id="a2">\n<text/>\n</article>'
    )


def test_compare_not_equal_xml():
    xml = b'<article id="a2">\n<text/>\n</article>'
    xml_tree = XMLTree()
    xml_tree.content = xml
    assert xml_tree.content is not None
    assert not xml_tree.compare(
        b'<article id="a1">\n<text/>\n</article>'
    )
