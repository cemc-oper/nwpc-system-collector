# coding=utf-8
from nwpc_workflow_model.ecflow.node_variable import NodeVariableType, NodeVariable


class TestNodeVariable(object):
    def test_create(self):
        var_name = 'var_name'
        var_type = NodeVariableType.variable
        var_value = 'var value'
        var = NodeVariable(var_type, var_name, var_value)
        assert var.name == var_name
        assert var.variable_type == var_type
        assert var.value == var_value

    def test_to_dict(self):
        var_name = 'var_name'
        var_type = NodeVariableType.variable
        var_value = 'var value'
        var = NodeVariable(var_type, var_name, var_value)
        var_dict = var.to_dict()
        assert var_dict['name'] == var_name
        assert var_dict['variable_type'] == var_type.value
        assert var_dict['value'] == var_value

    def test_create_from_dict(self):
        var_name = 'var_name'
        var_type = 'variable'
        var_value = 'var value'
        var_dict = {
            'name': var_name,
            'variable_type': var_type,
            'value': var_value
        }
        var = NodeVariable.create_from_dict(var_dict)

        assert var.name == var_name
        assert var.variable_type == NodeVariableType(var_type)
        assert var.value == var_value
