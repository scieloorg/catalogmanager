# coding=utf-8
import os

from ..xml.article_xml_tree import ArticleXMLTree


class Asset:

    def __init__(self, filename, asset_node):
        self.original_href = os.path.basename(filename)
        self.filename = filename
        self.asset_node = asset_node
        self.article_id = None

    def get_content(self):
        record = {}
        record['article_id'] = self.article_id
        record['filename'] = self.filename
        record['file'] = self.file
        record['node'] = self.asset_node
        record['location'] = self.href
        record['original_href'] = self.original_href
        return record

    @property
    def name(self):
        return self.original_href

    @property
    def file(self):
        if os.path.isfile(self.filename):
            return open(self.filename)

    @property
    def href(self):
        return self.asset_node.href

    def update_href(self, href):
        self.asset_node.update_href(href)


class Article:

    def __init__(self, xml=None, files=None):
        self.xml_tree = xml
        self.files = files
        self.assets = None
        self.location = None

    @property
    def xml_tree(self):
        return self._xml_tree

    @xml_tree.setter
    def xml_tree(self, xml):
        self._xml_tree = ArticleXMLTree(xml)

    def get_content(self, asset_id_items=None):
        record_content = {}
        record_content['location'] = self.location
        record_content['filename'] = self.xml_tree.filename
        record_content['basename'] = self.xml_tree.basename
        record_content['xml_content'] = self.xml_content
        record_content['assets'] = asset_id_items
        return record_content

    def link_files_to_assets(self):
        if self.xml_tree.asset_nodes is not None:
            self.assets = {}
            self.unlinked_assets = [os.path.basename(f) for f in self.files]
            self.unlinked_files = []
            for f in self.files:
                fname = os.path.basename(f)
                asset_node = self.xml_tree.asset_nodes.get(fname)
                if asset_node is None:
                    self.unlinked_files.append(fname)
                else:
                    self.unlinked_assets.remove(fname)
                    self.assets[fname] = Asset(
                        f, asset_node)

    def update_href(self, asset_id_items):
        if self.assets is not None:
            for name, asset in self.assets.items():
                self.assets[name].update_href(asset_id_items[name])

    @property
    def xml_content(self):
        return self.xml_tree.content
