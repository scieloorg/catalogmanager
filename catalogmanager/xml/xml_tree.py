# coding=utf-8

from lxml import etree
from io import (
    BytesIO,
    StringIO,
)


namespaces = {}
namespaces['mml'] = 'http://www.w3.org/1998/Math/MathML'
namespaces['xlink'] = 'http://www.w3.org/1999/xlink'
namespaces['xml'] = 'http://www.w3.org/XML/1998/namespace'

for namespace_id, namespace_link in namespaces.items():
    etree.register_namespace(namespace_id, namespace_link)


class XMLTree:

    def __init__(self, xml_content):
        self.tree = None
        self.xml_error = None
        self.content = xml_content

    @property
    def content(self):
        if self.tree is not None:
            return etree.tostring(self.tree.getroot(), encoding='utf-8')

    @content.setter
    def content(self, xml_content):
        bytes_io = BytesIO(xml_content)
        self.tree, self.xml_error = self.parse(bytes_io)

    def parse(self, bytes_io):
        message = None
        try:
            r = etree.parse(bytes_io)
        except Exception as e:
            message = 'XML is not well formed\n'
            r = None
        return (r, message)

    def compare(self, xml_content):
        return self.content == xml_content

    @property
    def pretty(self):
        return etree.tostring(
            self.tree.getroot(),
            encoding='utf-8',
            pretty_print=True)

    @property
    def otimized(self):
        parser = etree.XMLParser(remove_blank_text=True)
        content = self.content.decode('utf-8')
        root = etree.XML(content, parser)
        b = etree.tostring(root, encoding='utf-8')
        s = b.decode('utf-8')
        while ' '*2 in s:
            s = s.replace(' '*2, ' ')
        return s.encode('utf-8')
