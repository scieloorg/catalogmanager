# coding=utf-8
import os

from . import article_xml_tree


class Asset:

    def __init__(self, filename, asset_node):
        self.basename = os.path.basename(filename)
        self.filename = filename
        self.asset_node = asset_node

    @property
    def file(self):
        return open(self.filename)


class Article:

    def __init__(self, xml_filename, files):
        self.basename = os.path.basename(xml_filename)
        self.filename = xml_filename
        self.xml_tree = article_xml_tree.ArticleXMLTree(xml_filename)
        self.files = files

    def link_files_to_assets(self):
        self.assets = {}
        self.unlinked_assets = list([os.path.basename(f) for f in self.files])
        self.unlinked_files = []

        if self.xml_tree.asset_nodes is not None:
            for f in self.files:
                fname = os.path.basename(f)
                asset_node = self.xml_tree.asset_nodes.get(fname)
                if asset_node is None:
                    self.unlinked_files.append(fname)
                else:
                    self.unlinked_assets.remove(fname)
                    self.assets[fname] = Asset(f, asset_node)

    def update_href(self, asset_id_items):
        for name, asset in self.assets.items():
            asset.asset_node.update_href(asset_id_items[name])
