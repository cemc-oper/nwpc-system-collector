import zmq
import config


def main():

    print "Processor is starting up..."

    context = zmq.Context()

    processor_socket = context.socket(zmq.SUB)
    processor_socket.connect("tcp://localhost:{processor_socket_no}"
                             .format(processor_socket_no=config.PROCESSOR_SOCKET_NO))
    processor_socket.setsockopt(zmq.SUBSCRIBE, '')

    print "Processor is listening on tcp://localhost:{processor_socket_no}..."\
        .format(processor_socket_no=config.PROCESSOR_SOCKET_NO)

    while True:
        message = processor_socket.recv_string()
        print message


if __name__ == "__main__":
    main()