# coding=utf-8

from . import xml_tree


class AssetXMLNode:

    def __init__(self, xml_node):
        self.xml_node = xml_node

    def update_href(self, value):
        self.xml_node.set('{http://www.w3.org/1999/xlink}href]', value)


class AssetXMLNodesFinder:

    def __init__(self, tree):
        self.tree = tree

    @property
    def nodes_which_has_xlink_href(self):
        return self.tree.xpath('.//*[@{http://www.w3.org/1999/xlink}href]')

    @property
    def asset_nodes(self):
        items = {}
        for node in self.nodes_which_has_xlink_href:
            xml_node = xml_tree.XMLNode(node)
            if xml_node.local_href is not None:
                items[xml_node.local_href] = AssetXMLNode(xml_node)
        return items


class ArticleXMLTree:

    def __init__(self, xml_filename):
        self.xml_tree = xml_tree.XMLTree(xml_filename)

    @property
    def asset_nodes(self):
        return AssetXMLNodesFinder(self.xml_tree.tree).asset_nodes
