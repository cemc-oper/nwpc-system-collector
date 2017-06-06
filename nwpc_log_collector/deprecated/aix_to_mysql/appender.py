import argparse
import os
import sys
from datetime import date, datetime, timedelta

from nwpc_log_collector.record import Record
from nwpc_log_collector.database_engine import DatabaseEngine


def main():
    print datetime.utcnow()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
DESCRIPTION
    Append sms log.""")

    parser.add_argument("-i", "--id", type=int, help="user id")
    parser.add_argument("-r", "--repo", help="repo name")

    args = parser.parse_args()

    user_id = 1
    user_name = 'nwp_xp'
    repo_name = 'nwp_cma20n03'

    if args.id:
        user_id = args.id
        print 'user id: {user_id}'.format(user_id=user_id)
    else:
        print "Use default user id: {user_id}".format(user_id=user_id)

    if args.repo:
        repo_name = args.repo
        print 'repo name: {repo_name}'.format(repo_name=repo_name)
    else:
        print "Use default repo name: {repo_name}".format(repo_name=repo_name)

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

    # get repo and repo_version information according to user_id and repo_name
    query = "SELECT repo.repo_id, repo.repo_location, repo.current_version_id, " \
            "repo_version.version_name, repo_version.version_location, repo_version.head_line " \
            "FROM repo, repo_version " \
            "WHERE user_id={user_id} AND repo_name='{repo_name}' " \
            "AND repo.repo_id = repo_version.repo_id "\
            "AND repo.current_version_id = repo_version.version_id;".format(
            user_id=user_id, repo_name=repo_name
            )
    cursor.execute(query)
    for (repo_id, repo_location, current_version_id, version_name, version_location, head_line) in cursor:
        pass

    print ""
    log_file_path = version_location

    # check file
    if not os.path.isfile(log_file_path):
        print "log file doesn't exist: {log_file_path}".format(log_file_path=log_file_path)
        sys.exit(2)

    with open(log_file_path, 'r') as log_file:
        # check the repo version by reading the first line.
        print "Matching the head line...",
        pos = 0
        line = log_file.readline().strip()
        pos += 1
        if line == head_line:
            print "Matched"
        else:
            print "Not Matched"
            print "file line:", line
            print "head line:", head_line
            print "We need a new version for repo which is not implemented."
            sys.exit(-1)

        # get the last record line in database.
        print "Fetching the last record in database...",
        query = "SELECT record_id, line_no, record_type, record_date, record_time, record_command, " \
                "record_fullname, record_additional_information, record_string " \
                "FROM {table_name} " \
                "WHERE repo_id={repo_id} AND version_id={version_id} " \
                "ORDER BY line_no DESC LIMIT 1 ".format(
                    table_name=table_name, repo_id=repo_id, version_id=current_version_id)
        cursor.execute(query)
        record_id = -1
        line_no = 0
        for (record_id, line_no, record_type, record_date, record_time, record_command,
             record_fullname, record_additional_information, record_string) in cursor:
            pass
        if line_no != 0:
            print "Found"
            print "last line number:", line_no
        else:
            print "Not Found"
            print "There is no records in the database."

        # read line_no lines from files, line 1 is already read in the beginning.
        print "Searching the log file for the last line in database... ",
        for i in range(2, int(line_no)+1):
            line = log_file.readline()
        print "Done"
        print line

        # read all lines
        print "Reading all lines that are not in the database...",
        lines = []
        if line_no == 0:
            lines.append(head_line)
        new_lines = log_file.readlines()
        # new_lines=[]
        # for i in range(0,100):
        #     new_lines.append(log_file.readline())

        lines.extend([l.strip() for l in new_lines])
        print "Done"
        total_count = len(lines)
        print "Found {line_count} lines to be store in database".format(line_count=total_count)

        print 'Adding lines to database...'
        percent = 0
        i = 0
        cur_line_no = line_no
        for line in lines:
            cur_line_no += 1
            i += 1
            cur_percent = i*100/total_count
            if cur_percent > percent:
                percent = int(cur_percent)
                print "[{percent}%]".format(percent=percent)
                engine.commit_connect()

            record = Record()
            record.repo_id = repo_id
            record.version_id = current_version_id
            record.line_no = cur_line_no
            record.parse(line)

            engine.insert_record(record)

    engine.commit_connect()
    engine.close_cursor()
    engine.close_connect()

    print datetime.utcnow()

    return


if __name__ == "__main__":
    start_time = datetime.utcnow()
    main()
    end_time = datetime.utcnow()
    print end_time - start_time
