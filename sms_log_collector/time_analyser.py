import datetime


class TimeAnalyser(object):
    def __init__(self, database_engine):
        self.database_engine = database_engine

    def calculate_node_time(self, node_path, date):

        node_time = dict()

        message_list = self.database_engine.get_message(
            where_string="WHERE message_fullname='{node_path}' "
                         "AND DATE(message_time)='{date}' "
                         "AND message_command in ('submitted', 'active', 'complete', 'aborted') ".format(
                         node_path=node_path, date=date
                         ),
            order_by_string="ORDER BY message_id "
        )

        message_length = len(message_list)
        if message_length < 3:
            print "NOT IMPLEMENTED: not enough items."
            return node_time

        # found submitted
        submitted_pos = 0
        if message_list[submitted_pos].message_command != 'submitted':
            print "NOT IMPLEMENTED: the first item is not submitted."
            return node_time
        node_time['submitted'] = message_list[submitted_pos].message_time

        # found active
        active_pos = submitted_pos + 1
        if message_list[active_pos].message_command != 'active':
            print "NOT IMPLEMENTED: active is not found after submitted."
            return node_time
        node_time['active'] = message_list[active_pos].message_time

        # found complete
        complete_pos = active_pos + 1
        if message_list[complete_pos].message_command != 'complete':
            # find aborted
            if message_list[complete_pos].message_command == 'aborted':
                aborted_pos = complete_pos
                complete_pos = -1
                node_time['aborted'] = message_list[aborted_pos].message_time
            else:
                print "NOT IMPLEMENTED: complete is not found after active."
            return node_time

        node_time['complete'] = message_list[complete_pos].message_time

        return node_time

    def calculate_meter_total_time(self, meter_name, date, start_step, end_step):
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

    def get_meter_step_time_list(self, meter_name, date):
        self.database_engine.create_cursor()
        cursor = self.database_engine.select_message(
            where_string="WHERE message_fullname='{meter_name}' "
                         "AND DATE(message_time)='{date}'".format(
                         meter_name=meter_name, date=date
                         ),
            order_by_string="ORDER BY message_id "
        )
        meter_time_list = dict()
        for (message_id, message_type, message_time, message_command, message_fullname,
             message_additional_information, message_string) in cursor:
            meter_time_list[int(message_additional_information)] = message_time
        return meter_time_list

