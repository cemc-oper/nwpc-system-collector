import argparse
import os
import subprocess
import re


def get_sms_status(sms_name, sms_user, sms_password):
    command_string = "login {sms_name} {sms_user}  {sms_password};status;quit".format(
        sms_name=sms_name,
        sms_user=sms_user,
        sms_password=sms_password
    )
    echo_pipe = subprocess.Popen(['echo', command_string], stdout=subprocess.PIPE)
    cdp_pipe = subprocess.Popen(['/cma/u/app/sms/bin/cdp'],
                                stdin=echo_pipe.stdout,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    echo_pipe.stdout.close()
    (cdp_output, cdp_error) = cdp_pipe.communicate()
    return_code = cdp_pipe.returncode
    #print 'return code:', return_code
    if return_code <> 0:
        print "ERROR"
        print cdp_error
        return
    #print cdp_output
    cdp_output_lines = cdp_output.split('\n')
    #print cdp_output_lines
    status_lines = []
    for line in cdp_output_lines:
        if line.startswith('Welcome') or line.startswith('#') or line=='' or line.startswith('Goodbye'):
            #print "[ ] ", line
            pass
        else:
            status_lines.append(line)
            #print "[x] ", line

    #first_line = re.compile(r"^/\{[a-z]+\}( )*([! ])*\[([a-z])*\]( )*")
    first_line = re.compile(r"^/(\[|\{)([a-z]+)(\]|\}) *([a-zA-z0-9_]*) *(\[|\{)([a-z]+)(\]|\}) *")

    none_first_line = re.compile(r"^ *([a-zA-z0-9_]*) *(\[|\{)([a-z]+)(\]|\}) *")

    #print status_lines
    for a_status_line in status_lines:
        m = first_line.match(a_status_line)
        if m is None:
            m2 = none_first_line.match(a_status_line)
            if m2 is None:
                print "LINE: ",a_status_line.split()
            else:
                g = m2.groups()
                print "  |-",g[2], g[0]

        else:
            g = m.groups()
            print "/{sms_name}".format(sms_name=sms_name), g[1]
            print "  |-",g[5], g[3]


def sms_status_command_line_tool():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
DESCRIPTION
    Get sms suites' status.""")

    parser.add_argument("-n", "--name", help="sms server name", required=True)
    parser.add_argument("-u", "--user", help="sms server user name", required=True)
    parser.add_argument("-p", "--password", help="sms server password")

    args = parser.parse_args()

    sms_name = args.name
    sms_user = args.user
    sms_password = "1"
    if args.password:
        sms_password = args.password
    get_sms_status(sms_name, sms_user, sms_password)


if __name__ == "__main__":
    sms_status_command_line_tool()
