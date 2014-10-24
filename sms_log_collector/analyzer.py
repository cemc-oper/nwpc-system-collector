import os
import sys
from datetime import date, datetime, timedelta
import mysql.connector

from sms_log_collector.message import Message


def main():
    print datetime.now()

    user_name = 'nwp_qu'
    host_name = 'cma18n03'
    database_name = 'message_{user_name}_{host_name}'.format(user_name=user_name, host_name=host_name)

    connect = mysql.connector.connect(
        user='wangdp',
        password='shenyang',
        host='localhost',
        database='smslog'
    )

    update_connect = mysql.connector.connect(
        user='wangdp',
        password='shenyang',
        host='localhost',
        database='smslog'
    )
    cursor = connect.cursor()
    update_cursor = update_connect.cursor()
    # print "Fetching total count of messages in database...",
    # query = ("SELECT COUNT(message_id) FROM {database_name} "
    #          "WHERE message_command in ('submitted','active', 'queued', 'complete', 'aborted') ".format(
    #     database_name=database_name
    # ))
    # cursor.execute(query)
    # message_count = 0
    # for (count,) in cursor:
    #     message_count = count
    # if message_count > 0:
    #     print message_count
    # else:
    #     print 'None'
    #     sys.exit()
    message_count = 1000
    print "Currently we test only last {message_count} messages which we selected.".format(message_count=message_count)

    print "Updating messages in database..."
    query = ("SELECT message_id, message_type, message_time, message_command, message_fullname, "
             "message_additional_information, message_string FROM {database_name} "
             "WHERE message_command in ('submitted','active', 'queued', 'complete', 'aborted') "
             "ORDER BY message_id DESC "
             "LIMIT {message_count}".format(database_name=database_name, message_count=message_count))
    cursor.execute(query)
    message_id = None
    message_string = None
    i = 0.0
    percent = 0
    for (message_id, message_type, message_time, message_command, message_fullname,
         message_additional_information, message_string) in cursor:
        i += 1
        current_percent = int(i*100/message_count)
        if current_percent > percent:
            percent = current_percent
            print "{percent}%".format(percent=percent)
            update_connect.commit()

        #########################
        # analysis the message
        #########################
        changed_flag = False
        message = Message()
        message.parse(message_string)

        update_query = "UPDATE {database_name} SET message_fullname = %(message_fullname)s " \
                       "WHERE message_id = %(message_id)s".format(
                       database_name=database_name)
        update_cursor.execute(update_query, {'message_fullname': message.message_fullname,
                                             'message_id': message.message_id})

    connect.commit()
    cursor.close()
    connect.close()

    update_connect.commit()
    update_cursor.close()
    update_connect.close()

    print datetime.now()


if __name__ == "__main__":
    main()
