# coding: utf-8
import subprocess
from datetime import datetime

from nwpc_sms_collector.sms_status_collector import SmsStatusAnalyzer, Bunch


def get_suite_task_list(owner, repo, sms_name, sms_user, sms_password, node_prefix):
    command_string = "login {sms_name} {sms_user}  {sms_password};status -f;exit".format(
        sms_name=sms_name,
        sms_user=sms_user,
        sms_password=sms_password
    )
    echo_pipe = subprocess.Popen(
        ['echo', command_string],
        stdout=subprocess.PIPE,
        encoding='utf-8')
    cdp_pipe = subprocess.Popen(
        ['/cma/u/app/sms/bin/cdp'],
        stdin=echo_pipe.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8')
    echo_pipe.stdout.close()
    (cdp_output, cdp_error) = cdp_pipe.communicate()
    # print cdp_output
    # TODO: not login error
    return_code = cdp_pipe.returncode
    if return_code != 0:
        current_time = datetime.utcnow().isoformat()
        result = {
            'app': 'sms_status_collector',
            'timestamp': current_time,
            'error': 'command_return_code_error',
            'data': {
                'message': cdp_error
            }
        }
        return result

    tool = SmsStatusAnalyzer()
    node_status_list = tool.analyse_node_status(cdp_output)

    task_list = []
    for a_status in node_status_list:
        task_path = a_status['path']
        if task_path.startswith(node_prefix) and a_status['node_type']:
            task_list.append(a_status['path'])

    return task_list


if __name__ == "__main__":
    task_list = get_suite_task_list('wangdp', 'nwpc_wangdp', 'nwpc_wangdp', 'wangdp', '1', '/grapes_meso_post')
    for a_task in task_list:
        print(a_task)
