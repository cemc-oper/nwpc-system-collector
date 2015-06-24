# coding=utf-8
"""
读取sms日志文件，发送到agent server，agent server将其发送给kafka消息队列。
"""
import os
import json
import datetime
import argparse
import requests


NWPC_LOG_AGENT_HOST = "10.28.32.175"
NWPC_LOG_AGENT_PORT = "5001"


def get_sms_log_collector_info(owner, repo):
    """
    获取 sms log 的信息，并注册一个新的 collector。相当于开始日期收集。
    :param owner:
    :param repo:
    :return:
    """
    info_url = 'http://{log_agent_host}:{log_agent_port}/agent/repos/{owner}/{repo}/collector/sms/file/info'.format(
        log_agent_host=NWPC_LOG_AGENT_HOST,
        log_agent_port=NWPC_LOG_AGENT_PORT,
        owner=owner, repo=repo
    )
    info_request = requests.get(info_url)
    info_response = info_request.json()
    return info_response


def logout_sms_log_collector(owner, repo):
    """
    注销当前 collector。相当于结束日志收集。
    :param owner:
    :param repo:
    :return:
    """
    post_collector_log(owner, repo, "Logout collector from agent...")
    post_url = 'http://{log_agent_host}:{log_agent_port}/agent/repos/{owner}/{repo}/collector/sms/file/manage/logout'.format(
        log_agent_host=NWPC_LOG_AGENT_HOST,
        log_agent_port=NWPC_LOG_AGENT_PORT,
        owner=owner, repo=repo
    )
    post_data = {
        'status': 'complete'
    }
    r = requests.post(post_url, data=post_data)
    post_collector_log(owner, repo, "Logout collector from agent...Done")
    return


def post_collector_log(owner, repo, message):
    # show message in console, so as in a celery task's console output.
    print message

    post_url = 'http://{log_agent_host}:{log_agent_port}/agent/repos/{owner}/{repo}/collector/log'.format(
        log_agent_host=NWPC_LOG_AGENT_HOST,
        log_agent_port=NWPC_LOG_AGENT_PORT,
        owner=owner, repo=repo
    )
    post_data = {
        'content': message
    }
    r = requests.post(post_url, data=post_data)
    return


def post_sms_log_content(owner, repo, content, version, repo_id=None):
    """
    上传 sms log 日志条目
    :param owner:
    :param repo:
    :param content:
    :param version:
    :param repo_id:
    :return:
    """
    post_url = 'http://{log_agent_host}:{log_agent_port}/agent/repos/{owner}/{repo}/collector/sms/file/kafka'.format(
        log_agent_host=NWPC_LOG_AGENT_HOST,
        log_agent_port=NWPC_LOG_AGENT_PORT,
        owner=owner, repo=repo
    )
    post_data = {
        'content': json.dumps(content),
        'version_id': version
    }
    if repo_id is not None:
        post_data['repo_id'] = repo_id

    post_collector_log(owner, repo, "Posting log content to server...")
    r = requests.post(post_url, data=post_data)
    post_collector_log(owner, repo, "Posting log content to server...Done")
    return


