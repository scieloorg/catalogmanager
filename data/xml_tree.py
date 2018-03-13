# coding=utf-8

import os

from lxml import etree
from StringIO import StringIO

namespaces = {}
namespaces['mml'] = 'http://www.w3.org/1998/Math/MathML'
namespaces['xlink'] = 'http://www.w3.org/1999/xlink'
namespaces['xml'] = 'http://www.w3.org/XML/1998/namespace'

for namespace_id, namespace_link in namespaces.items():
    etree.register_namespace(namespace_id, namespace_link)


class XMLTree:

    def __init__(self, xml):
        self.load(xml)

    @property
    def content(self):
        return etree.tostring(self.tree.getroot())

    def load(self, xml):
        self.tree, self.xml_error = self.parse(self.read(xml))

    def read(self, xml):
        self.filename = None
        self.basename = None
        if '<' not in xml:
            self.filename = xml
            self.basename = os.path.basename(self.filename)
            xml = open(xml).read()
        return StringIO(xml)

    def parse(self, content):
        message = None
        try:
            r = etree.parse(content)
        except Exception as e:
            message = 'XML is not well formed\n'
            r = None
        return (r, message)


class XMLNode:

    def __init__(self, node):
        self.node = node

    @property
    def href(self):
        return self.xml_node.get('{http://www.w3.org/1999/xlink}href')

    @property
    def local_href(self):
        if self.href is not None and '/' not in self.href:
            return self.href
