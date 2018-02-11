# coding=utf-8
from enum import Enum


class NodeType(Enum):
    unknown = 'unknown'
    root = 'root'
    suite = 'suite'
    family = 'family'
    task = 'task'
    alias = 'alias'
    nonTaskNode = 'non-task'
    meter = 'meter'

    @classmethod
    def get_node_type_string(cls, node_type):
        return node_type.value
