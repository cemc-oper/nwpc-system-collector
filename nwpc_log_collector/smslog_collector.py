#!/usr/bin/env python3
# coding=utf-8
"""
读取 sms 日志文件，发送到 agent server，agent server 将其发送给 kafka 消息队列或者直接保存到 MySQL 数据库。
"""
import datetime
import json
import logging
import os
import sys

import click
import requests
import yaml

DEFAULT_CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "smslog_collector.config.yaml")


class SmsLogCollector(object):
    def __init__(self):
        self.config = None
        self.agent_config = None
        self.logger = SmsLogCollector.get_logger()

    def load_config(self, config_file_path):
        f = open(config_file_path, 'r')
        config= yaml.load(f)
        f.close()
        self.config = config['smslog_collector']
        self.agent_config = self.config['agent']

    @staticmethod
    def get_logger():
        script_logger = logging.getLogger(__name__)
        script_logger.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)

        script_logger.addHandler(ch)
        return script_logger

    def get_sms_log_collector_info(self, owner, repo):
        """
        获取 sms log 的信息
        :param owner:
        :param repo:
        :return:
        """
        info_url = self.config['sms']['info']['url'].format(
            host=self.agent_config['host'],
            port=self.agent_config['port'],
            owner=owner, repo=repo
        )
        info_request = requests.get(info_url)
        info_response = info_request.json()
        return info_response

    def login_sms_log_collector(self, owner, repo):
        """
        获取 sms log 的信息，并注册一个新的 collector。相当于开始日期收集。
        :param owner:
        :param repo:
        :return:
        """
        login_url = self.agent_config['sms']['login']['url'].format(
            host=self.agent_config['host'],
            port=self.agent_config['port'],
            owner=owner, repo=repo
        )
        login_request = requests.get(login_url)
        login_request = login_request.json()
        return login_request

    def logout_sms_log_collector(self, owner, repo, status='complete'):
        """
        注销当前 collector。相当于结束日志收集。
        :param owner:
        :param repo:
        :param status: complete 表示正常退出，其它值表示异常结束
        :return:
        """
        self.post_collector_log(owner, repo, "Logout collector from agent...")
        post_url = self.agent_config['sms']['logout']['url'].format(
            host=self.agent_config['host'],
            port=self.agent_config['port'],
            owner=owner, repo=repo
        )
        post_data = {
            'status': status
        }
        r = requests.post(post_url, data=post_data)
        self.post_collector_log(owner, repo, "Logout collector from agent...Done")
        return

    # 发送日志
    def post_collector_log(self, owner, repo, message, message_type=None):
        # show message in console, so as in a celery task's console output.
        self.logger.info(message)

        if message_type == 'error':
            post_url = self.agent_config['log']['post']['error_url'].format(
                host=self.agent_config['host'],
                port=self.agent_config['port'],
                owner=owner, repo=repo
            )
        else:
            post_url = self.agent_config['log']['post']['url'].format(
                host=self.agent_config['host'],
                port=self.agent_config['port'],
                owner=owner, repo=repo
            )
        post_data = {
            'content': message
        }

        r = requests.post(post_url, data=post_data)
        if r.status_code != 200:
            sys.exit()
        return

    def post_collector_error_log(self, owner, repo, message):
        return self.post_collector_log(owner, repo, message, message_type='error')

    def post_sms_log_content_to_mysql(self, owner, repo, content, version, repo_id=None):
        """
        将 sms 日志内容发送到 agent 的 mysql 接口
        :param owner:
        :param repo:
        :param content:
        :param version:
        :param repo_id:
        :return:
        """
        post_url = self.agent_config['sms']['post']['target']['mysql'].format(
            host=self.agent_config['host'],
            port=self.agent_config['port'],
            owner=owner, repo=repo
        )
        post_data = {
            'content': json.dumps(content),
            'version_id': version
        }
        if repo_id is not None:
            post_data['repo_id'] = repo_id

        self.post_collector_log(owner, repo, "Posting log content to agent/mysql...")
        r = requests.post(post_url, data=post_data)
        if r.status_code != 200:
            sys.exit()
        self.post_collector_log(owner, repo, "Posting log content to agent/mysql...Done")
        return

    def post_sms_log_content_to_kafka(self, owner, repo, content, version, repo_id=None):
        """
        将 sms 日志发送到 agent 的 kafka 接口
        :param owner:
        :param repo:
        :param content:
        :param version:
        :param repo_id:
        :return:
        """
        post_url = self.agent_config['sms']['post']['target']['kafka'].format(
            host=self.agent_config['host'],
            port=self.agent_config['port'],
            owner=owner, repo=repo
        )
        post_data = {
            'content': json.dumps(content),
            'version_id': version
        }
        if repo_id is not None:
            post_data['repo_id'] = repo_id

        self.post_collector_log(owner, repo, "{owner}/{repo} Posting log content to agent/kafka...".format(
            owner=owner,repo=repo
        ))
        r = requests.post(post_url, data=post_data)
        if r.status_code != 200:
            sys.exit()
        self.post_collector_log(owner, repo, "{owner}/{repo} Posting log content to agent/kafka...Done".format(
            owner=owner,repo=repo
        ))
        return


