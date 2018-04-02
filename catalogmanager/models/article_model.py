# coding=utf-8
import os
from uuid import uuid4

from ..xml.article_xml_tree import ArticleXMLTree


class Asset:

    def __init__(self, filename):
        self.name = os.path.basename(filename)
        self.filename = filename
        self.article_id = None

    def get_record_content(self):
        record_content = {}
        record_content['article_id'] = self.article_id
        record_content['name'] = self.name
        record_content['filename'] = self.filename
        return record_content

    @property
    def href(self):
        if self.asset_node is not None:
            return self.asset_node.href
        return self.name

    def update_href(self, href):
        if self.asset_node is not None:
            self.asset_node.update_href(href)


class Article:

    def __init__(self, xml=None, files=None):
        self.id = self._get_id()
        self.xml_tree = xml
        self.files = files

    @property
    def xml_tree(self):
        return self._xml_tree

    @xml_tree.setter
    def xml_tree(self, xml):
        self._xml_tree = ArticleXMLTree(xml)

    def _get_id(self):
        return uuid4().hex

    def get_record_content(self):
        record_content = {}
        record_content['xml_name'] = self.xml_tree.basename
        record_content['assets_names'] = list(self.xml_tree.asset_nodes.keys())
        return record_content

    @property
    def required_files(self):
        _required_files = []
        if self.xml_tree.asset_nodes is not None:
            _required_files = self.xml_tree.asset_nodes.keys()
            if self.files is not None:
                for f in self.files:
                    name = os.path.basename(f)
                    if name in _required_files:
                        _required_files.remove(name)
        return _required_files

    @property
    def unexpected_files(self):
        _unexpected_files = []
        if self.files is not None:
            _unexpected_files = [os.path.basename(f) for f in self.files]
            if self.xml_tree.asset_nodes is not None:
                for name in self.xml_tree.asset_nodes.keys():
                    if name in _unexpected_files:
                        _unexpected_files.remove(name)
        return _unexpected_files
