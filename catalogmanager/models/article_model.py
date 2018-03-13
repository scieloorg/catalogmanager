# coding=utf-8
import os

from ..xml import article_xml_tree


class Asset:

    def __init__(self, filename, asset_node):
        self.original_href = os.path.basename(filename)
        self.filename = filename
        self.asset_node = asset_node

    @property
    def file(self):
        return open(self.filename)

    def update_href(self, href):
        self.asset_node.update_href(href)

    @property
    def href(self):
        return self.asset_node.href


class Article:

    def __init__(self, xml_filename, files):
        self.basename = os.path.basename(xml_filename)
        self.filename = xml_filename
        self.article_xml_tree = article_xml_tree.ArticleXMLTree(xml_filename)
        self.files = files
        self.assets = None

    def link_files_to_assets(self):
        if self.article_xml_tree.asset_nodes is not None:
            self.assets = {}
            self.unlinked_assets = list(
                [os.path.basename(f) for f in self.files])
            self.unlinked_files = []

            for f in self.files:
                fname = os.path.basename(f)
                asset_node = self.article_xml_tree.asset_nodes.get(fname)
                if asset_node is None:
                    self.unlinked_files.append(fname)
                else:
                    self.unlinked_assets.remove(fname)
                    self.assets[fname] = Asset(f, asset_node)

    def update_href(self, asset_id_items):
        if self.assets is not None:
            for name, asset in self.assets.items():
                asset.update_href(asset_id_items[name])
