# coding=utf-8

import os

from lxml import etree
from io import StringIO


namespaces = {}
namespaces['mml'] = 'http://www.w3.org/1998/Math/MathML'
namespaces['xlink'] = 'http://www.w3.org/1999/xlink'
namespaces['xml'] = 'http://www.w3.org/XML/1998/namespace'

for namespace_id, namespace_link in namespaces.items():
    etree.register_namespace(namespace_id, namespace_link)


class XMLTree:

    def __init__(self, xml):
        self.tree = None
        self.xml_error = None
        self.load(xml)

    def _tostring(self):
        return etree.tostring(self.tree.getroot(), encoding='utf-8')

    @property
    def file_name(self):
        if os.path.isfile(self.file_fullpath):
            return os.path.basename(self.file_fullpath)

    @property
    def content(self):
        return str(self.bytes_content)

    @property
    def bytes_content(self):
        return self._tostring()

    def load(self, xml):
        self.tree, self.xml_error = self.parse(self.read(xml))

    def read(self, xml):
        self.file_fullpath = None
        if '<' not in xml:
            self.file_fullpath = xml
            xml = open(self.file_fullpath).read()
        return StringIO(xml)

    def parse(self, content):
        message = None
        try:
            r = etree.parse(content)
        except Exception as e:
            message = 'XML is not well formed\n'
            raise e
            r = None
        return (r, message)
