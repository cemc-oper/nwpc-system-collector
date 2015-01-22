import json
import time

import zmq

import config


count_per_commit = 1000


def main():
    print "Processor is starting up...",

    context = zmq.Context()

    processor_socket = context.socket(zmq.SUB)
    processor_socket.connect("tcp://localhost:{processor_socket_no}"
                             .format(processor_socket_no=config.PROCESSOR_SOCKET_NO))

    processor_socket.setsockopt(zmq.SUBSCRIBE, 'smslog')

    print "Done"

    print "Processor is listening on tcp://localhost:{processor_socket_no}..."\
        .format(processor_socket_no=config.PROCESSOR_SOCKET_NO)

    message_list = []

    while True:
        message = processor_socket.recv_multipart()

        if len(message) != 2:
            print "Error message:", message
            continue

        message_topic = message[0]
        message_body = json.loads(message[1])

        if message_body['type'] == 'smslog':
            message_list.append(message_body)
            if len(message_list) >= count_per_commit:
                print 'commit by count_per_commit...',
                time.sleep(2)
                print len(message_list), 'committed'
                message_list = []
        elif message_body['type'] == 'control':
            if message_body['command'] == 'commit':
                print 'commit by control message...',
                time.sleep(0.1)
                print len(message_list), 'committed'
                message_list = []


if __name__ == "__main__":
    main()