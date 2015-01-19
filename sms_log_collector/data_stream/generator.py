import zmq
import config


sms_log_file_path = '/cma/u/nwp/smsworks/sms/cma20n03.sms.log'


def main():
    context = zmq.Context()

    agent_socket = context.socket(zmq.REQ)
    agent_socket.connect("tcp://localhost:{agent_socket_no}".format(agent_socket_no=config.AGENT_SOCKET_NO))

    f = open(sms_log_file_path)
    cur_line = -1
    for line in f:
        cur_line += 1

        request = {
            'type': 'smslog',
            'line_no': cur_line,
            'content': line
        }

        agent_socket.send_json(request)
        response = agent_socket.recv_json()
        print response


if __name__ == '__main__':
    main()
