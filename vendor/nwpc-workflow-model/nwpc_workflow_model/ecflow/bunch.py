# coding=utf-8
from .node import Node, NodeStatus


class Bunch(Node):
    """
    Node tree
    """
    def __init__(self):
        Node.__init__(self)
        self.parent = None
        self.children = list()
        self.name = ''
        self.status = NodeStatus.unknown

    @classmethod
    def create_from_dict(cls, node_dict, parent=None):
        """
        Build bunch from a dict. Only the root node is a Bunch, while the others are Node.

        :param node_dict:
        :param parent:
        :return: bunch
        """
        # use parent is evil.
        bunch = Bunch()
        bunch.parent = parent
        bunch.name = node_dict['name']
        bunch.status = NodeStatus.get_node_status(node_dict['status'])
        for a_child_item in node_dict['children']:
            a_child_node = Node.create_from_dict(a_child_item, parent=bunch)
            bunch.children.append(a_child_node)
        return bunch

    def add_node(self, node_path):
        """
        Add node which node path is node_path, return added node or None

        :param node_path: node path of the node to be added
        :return:
        """
        if node_path == '/':
            return self
        node = None
        if node_path[0] != '/':
            return node
        node_path = node_path[1:]
        tokens = node_path.split("/")
        cur_node = self
        for a_token in tokens:
            t_node = None
            for a_child in cur_node.children:
                if a_child.name == a_token:
                    t_node = a_child
                    break
            if t_node is None:
                t_node = Node()
                t_node.parent = cur_node
                t_node.name = a_token
                cur_node.add_child(t_node)
            cur_node = t_node
        return cur_node

    def add_node_status(self, node_status_object):
        node_path = node_status_object['path']
        node_status = node_status_object['status']
        node_name = node_status_object['name']

        node = self.add_node(node_path)
        node.status = node_status
        node.name = node_name
        return node

    def find_node(self, node_path):
        if node_path == '/':
            return self
        if node_path[0] != '/':
            return None
        node_path = node_path[1:]
        tokens = node_path.split("/")
        cur_node = self
        for a_token in tokens:
            t_node = None
            for a_child in cur_node.children:
                if a_child.name == a_token:
                    t_node = a_child
                    break
            if t_node is None:
                return None
            cur_node = t_node
        return cur_node

