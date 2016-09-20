#!/usr/bin/env python
# coding=utf-8
"""
读取 sms 日志文件，发送到 agent server，agent server 将其发送给 kafka 消息队列或者直接保存到 MySQL 数据库。
"""
import os
import sys
import json
import datetime
import argparse
import requests
import logging


config_file_name = "smslog_collector.config"

NWPC_LOG_AGENT_HOST = "10.28.32.175"
NWPC_LOG_AGENT_PORT = "6501"

POST_MAX_COUNT = 1000   # 批量日志发送条目阈值


def get_config(config_file_path):
    """
    读取配置文件信息，配置文件为 json 格式
    :param config_file_path:
    :return:
    """
    global NWPC_LOG_AGENT_HOST, NWPC_LOG_AGENT_PORT, POST_MAX_COUNT
    f = open(config_file_path, 'r')
    config = json.load(f)
    f.close()

    NWPC_LOG_AGENT_HOST = config['nwpc_log_agent_host']
    NWPC_LOG_AGENT_PORT = config['nwpc_log_agent_port']
    POST_MAX_COUNT = config['post_max_count']

    return config


def get_logger():
    """
    初始化日志格式
    :return:
    """
    script_logger = logging.getLogger(__name__)
    script_logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)

    script_logger.addHandler(ch)
    return script_logger

logger = get_logger()


def get_sms_log_collector_info(owner, repo):
    """
    获取 sms log 的信息
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


def login_sms_log_collector(owner, repo):
    """
    获取 sms log 的信息，并注册一个新的 collector。相当于开始日期收集。
    :param owner:
    :param repo:
    :return:
    """
    info_url = 'http://{log_agent_host}:{log_agent_port}/agent/repos/{owner}/{repo}/collector/sms/file/manage/login'.format(
        log_agent_host=NWPC_LOG_AGENT_HOST,
        log_agent_port=NWPC_LOG_AGENT_PORT,
        owner=owner, repo=repo
    )
    info_request = requests.get(info_url)
    info_response = info_request.json()
    return info_response


def logout_sms_log_collector(owner, repo, status='complete'):
    """
    注销当前 collector。相当于结束日志收集。
    :param owner:
    :param repo:
    :param status: complete 表示正常退出，其它值表示异常结束
    :return:
    """
    post_collector_log(owner, repo, "Logout collector from agent...")
    post_url = 'http://{log_agent_host}:{log_agent_port}/agent/repos/{owner}/{repo}/collector/sms/file/manage/logout'.format(
        log_agent_host=NWPC_LOG_AGENT_HOST,
        log_agent_port=NWPC_LOG_AGENT_PORT,
        owner=owner, repo=repo
    )
    post_data = {
        'status': status
    }
    r = requests.post(post_url, data=post_data)
    post_collector_log(owner, repo, "Logout collector from agent...Done")
    return


# 发送日志

def post_collector_log(owner, repo, message, message_type=None):
    # show message in console, so as in a celery task's console output.
    logger.info(message)

    if message_type == 'error':
        post_url = 'http://{log_agent_host}:{log_agent_port}/agent/repos/{owner}/{repo}/collector/log/error'.format(
            log_agent_host=NWPC_LOG_AGENT_HOST,
            log_agent_port=NWPC_LOG_AGENT_PORT,
            owner=owner, repo=repo
        )
    else:
        post_url = 'http://{log_agent_host}:{log_agent_port}/agent/repos/{owner}/{repo}/collector/log'.format(
            log_agent_host=NWPC_LOG_AGENT_HOST,
            log_agent_port=NWPC_LOG_AGENT_PORT,
            owner=owner, repo=repo
        )
    post_data = {
        'content': message
    }

    r = requests.post(post_url, data=post_data)
    if r.status_code != 200:
        sys.exit()
    return


def post_collector_error_log(owner, repo, message):
    return post_collector_log(owner, repo, message, message_type='error')


def post_sms_log_content_to_mysql(owner, repo, content, version, repo_id=None):
    """
    将 sms 日志内容发送到 agent 的 mysql 接口
    :param owner:
    :param repo:
    :param content:
    :param version:
    :param repo_id:
    :return:
    """
    post_url = 'http://{log_agent_host}:{log_agent_port}/agent/repos/{owner}/{repo}/collector/sms/file'.format(
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

    post_collector_log(owner, repo, "Posting log content to agent/mysql...")
    r = requests.post(post_url, data=post_data)
    if r.status_code != 200:
        sys.exit()
    post_collector_log(owner, repo, "Posting log content to agent/mysql...Done")
    return


def post_sms_log_content_to_kafka(owner, repo, content, version, repo_id=None):
    """
    将 sms 日志发送到 agent 的 kafka 接口
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

    post_collector_log(owner, repo, "{owner}/{repo} Posting log content to agent/kafka...".format(
        owner=owner,repo=repo
    ))
    r = requests.post(post_url, data=post_data)
    if r.status_code != 200:
        sys.exit()
    post_collector_log(owner, repo, "{owner}/{repo} Posting log content to agent/kafka...Done".format(
        owner=owner,repo=repo
    ))
    return


