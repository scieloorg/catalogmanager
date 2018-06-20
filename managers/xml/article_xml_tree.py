# coding=utf-8
import hashlib

from .xml_tree import (
    XMLTree,
)


class HRefNode:

    _xpath = '{http://www.w3.org/1999/xlink}href'

    def __init__(self, node):
        self.node = node

    @property
    def href(self):
        return self.node.get(self._xpath)

    @href.setter
    def href(self, value):
        self.node.set(self._xpath, value)

    @property
    def local_href(self):
        if (self.href is not None and
                ('/' not in self.href or self.href.startswith('/'))):
            return self.href

    @property
    def external_href(self):
        if self.href is not None and '/' in self.href:
            return self.href


class ArticleXMLTree(XMLTree):

    @property
    def asset_nodes(self):
        if self.tree is not None:
            items = {}
            for node in self.nodes_which_has_xlink_href:
                href_node = HRefNode(node)
                if href_node.local_href is not None:
                    items[href_node.local_href] = href_node
            return items

    @property
    def nodes_which_has_xlink_href(self):
        if self.tree is not None:
            return self.tree.findall(
                './/*[@{http://www.w3.org/1999/xlink}href]')

    @property
    def checksum(self):
        return hashlib.sha1(self.content).hexdigest()
