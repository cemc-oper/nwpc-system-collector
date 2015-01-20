import time

import zmq

import config


count_per_commit = 1000


def main():

    print "Processor is starting up..."

    context = zmq.Context()

    processor_socket = context.socket(zmq.SUB)
    processor_socket.connect("tcp://localhost:{processor_socket_no}"
                             .format(processor_socket_no=config.PROCESSOR_SOCKET_NO))
    processor_socket.setsockopt(zmq.SUBSCRIBE, '')

    print "Processor is listening on tcp://localhost:{processor_socket_no}..."\
        .format(processor_socket_no=config.PROCESSOR_SOCKET_NO)

    message_list = []

    while True:
        message = processor_socket.recv_json()
        message_list.append(message)
        if len(message_list) >= count_per_commit:
            print 'commit message...',
            time.sleep(1)
            print 'Done'
            message_list = []


if __name__ == "__main__":
    main()