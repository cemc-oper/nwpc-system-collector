import datetime


class Node(object):
    def __init__(self):
        self.parent = None
        self.children = list()
        self.name = ''

    def __str__(self):
        return self.get_node_path()

    def add_child(self, node):
        self.children.append(node)

    def is_leaf(self):
        if len(self.children) == 0:
            return True
        else:
            return False

    def get_node_path(self):
        cur_node = self
        node_list = []
        while cur_node is not None:
            node_list.insert(0, cur_node.name)
            cur_node = cur_node.parent
        return "/".join(node_list)


class Bunch(Node):
    def __init__(self):
        Node.__init__(self)

    def add_node(self, node_path):
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


class NodeAnalyser(object):
    def __init__(self, database_engine):
        self.database_engine = database_engine

    def get_node_list(self, date):
        query = "SELECT DISTINCT `message_fullname` FROM {table_name} " \
                "WHERE message_date = '{date}' " \
                "AND message_fullname is not null ".format(
                table_name=self.database_engine.table_name, date=date)
        self.database_engine.cursor.execute(query)
        node_list = []
        for (node_full_name) in self.database_engine.cursor:
            node_list.append(node_full_name[0])

        return node_list

    def get_bunch(self, date):
        print "get node list..."
        node_list = self.get_node_list(date)

        print "building node tree..."
        bunch = Bunch()
        for a_node in node_list:
            bunch.add_node(a_node)

        return bunch

    def get_task_node_list(self, date):
        bunch = self.get_bunch(date)
        task_node_list = list()

        def pre_order_travel(root_node):
            if root_node.is_leaf():
                task_node_list.append(root_node)
            for child_node in root_node.children:
                pre_order_travel(child_node)

        pre_order_travel(bunch)

        return task_node_list