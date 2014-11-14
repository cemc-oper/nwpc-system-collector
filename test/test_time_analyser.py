import unittest
from datetime import datetime
from sms_log_collector import database_engine
from sms_log_collector import time_analyser


class TimeAnalyserTest(unittest.TestCase):
    def test_calculate_meter_step_time(self):
        print "begin at ", datetime.now()
        database = 'smslog'
        user_name = 'nwp_qu'
        host_name = 'cma18n03'
        table_name = 'message_{user_name}_{host_name}'.format(user_name=user_name, host_name=host_name)
        engine_config = {
            'user': 'wangdp',
            'password': 'shenyang',
            'host': 'localhost',
            'database': database,
            'table_name': table_name
        }

        engine = database_engine.DatabaseEngine()
        engine.create_connect(engine_config)
        cursor = engine.create_cursor()

        ta = time_analyser.TimeAnalyser(engine)
        ta.calculate_meter_step_time('/geps_t639/00/members/pair_3/mem1/model/forecast:completed',
                                     '2014-11-03', 1, 2160)

        print "end at ",datetime.now()


if __name__ == '__main__':
    unittest.main()