def agent_appender(owner, repo, limit_count=-1, upload_type='kafka'):
    """
    收集日志的主程序
    :param owner:
    :param repo:
    :param limit_count:
    :param upload_type:
    :return:
    """

    # 检查参数
    if upload_type == 'mysql':
        post_sms_log_function = post_sms_log_content_to_mysql
    elif upload_type == 'kafka':
        post_sms_log_function = post_sms_log_content_to_kafka
    else:
        post_collector_log(owner, repo, "Please select a valid upload type, such as mysql and kafka.")
        post_collector_error_log(owner, repo, "Upload type is not supported.")
        logout_sms_log_collector(owner, repo, status='error')
        return -3

    # 常数设置
    post_max_count = POST_MAX_COUNT
    post_collector_log(owner, repo, "post_max_count={post_max_count}".format(post_max_count=post_max_count))

    # TODO: check whether web site is available.
    post_collector_log(owner, repo, "Getting sms log info from server...")
    info_response = login_sms_log_collector(owner, repo)
    post_collector_log(owner, repo, "Getting sms log info from server...Done")
    if 'error' in info_response:
        post_collector_log(owner, repo, "There is some error:")
        post_collector_log(owner, repo, info_response['error_type'])
        post_collector_log(owner, repo, "ERROR: Collector exist.")
        post_collector_error_log(owner, repo, "Collector exist.")
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
        post_collector_error_log(owner, repo, "Log file doesn't exist.")
        logout_sms_log_collector(owner, repo, status='error')
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
            post_collector_error_log(owner, repo, "Head line doesn't match.")
            logout_sms_log_collector(owner, repo, status='error')
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
                post_sms_log_function(owner, repo, content, version, repo_id)
                content = []
                post_current_time = datetime.datetime.now()
                post_current_time_delta = post_current_time - post_start_time
                post_current_seconds = post_current_time_delta.days * 86400 + post_current_time_delta.seconds
                total_seconds = int(post_current_seconds / (i*0.1/total_count))
                left_time_delta = datetime.timedelta(seconds= total_seconds - post_current_seconds)
                post_collector_log(owner, repo, "[{percent}%] left time: {left_time}".format(percent=percent,
                                                                                             left_time=left_time_delta))

        # 上传日志内容
        post_sms_log_function(owner, repo, content, version, repo_id)

        content = []
        post_collector_log(owner, repo, "Posted all lines.")

        logout_sms_log_collector(owner, repo, status='complete')

        post_collector_log(owner, repo, "Goodbye")


def collect_handler(args):
    """
    处理 collect 命令，收集日志
    :param args:
    :return:
    """
    user_name = 'nwp_xp'
    repo_name = 'nwp_qu_cma20n03'
    limit_count_number = -1
    upload_type = 'kafka'
    if args.user:
        user_name = args.user
        print 'User name: {user_name}'.format(user_name=user_name)
    if args.repo:
        repo_name = args.repo
        print 'Repo name: {repo_name}'.format(repo_name=repo_name)
    if args.limit:
        limit_count_number = args.limit
        print "The number of appended records is limited to {limit_count}".format(limit_count=limit_count_number)
    if args.upload_type:
        upload_type = args.upload_type
    print "Upload type: {upload_type}".format(upload_type=upload_type)
    agent_appender(owner=user_name, repo=repo_name, limit_count=limit_count_number, upload_type=upload_type)


def show_handler(args):
    """
    处理 show 命令，显示项目信息
    :param args:
    :return:
    """
    owner = args.user
    print 'User name: {user_name}'.format(user_name=owner)
    repo = args.repo
    print 'Repo name: {repo_name}'.format(repo_name=repo)

    info_response = get_sms_log_collector_info(owner, repo)
    if 'error' in info_response:
        post_collector_log(owner, repo, "There is some error:")
        post_collector_log(owner, repo, info_response['error_type'])
        post_collector_log(owner, repo, "ERROR: Collector exist.")
        post_collector_error_log(owner, repo, "Collector exist.")
        return

    info_data = info_response['data']
    sms_log_file_path = info_data['path']
    head_line = info_data['head_line']
    last_line_no = info_data['last_line_no']
    repo_id = info_data['repo_id']
    version = info_data['version']

    post_collector_log(owner, repo, """SMS log repo info for {owner}/{repo}:
    version: {version}
    path: {path}
    head_line: {head_line}
    last_line_no: {last_line_no}""".format(owner=owner, repo=repo,
           version=version,
           path=sms_log_file_path,
           head_line=head_line,
           last_line_no=last_line_no))
    return


def nwpc_log_collector_tool():
    """
    命令行主程序，解析命令行参数
    :return:
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
DESCRIPTION
    Collect sms log to a web agent.""")

    parser.add_argument("-c", "--config", help="config file path. default config file is smslog_collector.config.")

    sub_parsers = parser.add_subparsers(title="sub commands", dest="sub_command")

    collect_parser = sub_parsers.add_parser('collect',description="collect sms log from sms log file.")
    collect_parser.add_argument("-u", "--user", help="user NAME", required=True)
    collect_parser.add_argument("-r", "--repo", help="repo name", required=True)
    collect_parser.add_argument("-l", "--limit", type=int, help="limit count")
    collect_parser.add_argument("-t", "--upload_type", help="upload type: mysql/kafka")

    show_parser = sub_parsers.add_parser('show', description="show sms log information.")
    show_parser.add_argument("-u", "--user", help="user NAME", required=True)
    show_parser.add_argument("-r", "--repo", help="repo name", required=True)

    args = parser.parse_args()

    # BUG: There is a bug for os.path.dirname on the python compiled by me on AIX.
    # config_file_path = os.path.dirname(__file__) + "/" + config_file_name
    config_file_path = "./conf/" + config_file_name

    if args.config:
        config_file_path = args.config
    get_config(config_file_path)

    if args.sub_command == "collect":
        collect_handler(args)
    elif args.sub_command == "show":
        show_handler(args)


if __name__ == "__main__":
    start_time = datetime.datetime.now()

    nwpc_log_collector_tool()

    end_time = datetime.datetime.now()
    print end_time - start_time
