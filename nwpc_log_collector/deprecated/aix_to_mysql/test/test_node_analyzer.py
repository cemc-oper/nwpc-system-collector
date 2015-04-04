import unittest
from datetime import datetime
from nwpc_log_collector import database_engine
from nwpc_log_collector import node_analyser


class NodeAnalyserTestCase(unittest.TestCase):
    def setUp(self):
        self.start_time = datetime.now()
        print "begin at ", self.start_time
        self.database = 'smslog'
        self.user_name = 'nwp'
        self.host_name = 'cma20n03'
        self.table_name = 'message_choice_{user_name}_{host_name}'.format(
            user_name=self.user_name, host_name=self.host_name)
        self.engine_config = {
            'user': 'windroc',
            'password': 'shenyang',
            'host': '10.28.32.175',
            'database': self.database,
            'table_name': self.table_name
        }
        self.engine = database_engine.DatabaseEngine()
        self.engine.create_connect(self.engine_config)
        self.cursor = self.engine.create_cursor()

    def tearDown(self):
        self.engine.close_cursor()
        self.engine.close_connect()
        self.end_time = datetime.now()
        print "end at ", self.end_time
        print self.end_time - self.start_time

    def test_get_bunch(self):
        na = node_analyser.NodeAnalyser(self.engine)
        bunch = na.get_bunch("2014-10-01")
        for node in bunch.children:
            print node.get_node_path()

    def test_get_task_node_list(self):
        na = node_analyser.NodeAnalyser(self.engine)
        task_node_list = na.get_task_node_list("2014-10-01")
        print task_node_list,


if __name__ == '__main__':
    unittest.main()
