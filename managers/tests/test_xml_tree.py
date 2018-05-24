
from managers.xml.xml_tree import (
    XMLTree
)


def test_good_xml():
    xml = b'<article id="a1">\n<text/>\n</article>'
    xml_tree = XMLTree(xml)
    assert xml == xml_tree.content
    assert xml_tree.xml_error is None
    assert xml_tree.tree is not None


def test_bad_xml():
    xml = b'<article id="a1">\n<text>\n</article>'
    xml_tree = XMLTree(xml)
    assert xml_tree.content is None
    assert xml_tree.xml_error is not None
    assert xml_tree.tree is None


def test_compare_equal_xml():
    xml = b'<article id="a2">\n<text/>\n</article>'
    xml_tree = XMLTree(xml)
    assert xml_tree.content is not None
    assert xml_tree.compare(
        b'<article id="a2">\n<text/>\n</article>'
    )


def test_compare_not_equal_xml():
    xml = b'<article id="a2">\n<text/>\n</article>'
    xml_tree = XMLTree(xml)
    assert xml_tree.content is not None
    assert not xml_tree.compare(
        b'<article id="a1">\n<text/>\n</article>'
    )


def test_pretty():
    s_xml = """<article><p>A ljllj <bold>kjjflajfa,</bold> """ \
        """<italic>djajflaj</italic></p><p>Parágrafo 2</p></article>"""
    s_expected = """<article>\n  <p>A ljllj <bold>kjjflajfa,</bold> """ \
        """<italic>djajflaj</italic></p>\n  <p>Parágrafo 2</p>\n</article>\n"""

    xml = s_xml.encode('utf-8')
    expected = s_expected.encode('utf-8')
    xml_tree = XMLTree(xml)
    assert xml_tree.content is not None
    assert xml_tree.pretty == expected


def otimize(s_xml, s_expected):
    b_xml = s_xml.encode('utf-8')
    b_expected = s_expected.encode('utf-8')
    xml_tree = XMLTree(b_xml)
    assert xml_tree.content is not None
    assert xml_tree.otimized == b_expected


def test_otimized_preserva_tab_linebreak_em_elementos_que_contenham_texto():
    s_xml = '<article>' \
        '\n    <body>' \
        '\n        <p>A ljllj' \
        '\n            <bold>kjjflajfa,</bold>' \
        '\n            <italic>djajflaj</italic>' \
        '\n        </p>' \
        '\n        a   ' \
        '\n        <p>Parágrafo 2</p>' \
        '\n    </body>' \
        '\n</article>'

    s_expected = '<article>' \
        '<body>' \
        '<p>A ljllj' \
        '\n <bold>kjjflajfa,</bold>' \
        '\n <italic>djajflaj</italic>' \
        '\n </p>' \
        '\n a ' \
        '\n <p>Parágrafo 2</p>' \
        '\n </body></article>'
    otimize(s_xml, s_expected)


def test_otimized_preserva_tab_linebreak_em_elementos_que_contenham_texto2():
    s_xml = '<article> ' \
        '\nA ljllj\n          \t\t   \n    \t  ' \
        '\nkjjflajfa,  ' \
        '\ndjajflaj ' \
        '\na  ' \
        '\nParágrafo 2 ' \
        '\n</article>'
    s_expected = '<article> ' \
        '\nA ljllj\n \t\t \n \t ' \
        '\nkjjflajfa, ' \
        '\ndjajflaj ' \
        '\na ' \
        '\nParágrafo 2 ' \
        '\n</article>'
    otimize(s_xml, s_expected)


def test_otimized_estilos():
    s_xml = '<article><b>Bold</b> <i>itálico</i></article>'
    s_expected = '<article><b>Bold</b><i>itálico</i></article>'
    otimize(s_xml, s_expected)


def test_otimized_elimina_tab_linebreak_em_elementos_que_nao_contem_texto():
    s_xml = """
    <article>            \n\t   
        <p>A ljllj </p>
        <p>Parágrafo 2</p>\n\n\n\n
   </article>\n
    """
    s_expected = '<article><p>A ljllj </p><p>Parágrafo 2</p></article>'
    otimize(s_xml, s_expected)
