# coding=utf-8

from lxml import etree
from io import BytesIO


namespaces = {}
namespaces['mml'] = 'http://www.w3.org/1998/Math/MathML'
namespaces['xlink'] = 'http://www.w3.org/1999/xlink'
namespaces['xml'] = 'http://www.w3.org/XML/1998/namespace'

for namespace_id, namespace_link in namespaces.items():
    etree.register_namespace(namespace_id, namespace_link)


class XMLTree:

    def __init__(self):
        self.tree = None
        self.xml_error = None

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
