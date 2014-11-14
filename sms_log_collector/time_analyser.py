import datetime

class TimeAnalyser(object):
    def __init__(self, database_engine):
        self.database_engine = database_engine

    def calculate_meter_step_time(self, meter_name, date, start_step, end_step):
        self.database_engine.create_cursor()
        cursor = self.database_engine.select_message(
            where_string="WHERE message_fullname='{meter_name}' "
                         "AND DATE(message_time)='{date}'".format(
                meter_name=meter_name, date=date
            ),
            order_by_string="ORDER BY message_id "
        )
        start_step_time = None
        end_step_time = None
        for (message_id, message_type, message_time, message_command, message_fullname,
             message_additional_information, message_string) in cursor:
            if int(message_additional_information) == int(start_step):
                start_step_time = message_time
            elif int(message_additional_information) == int(end_step):
                end_step_time = message_time
        if start_step_time is None or end_step_time is None:
            print "step is an over step."
            return

        print start_step_time
        print end_step_time
        print end_step_time - start_step_time