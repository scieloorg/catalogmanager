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
    def xml_file(self, xml_file):
        self._xml_file = xml_file
        self.xml_tree = ArticleXMLTree()
        self.xml_tree.content = self._xml_file.content
        self.assets = {
            name: Asset(node)
            for name, node in self.xml_tree.asset_nodes.items()
        }

    def update_asset_files(self, files):
        updated = []
        if files is not None:
            for file_properties in files:
                updated.append(self.update_asset_file(file_properties))
        return updated

    def update_asset_file(self, file_properties):
        if file_properties.get('filename'):
            name = os.path.basename(file_properties['filename'])
            if name in self.assets.keys():
                asset_file = File(file_properties['filename'])
                asset_file.content = file_properties['content']
                asset_file.size = file_properties['content_size']
                self.assets[name].file = asset_file
                return self.assets[name]
            self.unexpected_files_list.append(file_properties['filename'])

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
