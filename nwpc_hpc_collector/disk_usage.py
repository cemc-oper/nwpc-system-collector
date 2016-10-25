import subprocess
import os
import re
import locale


def get_user_name() -> str:
    if 'USER' in os.environ:
        return os.environ["USER"]
    else:
        cmquota_command = "whoami"
        pipe = subprocess.Popen([cmquota_command], stdout=subprocess.PIPE, shell=True)
        return pipe.communicate()[0].rstrip()


def run_cmquota_command() -> str:
    cmquota_command = "/cma/u/app/sys_bin/cmquota ${USER}"
    pipe = subprocess.Popen([cmquota_command], stdout=subprocess.PIPE, shell=True)
    output = pipe.communicate()[0]
    return output


def get_cmquota() -> dict:
    user = get_user_name()
    result_lines = run_cmquota_command().split("\n")

    detail_pattern = r'^(\w+) +(\w+) +(\d+) +(\d+) +(\d+) +(\d+) +(\w+) \| +(\d+) +(\d+) +(\d+) +(\d+) +(\w+) +(\w+)'
    detail_prog = re.compile(detail_pattern)
    quota_result = dict()
    file_system_list = list()

    for a_line in result_lines:
        detail_re_result = detail_prog.match(a_line)
        if detail_re_result:
            file_system = detail_re_result.group(1)
            quota_type = detail_re_result.group(2)

            current_usage = detail_re_result.group(3)
            if current_usage.isdigit():
                current_usage = locale.atoi(current_usage)

            block_quota = detail_re_result.group(4)
            if block_quota.isdigit():
                block_quota = locale.atoi(block_quota)

            block_limit = detail_re_result.group(5)
            if block_limit.isdigit():
                block_limit = locale.atoi(block_limit)

            block_in_doubt = detail_re_result.group(6)
            if block_in_doubt.isdigit():
                block_in_doubt = locale.atoi(block_in_doubt)

            block_grace = detail_re_result.group(7)

            file_files = detail_re_result.group(8)
            if file_files.isdigit():
                file_files = locale.atoi(file_files)

            file_quota = detail_re_result.group(9)
            if file_quota.isdigit():
                file_quota = locale.atoi(file_quota)

            file_limit = detail_re_result.group(10)
            if file_limit.isdigit():
                file_limit = locale.atoi(file_limit)

            file_in_doubt = detail_re_result.group(11)
            if file_in_doubt.isdigit():
                file_in_doubt = locale.atoi(file_in_doubt)

            file_grace = detail_re_result.group(12)
            file_remarks = detail_re_result.group(13)

            current_file_system = dict()
            current_file_system['file_system'] = file_system
            current_file_system['type'] = quota_type

            block_limits = {
                'current': current_usage,
                'quota': block_quota,
                'limit': block_limit,
                'in_doubt': block_in_doubt,
                'grace': block_grace
            }
            file_limits = {
                'files': file_files,
                'quota': file_quota,
                'limit': file_limit,
                'in_doubt': file_in_doubt,
                'grace': file_grace,
                'remarks': file_remarks
            }
            current_file_system['block_limits'] = block_limits
            current_file_system['file_limits'] = file_limits

            file_system_list.append(current_file_system)

    quota_result['file_systems'] = file_system_list
    quota_result['user'] = user
    return quota_result


if __name__ == "__main__":
    print(get_user_name())
    print(run_cmquota_command())