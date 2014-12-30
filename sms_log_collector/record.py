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

        if not self.record_string.startswith("# "):
            """some line don't start with '# '

                exit

            just ignore it.
            """
            return

        start_pos = 2
        end_pos = line.find(':')
        self.record_type = line[start_pos:end_pos]

        start_pos = end_pos + 2
        end_pos = line.find(']', start_pos)
        if end_pos == -1:
            """some line is not like what we suppose it to be. Such as:

                # MSG:[02:50:38 22.10.2013] login:User nwp_sp@16239 with password from cma20n03
                readlists
                # MSG:[02:50:48 22.10.2013] logout:User nwp_sp@16239

            So we should check if the line starts with '#[...]'. If not, we don't parse it and just return.
            """
            return
        record_time_string = line[start_pos:end_pos]
        date_time = datetime.strptime(record_time_string, '%H:%M:%S %d.%m.%Y')
        self.record_date = date_time.date()
        self.record_time = date_time.time()

        start_pos = end_pos + 2
        end_pos = line.find(":", start_pos)
        if end_pos == -1:
            """
            some line is not like what we suppose it to be. Such as:

                # WAR:[21:05:13 25.9.2013] SCRIPT-NAME will return NULL, script is [/cma/g1/nwp_sp/SMSOUT/env_grib_v20/T639_ENV/gmf/12/upload/upload_003.sms]

            We need to check end_pos.
            """
            return
        self.record_command = line[start_pos:end_pos]

        if self.record_command in ('submitted', 'active', 'queued', 'complete', 'aborted'):
            start_pos = end_pos+1
            end_pos = line.find(' ', start_pos)
            if end_pos == -1:
                self.record_fullname = line[start_pos:].strip()
            else:
                self.record_fullname = line[start_pos:end_pos]
                self.record_additional_information = line[end_pos+1:]
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
        elif self.record_command == 'force':
            start_pos = end_pos + 1
            end_pos = line.find(' ', start_pos)
            self.record_fullname = line[start_pos:end_pos]
            if line[end_pos:end_pos+4] == " to ":
                start_pos = end_pos + 4
                end_pos = line.find(' ', start_pos)
                self.record_additional_information = line[start_pos:end_pos]