def agent_appender(config_file_path, owner, repo, limit_count=-1, upload_type='kafka'):
    """
    收集日志的主程序
    :param config_file_path:
    :param owner:
    :param repo:
    :param limit_count:
    :param upload_type:
    :return:
    """

    collector = SmsLogCollector()
    collector.load_config(config_file_path)

    # 检查参数
    if upload_type == 'mysql':
        post_sms_log_function = collector.post_sms_log_content_to_mysql
    elif upload_type == 'kafka':
        post_sms_log_function = collector.post_sms_log_content_to_kafka
    else:
        collector.post_collector_log(owner, repo, "Please select a valid upload type, such as mysql and kafka.")
        collector.post_collector_error_log(owner, repo, "Upload type is not supported.")
        collector.logout_sms_log_collector(owner, repo, status='error')
        return -3

    # 常数设置
    post_max_count = collector.agent_config['sms']['post']['max_count']
    collector.post_collector_log(owner, repo, "post_max_count={post_max_count}".format(post_max_count=post_max_count))

    # TODO: check whether web site is available.
    collector.post_collector_log(owner, repo, "Getting sms log info from server...")
    info_response = collector.login_sms_log_collector(owner, repo)
    collector.post_collector_log(owner, repo, "Getting sms log info from server...Done")
    if 'error' in info_response:
        collector.post_collector_log(owner, repo, "There is some error:")
        collector.post_collector_log(owner, repo, info_response['error_type'])
        collector.post_collector_log(owner, repo, "ERROR: Collector exist.")
        collector.post_collector_error_log(owner, repo, "Collector exist.")
        return

    info_data = info_response['data']
    sms_log_file_path = info_data['path']
    head_line = info_data['head_line']
    last_line_no = info_data['last_line_no']
    repo_id = info_data['repo_id']
    version = info_data['version']

    collector.post_collector_log(owner, repo, """Log info for {owner}/{repo}:
    version: {version}
    path: {path}
    head_line: {head_line}
    last_line_no: {last_line_no}
""".format(owner=owner, repo=repo,
           version=version,
           path=sms_log_file_path,
           head_line=head_line,
           last_line_no=last_line_no))

    collector.post_collector_log(owner, repo, "Checking whether the file exists...")
    if not os.path.isfile(sms_log_file_path):
        collector.post_collector_log(owner, repo, "Checking whether the file exists...Not Found")
        collector.post_collector_log(owner, repo, "Error!")
        collector.post_collector_error_log(owner, repo, "Log file doesn't exist.")
        collector.logout_sms_log_collector(owner, repo, status='error')
        return -2
    collector. post_collector_log(owner, repo, "Checking whether the file exists...Found")

    with open(sms_log_file_path, 'r') as log_file:
        # check the repo version by reading the first line.
        collector.post_collector_log(owner, repo, "Matching the head line...")
        pos = 0
        line = log_file.readline().strip()
        pos += 1
        if line == head_line:
            collector.post_collector_log(owner, repo, "Matching the head line...Matched")
        else:
            collector.post_collector_log(owner, repo, "Matching the head line...Not Matched")
            collector.post_collector_log(owner, repo, "file line: "+line)
            collector.post_collector_log(owner, repo, "head line:"+head_line)
            collector.post_collector_log(owner, repo, "We need a new version for repo which is not implemented.")
            collector.post_collector_error_log(owner, repo, "Head line doesn't match.")
            collector.logout_sms_log_collector(owner, repo, status='error')
            return -1

        # get the last record line in database.
        collector.post_collector_log(owner, repo, "Fetching the last record in database...")
        line_no = last_line_no
        collector.post_collector_log(owner, repo, "Fetching the last record in database...Cached")

        # read line_no lines from files, line 1 is already read in the beginning.
        collector.post_collector_log(owner, repo, "Searching the log file for the last line in database...")
        for i in range(2, int(line_no)+1):
            line = log_file.readline()
        collector.post_collector_log(owner, repo, "Searching the log file for the last line in database...Done")
        collector.post_collector_log(owner, repo, line.strip())

        # read all lines
        collector.post_collector_log(owner, repo, "Reading all lines that are not in the database...")
        lines = []
        if line_no == 0:
            lines.append(head_line)
        new_lines = log_file.readlines()

        lines.extend([l.strip() for l in new_lines])
        collector.post_collector_log(owner, repo, "Reading all lines that are not in the database...Done")
        total_count = len(lines)
        collector.post_collector_log(owner, repo, "Found {line_count} lines to be store in database".format(line_count=total_count))
        if limit_count != -1:
            if total_count > limit_count:
                total_count = limit_count
                collector.post_collector_log(owner, repo, "But user has limited to {line_count}".format(line_count=total_count))

        submit_lines = lines[0:total_count]

        collector.post_collector_log(owner, repo, "Appending lines to agent server...")

        content = []
        percent = 0
        i = 0
        post_start_time = datetime.datetime.utcnow()
        cur_line_no = line_no
        for line in submit_lines:
            cur_line_no += 1
            i += 1
            cur_percent = i*100/total_count
            if cur_percent > percent:
                percent = int(cur_percent)
                post_current_time = datetime.datetime.utcnow()
                post_current_time_delta = post_current_time - post_start_time
                post_current_seconds = post_current_time_delta.days * 86400 + post_current_time_delta.seconds
                total_seconds = int(post_current_seconds / (percent/100.0))
                left_time_delta = datetime.timedelta(seconds= total_seconds - post_current_seconds)
                collector.post_collector_log(owner, repo, "[{percent}%] left time: {left_time}".format(percent=percent,
                                                                                                       left_time=left_time_delta))

            content.append({
                'no': cur_line_no,
                'line': line
            })
            if len(content) >= post_max_count:
                post_sms_log_function(owner, repo, content, version, repo_id)
                content = []
                post_current_time = datetime.datetime.utcnow()
                post_current_time_delta = post_current_time - post_start_time
                post_current_seconds = post_current_time_delta.days * 86400 + post_current_time_delta.seconds
                total_seconds = int(post_current_seconds / (i*0.1/total_count))
                left_time_delta = datetime.timedelta(seconds= total_seconds - post_current_seconds)
                collector.post_collector_log(owner, repo, "[{percent}%] left time: {left_time}".format(percent=percent,
                                                                                                       left_time=left_time_delta))

        # 上传日志内容
        post_sms_log_function(owner, repo, content, version, repo_id)

        content = []
        collector.post_collector_log(owner, repo, "Posted all lines.")

        collector.logout_sms_log_collector(owner, repo, status='complete')

        collector.post_collector_log(owner, repo, "Goodbye")


