from datetime import datetime


class Message(object):
    def __init__(self):
        self.message_id = None
        self.message_type = None
        self.message_time = None
        self.message_command = None
        self.message_fullname = None
        self.message_additional_information = None
        self.message_string = None

    def parse(self, line):
        self.message_string = line
        start_pos = 2
        end_pos = line.find(':')
        self.message_type = line[start_pos:end_pos]

        start_pos = end_pos + 2
        end_pos = line.find(']', start_pos)
        message_time_string = line[start_pos:end_pos]
        self.message_time = datetime.strptime(message_time_string, '%H:%M:%S %d.%m.%Y')

        start_pos = end_pos + 2
        end_pos = line.find(":", start_pos)
        self.message_command = line[start_pos:end_pos]

        if self.message_command in ('submitted', 'active', 'queued', 'complete', 'aborted'):
            self.message_fullname = line[end_pos+1:].strip()
        elif self.message_command == 'alter':
            start_pos = end_pos+1
            pos = line.find(' [v', start_pos)
            if pos != -1:
                self.message_fullname = line[start_pos:pos]
        elif self.message_command == 'meter':
            start_pos = end_pos + 1
            end_pos = line.find(' ', start_pos)
            self.message_fullname = line[start_pos:end_pos]
            start_pos = end_pos + 4
            self.message_additional_information = line[start_pos:]
        elif self.message_command == 'begin':
            start_pos = end_pos + 1
            end_pos = line.find(' ', start_pos)
            self.message_fullname = line[start_pos: end_pos]