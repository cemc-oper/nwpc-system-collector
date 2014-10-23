import os
import sys
from datetime import date, datetime, timedelta
import mysql.connector


def main():
    print datetime.now()

    log_file_path = "/cma/u/nwp_qu/smsworks/sms/cma18n03.sms.log"
    if not os.path.isfile(log_file_path):
        print "log file doesn't exist: {log_file_path}".format(log_file_path=log_file_path)
        sys.exit(2)

    with open(log_file_path, 'r') as log_file:
        print "Reading log file. This will take some time...",
        lines = log_file.readlines()
        print "Done"
        total_log_message = len(lines)
        print "total : {total_log_message}".format(total_log_message=total_log_message)
        print lines[:3]
        print lines[-3:]

        connect = mysql.connector.connect(
            user='wangdp',
            password='shenyang',
            host='localhost',
            database='smslog'
        )
        cursor = connect.cursor()

        count = dict()
        message = dict()
        percent = 0
        i = 0

        add_message = ("INSERT INTO `smslog`.`message_nwp_qu_cma18n03` "
                       "(`message_id`,`message_type`,`message_time`,`message_command`,"
                       "`message_fullname`,`message_additional_information`,`message_string`) "
                       "VALUES (%(message_id)s, %(message_type)s, %(message_time)s, %(message_command)s, "
                       "%(message_fullname)s, %(message_additional_information)s, %(message_string)s) ")

        for line in lines:
            #print "{i}/{total}".format(i=i, total=total_log_message)
            i += 1
            cur_percent = i*100/total_log_message
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

        for c in count:
            print c, count[c]
        for m in message:
            print m, message[m]

    print datetime.now()


if __name__ == "__main__":
    main()
