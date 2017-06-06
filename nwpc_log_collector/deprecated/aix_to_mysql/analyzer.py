import os
import sys
from datetime import date, datetime, timedelta

from nwpc_log_collector.record import Record
from nwpc_log_collector.database_engine import DatabaseEngine


def main():
    print datetime.utcnow()

    user_id = 1
    user_name = 'nwp_xp'
    repo_name = 'nwp_qu_cma20n03'
    table_name = 'record_{repo_name}'.format(repo_name=repo_name)

    engine_config = {
        'user': 'windroc',
        'password': 'shenyang',
        'host': '10.28.32.175',
        'database': 'smslog',
        'table_name': table_name
    }
    engine = DatabaseEngine()
    engine.create_connect(engine_config)
    cursor = engine.create_cursor()

    update_engine = DatabaseEngine()
    update_engine.create_connect(engine_config)
    update_engine.create_cursor()

    where_string = "WHERE record_command IN ('suspend', 'force(recursively)') "
    query = "SELECT COUNT(record_id) FROM {table_name} {where_string}".format(
        table_name=table_name, where_string=where_string)
    cursor.execute(query)
    record_count = -1
    for (record_count,) in cursor:
        pass
    if record_count > 0:
        print record_count
    else:
        print 'None'
        sys.exit()
    #record_count = 10
    print "Currently we test only last {record_count} messages which we selected.".format(record_count=record_count)

    print "Updating messages in database..."

    i = 0.0
    percent = 0
    update_count = 0

    count_per_connection = 2000
    current_offset = 0
    while current_offset < record_count:
        engine.select_record(
            where_string=where_string,
            order_by_string="ORDER BY record_id DESC LIMIT {offset},{count_per_connection} ".format(
                offset=current_offset, count_per_connection=count_per_connection)
        )
        for (record_id, repo_id, version_id, line_no, record_type, record_date, record_time, record_command,
             record_fullname, record_additional_information, record_string) in cursor:
            i += 1
            current_percent = int(i*100/record_count)
            if current_percent > percent:
                percent = current_percent
                print "{percent}%".format(percent=percent)
            # if i % 1000 == 0:
            #     update_engine.commit_connect()

            # analysis the record
            record = Record()
            record.record_id = record_id
            record.repo_id = repo_id
            record.version_id = version_id
            record.line_no = line_no
            record.parse(record_string)
            if record.record_fullname != record_fullname or \
                    record.record_type != record_type or \
                    record.record_command != record_command or \
                    record.record_additional_information != record_additional_information:

                update_engine.update_record(record)
                update_count += 1

        engine.commit_connect()

        update_engine.commit_connect()

        current_offset += count_per_connection

    print "Count of updated messages...", update_count

    engine.commit_connect()
    engine.close_cursor()
    engine.close_connect()

    update_engine.commit_connect()
    update_engine.close_cursor()
    update_engine.close_connect()

    print datetime.utcnow()


if __name__ == "__main__":
    main()
