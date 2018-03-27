# coding=utf-8

from .xml_tree import (
    XMLTree,
    etree
)


class AssetXMLNode:

    _xpath = '{http://www.w3.org/1999/xlink}href'

    def __init__(self, node):
        self.node = node

    def update_href(self, value):
        self.node.set(self._xpath, value)

    @property
    def href(self):
        return self.node.get(self._xpath)

    @property
    def local_href(self):
        if self.href is not None and '/' not in self.href:
            return self.href

    @property
    def xml(self):
        return etree.tostring(self.node)

    @property
    def id(self):
        _id = self.get(
                'id',
                self.getparent().get(
                    'id',
                    self.original_href
                    )
                )
        return _id


class ArticleXMLTree(XMLTree):

    def __init__(self, xml):
        super().__init__(xml)

    @property
    def asset_nodes(self):
        if self.tree is not None:
            items = {}
            for node in self.nodes_which_has_xlink_href:
                asset_xml_node = AssetXMLNode(node)
                if asset_xml_node.local_href is not None:
                    items[asset_xml_node.local_href] = asset_xml_node
            return items

    @property
    def nodes_which_has_xlink_href(self):
        if self.tree is not None:
            return self.tree.findall('.//*[@{http://www.w3.org/1999/xlink}href]')
