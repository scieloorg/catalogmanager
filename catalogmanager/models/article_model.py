# coding=utf-8
import os
import mimetypes

from ..xml.article_xml_tree import ArticleXMLTree


class File:

    def __init__(self, file_fullpath):
        self.file_fullpath = file_fullpath
        self.name = None
        self.path = None
        self.size = None
        self.content_type = None
        self.content = None
        if file_fullpath is not None and os.path.isfile(file_fullpath):
            self.name = os.path.basename(file_fullpath)
            self.path = os.path.dirname(file_fullpath)
            self.size = os.stat(file_fullpath).st_size
            self.content_type = mimetypes.guess_type(file_fullpath)
            self.content = open(file_fullpath)


class Asset:

    def __init__(self, asset_node, asset_file=None):
        self.file = asset_file
        self.node = asset_node
        self.name = asset_node.href
        self.document_id = None

    def get_record_content(self):
        return {'file_href': self.name, 'file_id': self.file.name}

    @property
    def href(self):
        if self.node is not None:
            return self.node.href

    @href.setter
    def href(self, value):
        if self.node is not None:
            self.node.href = value


class Article:

    def __init__(self, xml=None, asset_files=None):
        self.id = None
        self.xml_tree = xml
        self.asset_files = asset_files
        if asset_files is not None:
            self.asset_files = {os.path.basename(f): f for f in asset_files if os.path.isfile(f)}
        self.assets = {name: Asset(node, File(self.asset_files.get(name))) for name, node in self.xml_tree.asset_nodes.items()}

    @property
    def xml_tree(self):
        return self._xml_tree

    @xml_tree.setter
    def xml_tree(self, xml):
        self._xml_tree = ArticleXMLTree(xml)

    def get_record_content(self):
        record_content = {}
        record_content['xml'] = self.xml_tree.file_name
        record_content['assets'] = []
        for asset in self.assets.values():
            asset.document_id = self.id
            record_content['assets'].append(asset.get_record_content())
        print('record', record_content)
        return record_content

    @property
    def missing_files_list(self):
        _missing_files_list = []
        if self.assets is not None:
            _missing_files_list = [item for item in self.assets.keys() if item not in self.asset_files.keys()]
        return _missing_files_list

    @property
    def unexpected_files_list(self):
        _unexpected_files_list = []
        if self.asset_files is not None:
            _unexpected_files_list = [item for item in self.asset_files.keys() if item not in self.assets.keys()]
        return _unexpected_files_list
