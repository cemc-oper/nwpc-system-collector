import os
import sys
from datetime import date, datetime, timedelta
import mysql.connector


def main():
    print datetime.now()

    user_name = 'nwp_qu'
    host_name = 'cma20n03'
    database_name = 'message_{user_name}_{host_name}'.format(user_name=user_name, host_name=host_name)
    log_file_path = "/cma/u/{user_name}/smsworks/sms/{host_name}.sms.log".format(user_name=user_name, host_name=host_name)
    if not os.path.isfile(log_file_path):
        print "log file doesn't exist: {log_file_path}".format(log_file_path=log_file_path)
        sys.exit(2)

    with open(log_file_path, 'r') as log_file:
        connect = mysql.connector.connect(
            user='wangdp',
            password='shenyang',
            host='localhost',
            database='smslog'
        )
        cursor = connect.cursor()
        print "Fetching the first message in database...",
        query = ("SELECT message_id, message_string FROM {database_name} ORDER BY message_id LIMIT 1".format(
            database_name=database_name
        ))
        cursor.execute(query)
        message_id = None
        message_string = None
        for (message_id, message_string) in cursor:
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
            query = ("SELECT COUNT(message_id) FROM {database_name}".format(database_name=database_name))
            cursor.execute(query)
            for (count,) in cursor:
                print count
            print "Fetching the last message in database...",
            query = ("SELECT message_id, message_string FROM {database_name} ORDER BY message_id DESC LIMIT 1".format(
                database_name=database_name
            ))
            cursor.execute(query)
            for (message_id, message_string) in cursor:
                print "Done"
            print "Searching for line No. {count}...".format(count=count),
            for i in range(1, int(count)-1):
                log_file.readline()
            line = log_file.readline()
            print "Found"
            print "line          :", line,
            print "message_string:", message_string,

        append_line_count = 0
        print 'read all lines that are not in database...',
        lines = log_file.readlines()
        total_count = len(lines)
        print 'Done'
        print 'Count of messages to be add into database:', total_count

        print 'Adding lines to database...'
        count = dict()
        message = dict()
        percent = 0
        i = 0
        add_message = ("INSERT INTO {database_name} "
                       "(`message_id`,`message_type`,`message_time`,`message_command`,"
                       "`message_fullname`,`message_additional_information`,`message_string`) "
                       "VALUES (%(message_id)s, %(message_type)s, %(message_time)s, %(message_command)s, "
                       "%(message_fullname)s, %(message_additional_information)s, %(message_string)s) ".format(
            database_name=database_name
        ))

        for line in lines:
            i += 1
            cur_percent = i*100/total_count
            if cur_percent > percent:
                percent = int(cur_percent)
                print "[{percent}%]".format(percent=percent)
                connect.commit()

            start_pos = 2
            end_pos = line.find(':')
            message_type = line[start_pos:end_pos]

            start_pos = end_pos + 2
            end_pos = line.find(']',start_pos)
            message_time_string = line[start_pos:end_pos]
            message_time = datetime.strptime(message_time_string, '%H:%M:%S %d.%m.%Y')

            start_pos = end_pos + 2
            end_pos = line.find(":", start_pos)
            message_command = line[start_pos:end_pos]
            if message_command in count:
                count[message_command] += 1
            else:
                count[message_command] = 1
                message[message_command] = line

            message_fullname = None
            message_additional_information = None

            message_string = line

            message_data = {
                'database_name': database_name,
                'message_id': None,
                'message_type': message_type,
                'message_time': message_time,
                'message_command': message_command,
                'message_fullname': message_fullname,
                'message_additional_information': message_additional_information,
                'message_string': message_string
            }
            try:
                cursor.execute(add_message, message_data)
            except mysql.connector.errors.ProgrammingError:
                print cursor.statement
                raise

        connect.commit()
        cursor.close()
        connect.close()

    print datetime.now()


if __name__ == "__main__":
    main()
