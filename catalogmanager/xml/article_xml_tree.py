# coding=utf-8

from . import xml_tree


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
        return xml_tree.etree.tostring(self.node)

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


class AssetXMLNodesFinder:

    def __init__(self, tree):
        self.tree = tree

    @property
    def nodes_which_has_xlink_href(self):
        return self.tree.findall('.//*[@{http://www.w3.org/1999/xlink}href]')

    @property
    def asset_nodes(self):
        items = {}
        for node in self.nodes_which_has_xlink_href:
            asset_xml_node = AssetXMLNode(node)
            if asset_xml_node.local_href is not None:
                items[asset_xml_node.local_href] = asset_xml_node
        return items


class ArticleXMLTree:

    def __init__(self, xml_filename):
        self.xml_tree = xml_tree.XMLTree(xml_filename)

    @property
    def asset_nodes(self):
        if self.xml_tree.tree is not None:
            return AssetXMLNodesFinder(self.xml_tree.tree).asset_nodes

    @property
    def content(self):
        return self.xml_tree.content
