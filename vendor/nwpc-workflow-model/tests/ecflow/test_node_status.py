# coding=utf-8
import pytest
from nwpc_workflow_model.ecflow import NodeStatus


class TestNodeStatus:
    @classmethod
    def setup_class(cls):
        pass

    def test_construction(self):
        node_status = NodeStatus.unknown
        assert node_status == NodeStatus.unknown

        node_status = NodeStatus('active')
        assert node_status == NodeStatus.active

        node_status = NodeStatus['active']
        assert node_status == NodeStatus.active

        with pytest.raises(ValueError):
            NodeStatus('non-exist-status')

    def test_get_node_status(self):
        mapper = {
            'unknown': NodeStatus.unknown,
            'suspended': NodeStatus.suspended,
            'complete': NodeStatus.complete,
            'queued': NodeStatus.queued,
            'submitted': NodeStatus.submitted,
            'active': NodeStatus.active,
            'aborted': NodeStatus.aborted,
            'SHUTDOWN': NodeStatus.SHUTDOWN,
            'HALTED': NodeStatus.HALTED,
            'RUNNING': NodeStatus.RUNNING
        }

        result_list = [NodeStatus.get_node_status(i) == mapper[i] for i in mapper]
        assert all(result_list)

        result_list = [NodeStatus(i) == mapper[i] for i in mapper]
        assert all(result_list)

        assert NodeStatus.get_node_status('non-exist-status') is None
