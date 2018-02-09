# coding: utf-8
from enum import Enum


class NodeStatus(Enum):
    unknown = 'unknown'
    suspended = 'suspended'
    complete = 'complete'
    queued = 'queued'
    submitted = 'submitted'
    active = 'active'
    aborted = 'aborted'
    SHUTDOWN = 'SHUTDOWN'
    HALTED = 'HALTED'
    RUNNING = 'RUNNING'

    @classmethod
    def get_node_status(cls, status_string):
        if status_string in cls.__members__:
            return NodeStatus(status_string)
        else:
            return None
