# coding=utf-8

import ecflow
from nwpc_workflow_model.ecflow.ecflow_node import EcflowNode
from nwpc_workflow_model.ecflow.node_variable import NodeVariable, NodeVariableType
from nwpc_workflow_model.ecflow import NodeStatus, NodeType


def get_node_variable_only(node):
    ecf_node = EcflowNode()

    ecf_node.name = node.name()
    ecf_node.path = node.get_abs_node_path()
    ecf_node.status = NodeStatus(str(node.get_dstate()))
    if isinstance(node, ecflow.Alias):
        ecf_node.node_type = NodeType.alias
    elif isinstance(node, ecflow.Task):
        ecf_node.node_type = NodeType.task
    elif isinstance(node, ecflow.Family):
        ecf_node.node_type = NodeType.family
    elif isinstance(node, ecflow.Suite):
        ecf_node.node_type = NodeType.suite
    else:
        ecf_node.node_type = NodeType.unknown

    for a_var in node.variables:
        ecf_node.variable_list.append(
            NodeVariable(
                NodeVariableType.variable,
                a_var.name(),
                a_var.value())
        )

    gen_var_list = ecflow.VariableList()
    node.get_generated_variables(gen_var_list)
    for a_var in gen_var_list:
        ecf_node.generated_variable_list.append(
            NodeVariable(
                NodeVariableType.generatedVariable,
                a_var.name(),
                a_var.value()
            )
        )

    return ecf_node


def get_node_variable(node):
    ecf_node = get_node_variable_only(node)

    parent = node.get_parent()

    while parent:
        parent_ecf_node = get_node_variable_only(parent)

        ecf_node.inherited_variable_list.append({
            'path': parent_ecf_node.path,
            'variable_list': parent_ecf_node.variable_list,
            'generated_variable_list': parent_ecf_node.generated_variable_list
        })
        parent = parent.get_parent()

    return ecf_node
