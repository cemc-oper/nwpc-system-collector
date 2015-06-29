# coding=utf-8
"""
读取sms日志文件，发送到agent server的mysql接口，将日志条目存储到mysql中。
"""
import os
import json
import datetime
import argparse
import logging
import requests


def logout_sms_log(owner, repo):
    print "Logout collector from agent...",
    post_url = 'http://10.28.32.175:5001/agent/repos/{owner}/{repo}/collector/sms/file/manage/logout'.format(
        owner=owner, repo=repo
    )
    post_data = {
        'status': 'complete'
    }
    r = requests.post(post_url, data=post_data)
    print "Done"
    return


def post_sms_log_content_to_mysql(owner, repo, content, version, repo_id=None):
    post_url = 'http://10.28.32.175:5001/agent/repos/{owner}/{repo}/collector/sms/file'.format(
        owner=owner, repo=repo
    )
    post_data = {
        'content': json.dumps(content),
        'version_id': version
    }
    if repo_id is not None:
        post_data['repo_id'] = repo_id

    print "Posting log content to server...",
    r = requests.post(post_url, data=post_data)
    print "Done"
    return


def agent_appender(owner, repo):
    post_max_count = 1000

    info_url = 'http://10.28.32.175:5001/agent/repos/{owner}/{repo}/collector/sms/file/manage/login'.format(
        owner=owner, repo=repo
    )
    print "Getting sms log info from server...",
    info_request = requests.get(info_url)
    print "Done"
    info_response = info_request.json()
    if 'error' in info_response:
        print "There is some error:"
        print info_response['error_type']
        print "ERROR: Collector exist."
        return

    info_data = info_response['data']
    sms_log_file_path = info_data['path']
    head_line = info_data['head_line']
    last_line_no = info_data['last_line_no']
    repo_id = info_data['repo_id']
    version = info_data['version']

    print """Log info for {owner}/{repo}:
    version: {version}
    path: {path}
    head_line: {head_line}
    last_line_no: {last_line_no}
""".format(owner=owner, repo=repo,
           version=version,
           path=sms_log_file_path,
           head_line=head_line,
           last_line_no=last_line_no)

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
        line_no = last_line_no
        print "Cached"

        # read line_no lines from files, line 1 is already read in the beginning.
        print "Searching the log file for the last line in database... ",
        for i in range(2, int(line_no)+1):
            line = log_file.readline()
        print "Done"
        print line.strip()

        # read all lines
        print "Reading all lines that are not in the database...",
        lines = []
        if line_no == 0:
            lines.append(head_line)
        new_lines = log_file.readlines()

        lines.extend([l.strip() for l in new_lines])
        print "Done"
        total_count = len(lines)
        # total_count = 100000
        print "Found {line_count} lines to be store in database".format(line_count=total_count)

        submit_lines = lines[0:total_count]

        print "Appending lines to agent server..."

        content = []
        percent = 0
        i = 0
        cur_line_no = line_no
        for line in submit_lines:
            cur_line_no += 1
            i += 1
            cur_percent = i*100/total_count
            if cur_percent > percent:
                percent = int(cur_percent)
                print "[{percent}%]".format(percent=percent)
            content.append({
                'no': cur_line_no,
                'line': line
            })
            if len(content) >= post_max_count:
                post_sms_log_content_to_mysql(owner, repo, content, version, repo_id)
                content = []
        post_sms_log_content_to_mysql(owner, repo, content, version, repo_id)
        content = []
        print "Posted all lines."

        logout_sms_log(owner, repo)

        print "Goodbye"


if __name__ == "__main__":
    start_time = datetime.datetime.now()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
DESCRIPTION
    Append sms log.""")

    parser.add_argument("-u", "--user", type=int, help="user NAME")
    parser.add_argument("-r", "--repo", help="repo name")

    args = parser.parse_args()

    user_name = 'nwp_xp'
    repo_name = 'nwp_cma20n03'

    if args.user:
        user_name = args.user
        print 'user name: {user_name}'.format(user_name=user_name)
    else:
        print "Use default user: {user_name}".format(user_name=user_name)

    if args.repo:
        repo_name = args.repo
        print 'repo name: {repo_name}'.format(repo_name=repo_name)
    else:
        print "Use default repo name: {repo_name}".format(repo_name=repo_name)

    agent_appender(user_name, repo_name)

    end_time = datetime.datetime.now()
    print end_time - start_time
