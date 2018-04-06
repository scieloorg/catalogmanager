# coding=utf-8
import os

from ..xml.article_xml_tree import ArticleXMLTree

from .file import (
    File
)


class Asset:

    def __init__(self, asset_node):
        self.file = None
        self.node = asset_node
        self.name = asset_node.href

    @property
    def href(self):
        if self.node is not None:
            return self.node.href

    @href.setter
    def href(self, value):
        if self.node is not None:
            self.node.href = value


class Article:

    def __init__(self, article_id):
        self.id = article_id
        self.assets = {}
        self.unexpected_files_list = []

    @property
    def xml_file(self):
        return self._xml_file

    @xml_file.setter
    def xml_file(self, xml_file_path):
        self._xml_file = File(xml_file_path)
        self.xml_tree = ArticleXMLTree()
        self.xml_tree.content = self._xml_file.content
        self.assets = {
            name: Asset(node)
            for name, node in self.xml_tree.asset_nodes.items()
        }

    def update_asset_files(self, files):
        updated = []
        if files is not None:
            for f in files:
                updated.append(self.update_asset_file(f))
        return updated

    def update_asset_file(self, file):
        if file is not None and os.path.isfile(file):
            name = os.path.basename(file)
            if name in self.assets.keys():
                self.assets[name].file = File(file)
                return self.assets[name]
            self.unexpected_files_list.append(file)

    def get_record_content(self):
        record_content = {}
        record_content['xml'] = self.xml_file.name
        record_content['assets'] = []
        for asset in self.assets.values():
            record_content['assets'].append(asset.name)
        return record_content

    @property
    def missing_files_list(self):
        return [
            name
            for name, asset in self.assets.items()
            if asset.file is None
        ]