def agent_appender(owner, repo, limit_count=-1):
    post_max_count = 1000

    # TODO: check whether web site is available.
    post_collector_log(owner, repo, "Getting sms log info from server...")
    info_response = get_sms_log_collector_info(owner, repo)
    post_collector_log(owner, repo, "Getting sms log info from server...Done")
    if 'error' in info_response:
        post_collector_log(owner, repo, "There is some error:")
        post_collector_log(owner, repo, info_response['error_type'])
        post_collector_log(owner, repo, "ERROR: Collector exist.")
        return

    info_data = info_response['data']
    sms_log_file_path = info_data['path']
    head_line = info_data['head_line']
    last_line_no = info_data['last_line_no']
    repo_id = info_data['repo_id']
    version = info_data['version']

    post_collector_log(owner, repo, """Log info for {owner}/{repo}:
    version: {version}
    path: {path}
    head_line: {head_line}
    last_line_no: {last_line_no}
""".format(owner=owner, repo=repo,
           version=version,
           path=sms_log_file_path,
           head_line=head_line,
           last_line_no=last_line_no))

    post_collector_log(owner, repo, "Checking whether the file exists...")
    if not os.path.isfile(sms_log_file_path):
        post_collector_log(owner, repo, "Checking whether the file exists...Not Found")
        post_collector_log(owner, repo, "Error!")
        return -2
    post_collector_log(owner, repo, "Checking whether the file exists...Found")

    with open(sms_log_file_path, 'r') as log_file:
        # check the repo version by reading the first line.
        post_collector_log(owner, repo, "Matching the head line...")
        pos = 0
        line = log_file.readline().strip()
        pos += 1
        if line == head_line:
            post_collector_log(owner, repo, "Matching the head line...Matched")
        else:
            post_collector_log(owner, repo, "Matching the head line...Not Matched")
            post_collector_log(owner, repo, "file line: "+line)
            post_collector_log(owner, repo, "head line:"+head_line)
            post_collector_log(owner, repo, "We need a new version for repo which is not implemented.")
            return -1

        # get the last record line in database.
        post_collector_log(owner, repo, "Fetching the last record in database...")
        line_no = last_line_no
        post_collector_log(owner, repo, "Fetching the last record in database...Cached")

        # read line_no lines from files, line 1 is already read in the beginning.
        post_collector_log(owner, repo, "Searching the log file for the last line in database...")
        for i in range(2, int(line_no)+1):
            line = log_file.readline()
        post_collector_log(owner, repo, "Searching the log file for the last line in database...Done")
        post_collector_log(owner, repo, line.strip())

        # read all lines
        post_collector_log(owner, repo, "Reading all lines that are not in the database...")
        lines = []
        if line_no == 0:
            lines.append(head_line)
        new_lines = log_file.readlines()

        lines.extend([l.strip() for l in new_lines])
        post_collector_log(owner, repo, "Reading all lines that are not in the database...Done")
        total_count = len(lines)
        post_collector_log(owner, repo, "Found {line_count} lines to be store in database".format(line_count=total_count))
        if limit_count != -1:
            if total_count > limit_count:
                total_count = limit_count
                post_collector_log(owner, repo, "But user has limited to {line_count}".format(line_count=total_count))

        submit_lines = lines[0:total_count]

        post_collector_log(owner, repo, "Appending lines to agent server...")

        content = []
        percent = 0
        i = 0
        post_start_time = datetime.datetime.now()
        cur_line_no = line_no
        for line in submit_lines:
            cur_line_no += 1
            i += 1
            cur_percent = i*100/total_count
            if cur_percent > percent:
                percent = int(cur_percent)
                post_current_time = datetime.datetime.now()
                post_current_time_delta = post_current_time - post_start_time
                post_current_seconds = post_current_time_delta.days * 86400 + post_current_time_delta.seconds
                total_seconds = int(post_current_seconds / (percent/100.0))
                left_time_delta = datetime.timedelta(seconds= total_seconds - post_current_seconds)
                post_collector_log(owner, repo, "[{percent}%] left time: {left_time}".format(percent=percent,
                                                                                             left_time=left_time_delta))

            content.append({
                'no': cur_line_no,
                'line': line
            })
            if len(content) >= post_max_count:
                post_sms_log_content(owner, repo, content, version, repo_id)
                content = []
                post_current_time = datetime.datetime.now()
                post_current_time_delta = post_current_time - post_start_time
                post_current_seconds = post_current_time_delta.days * 86400 + post_current_time_delta.seconds
                total_seconds = int(post_current_seconds / (i*0.1/total_count))
                left_time_delta = datetime.timedelta(seconds= total_seconds - post_current_seconds)
                post_collector_log(owner, repo, "left time: {left_time}".format(left_time=left_time_delta))

        post_sms_log_content(owner, repo, content, version, repo_id)
        content = []
        post_collector_log(owner, repo, "Posted all lines.")

        logout_sms_log_collector(owner, repo)

        post_collector_log(owner, repo, "Goodbye")


if __name__ == "__main__":
    start_time = datetime.datetime.now()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
DESCRIPTION
    Append sms log to a web agent.""")

    parser.add_argument("-u", "--user", help="user NAME")
    parser.add_argument("-r", "--repo", help="repo name")
    parser.add_argument("-l", "--limit", type=int, help="limit count")

    args = parser.parse_args()

    user_name = 'nwp_xp'
    repo_name = 'nwp_qu_cma20n03'
    limit_count_number = -1

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

    if args.limit:
        limit_count_number = args.limit
        print "The number of appended records is limited to {limit_count}".format(limit_count=limit_count_number)

    agent_appender(owner=user_name, repo=repo_name, limit_count=limit_count_number)

    end_time = datetime.datetime.now()
    print end_time - start_time
