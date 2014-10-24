import os
import sys
from datetime import date, datetime, timedelta
import mysql.connector

from sms_log_collector.message import Message
from sms_log_collector.database_engine import DatabaseEngine


def main():
    print datetime.now()

    user_name = 'nwp_qu'
    host_name = 'cma18n03'
    table_name = 'message_{user_name}_{host_name}'.format(user_name=user_name, host_name=host_name)
    log_file_path = "/cma/u/{user_name}/smsworks/sms/{host_name}.sms.log".format(user_name=user_name,
                                                                                 host_name=host_name)
    engine_config = {
        'user': 'wangdp',
        'password': 'shenyang',
        'host': 'localhost',
        'database': 'smslog',
        'table_name': table_name
    }

    # check file
    if not os.path.isfile(log_file_path):
        print "log file doesn't exist: {log_file_path}".format(log_file_path=log_file_path)
        sys.exit(2)

    with open(log_file_path, 'r') as log_file:
        message_id = None
        message_string = None

        engine = DatabaseEngine()
        engine.create_connect(engine_config)
        cursor = engine.create_cursor()

        print "Fetching the first message in database...",
        message_list = engine.get_message(order_by_string="ORDER BY message_id LIMIT 1")
        if len(message_list) == 1:
            message_id = message_list[0].message_id
            message_string = message_list[0].message_string
            print "Found"

        pos = 0
        if message_id is None:
            print "There is no message in database"
        else:
            print "Matching the first message between database and the log file...",
            line = log_file.readline()
            pos += 1
            if line != message_string:
                print "Failed"
                print "First line has been changed. We haven't implemented this."
                print line,
                print message_string,
                sys.exit()
            print "Matched."

            print "Fetching the count of messages in database...",
            count = engine.get_message_count()
            print count

            print "Fetching the last message in database...",
            message_list = engine.get_message(order_by_string="ORDER BY message_id DESC LIMIT 1")
            if len(message_list) == 1:
                message_id = message_list[0].message_id
                message_string = message_list[0].message_string
                print "Done"

            print "Searching the log file for line No. {count}...".format(count=count),
            for i in range(pos, int(count)-1):
                log_file.readline()
            line = log_file.readline()
            print "Found"
            print "line          :", line,
            print "message_string:", message_string,

        print 'read all lines that are not in database...',
        lines = log_file.readlines()
        total_count = len(lines)
        print 'Done'
        print 'Count of messages to be add into database:', total_count

        print 'Adding lines to database...'
        percent = 0
        i = 0
        for line in lines:
            i += 1
            cur_percent = i*100/total_count
            if cur_percent > percent:
                percent = int(cur_percent)
                print "[{percent}%]".format(percent=percent)
                engine.commit_connect()

            message = Message()
            message.parse(line)
            engine.insert_message(message)

        engine.commit_connect()
        engine.close_cursor()
        engine.close_connect()

    print datetime.now()


if __name__ == "__main__":
    main()
