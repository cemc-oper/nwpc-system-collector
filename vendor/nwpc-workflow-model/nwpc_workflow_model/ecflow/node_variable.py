# coding=utf-8
from enum import Enum


class NodeVariableType(Enum):
    variable = 'variable'
    generatedVariable = 'generatedVariable'


class NodeVariable(object):
    def __init__(self, variable_type, name, value):
        self.variable_type = NodeVariableType(variable_type)
        self.name = name
        self.value = value

    def to_dict(self):
        return {
            'name': self.name,
            'variable_type': self.variable_type.value,
            'value': self.value
        }

    @classmethod
    def create_from_dict(cls, var_dict):
        var = NodeVariable(var_dict['variable_type'], var_dict['name'], var_dict['value'])
        return var
