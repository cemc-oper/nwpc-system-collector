# coding=utf-8
from paramiko import SSHClient


def run_command(client: SSHClient, command: str) -> (str, str):
    stdin, stdout, stderr = client.exec_command(command)
    std_out_string = stdout.read().decode('UTF-8')
    std_error_out_string = stderr.read().decode('UTF-8')

    return std_out_string, std_error_out_string
