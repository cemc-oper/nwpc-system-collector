from datetime import datetime


class Record(object):
    def __init__(self):
        self.record_id = None
        self.repo_id = None
        self.version_id = None
        self.line_no = None
        self.record_type = None
        self.record_date = None
        self.record_time = None
        self.record_command = None
        self.record_fullname = None
        self.record_additional_information = None
        self.record_string = None

    def show(self):
        print self.record_id
        print self.repo_id
        print self.version_id
        print self.line_no
        print self.record_type
        print self.record_date
        print self.record_time
        print self.record_command
        print self.record_fullname
        print self.record_additional_information
        print self.record_string


    def parse(self, line):
        self.record_string = line
        start_pos = 2
        end_pos = line.find(':')
        self.record_type = line[start_pos:end_pos]

        start_pos = end_pos + 2
        end_pos = line.find(']', start_pos)
        record_time_string = line[start_pos:end_pos]
        date_time = datetime.strptime(record_time_string, '%H:%M:%S %d.%m.%Y')
        self.record_date = date_time.date()
        self.record_time = date_time.time()

        start_pos = end_pos + 2
        end_pos = line.find(":", start_pos)
        self.record_command = line[start_pos:end_pos]

        if self.record_command in ('submitted', 'active', 'queued', 'complete', 'aborted'):
            self.record_fullname = line[end_pos+1:].strip()
        elif self.record_command == 'alter':
            start_pos = end_pos+1
            pos = line.find(' [v', start_pos)
            if pos != -1:
                self.record_fullname = line[start_pos:pos]
        elif self.record_command == 'meter':
            start_pos = end_pos + 1
            end_pos = line.find(' ', start_pos)
            self.record_fullname = line[start_pos:end_pos]
            start_pos = end_pos + 4
            self.record_additional_information = line[start_pos:]
        elif self.record_command == 'begin':
            start_pos = end_pos + 1
            end_pos = line.find(' ', start_pos)
            self.record_fullname = line[start_pos: end_pos]