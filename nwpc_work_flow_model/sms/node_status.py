class NodeStatus(object):
    Unknown = 'unk'
    Suspend = 'sus'
    Complete = 'com'
    Queued = 'que'
    Submitted = 'sub'
    Active = 'act'
    Aborted = 'abo'
    Shutdown = 'shu'
    Halted = 'hal'

    status_mapper = {
        'unk': Unknown,
        'sus': Suspend,
        'com': Complete,
        'que': Queued,
        'sub': Submitted,
        'act': Active,
        'abo': Aborted,
        'shu': Shutdown,
        'hal': Halted
    }

    def __init__(self, status='unk'):
        if status in NodeStatus.status_mapper:
            self.status = NodeStatus.get_node_status(status)
        else:
            raise AttributeError("error status")

    @staticmethod
    def get_node_status(status_string):
        if status_string in NodeStatus.status_mapper:
            return NodeStatus.status_mapper[status_string]
        else:
            return None
