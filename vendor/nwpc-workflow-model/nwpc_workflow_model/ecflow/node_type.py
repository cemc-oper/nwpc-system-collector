# coding=utf-8
from enum import Enum


class NodeType(Enum):
    Unknown = 'unknown'
    Root = 'root'
    Suite = 'suite'
    Family = 'family'
    Task = 'task'
    Alias = 'alias'
    NonTaskNode = 'non-task'
    Meter = 'meter'

    @classmethod
    def get_node_type_string(cls, node_type):
        return node_type.value
