import os
import sys
from datetime import date, datetime, timedelta

from nwpc_log_collector.record import Message
from nwpc_log_collector.database_engine import DatabaseEngine


def main():
    print datetime.utcnow()

    database = 'smslog'
    user_name = 'nwp'
    host_name = 'cma20n03'
    table_name = 'message_choice_{user_name}_{host_name}'.format(user_name=user_name, host_name=host_name)
    engine_config = {
        'user': 'windroc',
        'password': 'shenyang',
        'host': 'localhost',
        'database': database,
        'table_name': table_name
    }

    engine = DatabaseEngine()
    engine.create_connect(engine_config)
    cursor = engine.create_cursor()

    update_engine = DatabaseEngine()
    update_engine.create_connect(engine_config)
    update_engine.create_cursor()

    message_count = engine.get_message_count(
        where_string="WHERE message_command in ('submitted','active', 'queued', "
                     "'complete', 'aborted', 'alter', 'meter', 'begin') ")
    if message_count > 0:
        print message_count
    else:
        print 'None'
        sys.exit()
    #message_count = 1000
    print "Currently we test only last {message_count} messages which we selected.".format(message_count=message_count)

    print "Updating messages in database..."
    engine.select_message(
        where_string="WHERE message_command in ('submitted','active', 'queued', "
                     "'complete', 'aborted', 'alter', 'meter', 'begin') ",
        order_by_string="ORDER BY message_id DESC LIMIT {message_count} ".format(message_count=message_count)
    )
    i = 0.0
    percent = 0
    update_count = 0
    for (message_id, message_type, message_time, message_command, message_fullname,
         message_additional_information, message_string) in cursor:
        i += 1
        current_percent = int(i*100/message_count)
        if current_percent > percent:
            percent = current_percent
            print "{percent}%".format(percent=percent)
            update_engine.commit_connect()

        # analysis the message
        message = Message()
        message.message_id = message_id
        message.parse(message_string)
        if message.message_fullname != message_fullname or \
            message.message_type != message_type or \
            message.message_command != message_command or \
            message.message_additional_information != message_additional_information:
            update_engine.update_message(message)
            update_count += 1

    engine.commit_connect()
    engine.close_cursor()
    engine.close_connect()

    update_engine.commit_connect()
    update_engine.close_cursor()
    update_engine.close_connect()
    print "Count of updated messages...",update_count

    print datetime.utcnow()


if __name__ == "__main__":
    main()
