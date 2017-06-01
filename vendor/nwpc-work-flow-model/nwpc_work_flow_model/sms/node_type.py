class NodeType(object):
    Unknown = 1
    Root = 2
    Suite = 3
    Family = 4
    Task = 5
    Alias = 6
    NonTaskNode = 7
    Meter = 8

    node_type_mapper = {
        Unknown: 'unknown',
        Root: 'root',
        Suite: 'suite',
        Family: 'family',
        Task: 'task',
        Alias: 'alias',
        NonTaskNode: 'non-task',
        Meter: 'meter',
    }

    def __init__(self):
        self.node_state = self.Unknown

    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

    @staticmethod
    def get_node_type_string(node_type):
        if node_type in NodeType.node_type_mapper:
            return NodeType.node_type_mapper[node_type]
        else:
            return None