@click.group()
def cli():
    pass


@cli.command()
@click.option('-c', '--config', default=DEFAULT_CONFIG_FILE_PATH, help="config file path")
@click.option('-o', '--owner', help="owner name", required=True)
@click.option('-r', '--repo', help="repo name", required=True)
@click.option('-l', '--limit', type=int, default=-1, help="limit count")
@click.option('-t', '--upload-type', type=click.Choice(['mysql, kafka']), default='kafka', help="upload type")
def collect(config, owner, repo, limit, upload_type):
    """
    处理 collect 命令，收集日志
    :param config:
    :param owner:
    :param repo:
    :param limit:
    :param upload_type:
    :return:
    """
    click.echo("Config file: {config}".format(config=config))
    click.echo('User name: {owner}'.format(owner=owner))
    click.echo('Repo name: {repo}'.format(repo=repo))
    click.echo("The number of appended records is limited to {limit}".format(limit=limit))
    click.echo("Upload type: {upload_type}".format(upload_type=upload_type))
    agent_appender(config, owner, repo, limit, upload_type)


@cli.command()
@click.option('-c','--config', default=DEFAULT_CONFIG_FILE_PATH, help="config file path")
@click.option('-o','--owner', help="owner name", required=True)
@click.option('-r','--repo', help="repo name", required=True)
def show(config, owner, repo):
    """
    处理 show 命令，显示项目信息
    :param config:
    :param owner:
    :param repo:
    :return:
    """
    click.echo("Config file: {config}".format(config=config))
    click.echo('User name: {owner}'.format(owner=owner))
    click.echo('Repo name: {repo}'.format(repo=repo))

    collector = SmsLogCollector()
    collector.load_config(config)

    info_response = collector.get_sms_log_collector_info(owner, repo)
    if 'error' in info_response:
        collector.post_collector_log(owner, repo, "There is some error:")
        collector.post_collector_log(owner, repo, info_response['error_type'])
        collector.post_collector_log(owner, repo, "ERROR: Collector exist.")
        collector.post_collector_error_log(owner, repo, "Collector exist.")
        return

    info_data = info_response['data']
    sms_log_file_path = info_data['path']
    head_line = info_data['head_line']
    last_line_no = info_data['last_line_no']
    repo_id = info_data['repo_id']
    version = info_data['version']

    collector.post_collector_log(owner, repo, """SMS log repo info for {owner}/{repo}:
    version: {version}
    path: {path}
    head_line: {head_line}
    last_line_no: {last_line_no}""".format(
        owner=owner, repo=repo,
        version=version,
        path=sms_log_file_path,
        head_line=head_line,
        last_line_no=last_line_no))
    return


if __name__ == "__main__":
    # start_time = datetime.datetime.utcnow()

    cli()

    # end_time = datetime.datetime.utcnow()
    # print(end_time - start_time)
