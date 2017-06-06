import unittest
from datetime import datetime
from nwpc_log_collector import database_engine
from nwpc_log_collector import time_analyser
from nwpc_log_collector.message import Message


class TimeAnalyserTest(unittest.TestCase):

    def setUp(self):
        self.start_time = datetime.utcnow()
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
        self.end_time = datetime.utcnow()
        print "end at ", self.end_time
        print self.end_time - self.start_time

    def test_calculate_meter_total_time(self):
        ta = time_analyser.TimeAnalyser(self.engine)
        ta.calculate_meter_total_time('/grapes_meso_v4_0/cold/00/model/fcst:steps',
                                      '2014-10-03', 1, 4320)

    def test_get_meter_step_time_list(self):
        ta = time_analyser.TimeAnalyser(self.engine)
        time_map = ta.get_meter_step_time_list(
            '/grapes_meso_v4_0/cold/00/model/fcst:steps', '2014-10-03')
        print time_map

    def test_calculate_node_time(self):
        ta = time_analyser.TimeAnalyser(self.engine)
        node_time = ta.calculate_node_time(
            '/grapes_meso_v4_0/cold/00/model/fcst', '2014-10-03')
        print node_time

if __name__ == '__main__':
    unittest.main()
