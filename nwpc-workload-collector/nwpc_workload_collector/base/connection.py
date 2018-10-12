# coding=utf-8
from paramiko import SSHClient, AutoAddPolicy


def get_ssh_client(auth: dict) -> SSHClient:
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(auth['host'], auth['port'], auth['user'], auth['password'])
    return client
