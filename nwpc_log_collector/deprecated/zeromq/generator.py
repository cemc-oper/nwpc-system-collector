import os
import json

import zmq
from sqlalchemy import text

import config
from nwpc_log_collector.sms_log_model import Session, RepoVersion, Repo, Record


def main():
    user_id = 1
    user_name = 'nwp_xp'
    repo_name = 'nwp_cma20n03'
    table_name = 'record_{repo_name}'.format(repo_name=repo_name)
    session = Session()

    print "Querying the log file location...",
    query = session.query(Repo, RepoVersion).filter(Repo.user_id == user_id).filter(Repo.repo_name == repo_name)\
        .filter(Repo.repo_id == RepoVersion.repo_id).filter(Repo.current_version_id == RepoVersion.version_id)
    (repo, repo_version) = query.first()
    sms_log_file_path = repo_version.version_location
    head_line = repo_version.head_line
    print sms_log_file_path

    print "Checking whether the file exists...",
    if not os.path.isfile(sms_log_file_path):
        print "Not Found"
        print "Error!"
        return -2
    print "Found"

    with open(sms_log_file_path, 'r') as log_file:
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
            return -1

        # get the last record line in database.
        print "Fetching the last record in database...",
        query = session.query(Record).filter(Record.repo_id == repo.repo_id)\
            .filter(Record.version_id == repo.current_version_id).order_by(text("line_no DESC")).limit(1)
        last_record = query.first()

        line_no = last_record.line_no

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

        lines.extend([l.strip() for l in new_lines])
        print "Done"
        total_count = len(lines)
        print "Found {line_count} lines to be store in database".format(line_count=total_count)

        print "Now, publish them to the collector..."
        context = zmq.Context()

        agent_socket = context.socket(zmq.REQ)
        agent_socket.connect("tcp://localhost:{agent_socket_no}".format(agent_socket_no=config.AGENT_SOCKET_NO))

        agent_socket_topic = 'smslog'

        for line in lines:
            line_no += 1

            message_body = {
                'type': 'smslog',
                'line_no': line_no,
                'content': line
            }

            agent_socket.send_multipart([agent_socket_topic, json.dumps(message_body)])
            response = agent_socket.recv_json()

        print "Done"

        print "Sending control command...",
        command_message_body = {
            'type': 'control',
            'command': 'commit'
        }
        agent_socket.send_multipart([agent_socket_topic, json.dumps(command_message_body)])
        response = agent_socket.recv_json()
        print "Done"

        print "Goodbye"


if __name__ == '__main__':
    main()
