import mysql.connector
from legacy.nwpc_log_collector import Record
from legacy.nwpc_log_collector import Message


class DatabaseEngine(object):
    default_config = {
        'user': 'windroc',
        'password': 'shenyang',
        'host': '10.28.32.175',
        'database': 'smslog',
        'table_name': 'record_nwp_qu_cma18n03'
    }

    def __init__(self):
        self.connect = None
        self.cursor = None
        self.table_name = None

    def create_connect(self, config):
        self.connect = mysql.connector.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            database=config['database']
        )
        self.table_name = config['table_name']

    def close_connect(self):
        self.connect.close()

    def create_cursor(self):
        self.cursor = self.connect.cursor()
        return self.cursor

    def close_cursor(self):
        self.cursor.close()
        self.cursor = None

    def commit_connect(self):
        self.connect.commit()

    def insert_record(self, record):
        query = ("INSERT INTO {table_name} (`record_id`, `repo_id`, `version_id`, `line_no`, "
                 "`record_type`, `record_date`, `record_time`, "
                 "`record_command`,  `record_fullname`,`record_additional_information`, `record_string`) "
                 "VALUES (%(record_id)s, %(repo_id)s, %(version_id)s, %(line_no)s, "
                 "%(record_type)s, %(record_date)s,  %(record_time)s, %(record_command)s, "
                 "%(record_fullname)s, %(record_additional_information)s, %(record_string)s);".format(
                 table_name=self.table_name))

        record_data = {
            'table_name': self.table_name,
            'record_id': record.record_id,
            'repo_id': record.repo_id,
            'version_id': record.version_id,
            'line_no': record.line_no,
            'record_type': record.record_type,
            'record_date': record.record_date,
            'record_time': record.record_time,
            'record_command': record.record_command,
            'record_fullname': record.record_fullname,
            'record_additional_information': record.record_additional_information,
            'record_string': record.record_string
        }
        try:
            self.cursor.execute(query, record_data)
        except mysql.connector.errors.ProgrammingError:
            print self.cursor.statement
            raise

    def update_message(self, message):
        if message.message_id is None:
            print "WARNING: message id must not be None!"
            return

        query = "UPDATE {table_name} SET message_fullname = %(message_fullname)s, " \
                " message_additional_information = %(message_additional_information)s " \
                "WHERE message_id = %(message_id)s".format(table_name=self.table_name)
        message_data = {
            'table_name': self.table_name,
            'message_id': message.message_id,
            'message_type': message.message_type,
            'message_time': message.message_time,
            'message_command': message.message_command,
            'message_fullname': message.message_fullname,
            'message_additional_information': message.message_additional_information,
            'message_string': message.message_string
        }
        try:
            self.cursor.execute(query, message_data)
        except mysql.connector.errors.ProgrammingError:
            print self.cursor.statement
            raise

    def update_record(self, record):
        if record.record_id is None:
            print "WARNING: record id must not be None!"
            return

        query = "UPDATE {table_name} SET record_fullname = %(record_fullname)s, " \
                " record_additional_information = %(record_additional_information)s " \
                "WHERE record_id = %(record_id)s".format(table_name=self.table_name)
        record_data = {
            'table_name': self.table_name,
            'record_id': record.record_id,
            'record_type': record.record_type,
            'record_time': record.record_time,
            'record_command': record.record_command,
            'record_fullname': record.record_fullname,
            'record_additional_information': record.record_additional_information,
            'record_string': record.record_string
        }
        try:
            self.cursor.execute(query, record_data)
        except mysql.connector.errors.ProgrammingError:
            print self.cursor.statement
            raise

    def get_message_count(self, where_string=""):
        query = "SELECT COUNT(message_id) FROM {table_name} ".format(table_name=self.table_name)
        if len(where_string) > 0:
            query += where_string + " "
        self.cursor.execute(query)
        count = -1
        for (count,) in self.cursor:
            pass
        return count

    def select_message(self, where_string="", order_by_string=""):
        query = "SELECT `message_id`,`message_type`,`message_time`,`message_command`, " \
                "`message_fullname`,`message_additional_information`,`message_string` " \
                "FROM {table_name} ".format(table_name=self.table_name)
        if len(where_string) > 0:
            query += where_string + ' '
        if len(order_by_string) > 0:
            query += order_by_string + ' '
        q = (query,)
        self.cursor.execute(query)
        return self.cursor

    def select_record(self, where_string="", order_by_string=""):
        query = "SELECT `record_id`, `repo_id`, `version_id`, `line_no`, `record_type`, `record_date`, "\
                "`record_time`, `record_command`, `record_fullname`, `record_additional_information`, `record_string` "\
                "FROM {table_name} ".format(table_name=self.table_name)
        if len(where_string) > 0:
            query += where_string + ' '
        if len(order_by_string) > 0:
            query += order_by_string + ' '
        q = (query,)
        self.cursor.execute(query)
        return self.cursor

    def get_message(self, where_string="", order_by_string=""):
        query = "SELECT `message_id`,`message_type`,`message_time`,`message_command`, " \
                "`message_fullname`,`message_additional_information`,`message_string` " \
                "FROM {table_name} ".format(table_name=self.table_name)
        if len(where_string) > 0:
            query += where_string + ' '
        if len(order_by_string) > 0:
            query += order_by_string + ' '
        q = (query,)
        self.cursor.execute(query)
        message_list = []
        for (message_id, message_type, message_time, message_command, message_fullname,
             message_additional_information, message_string) in self.cursor:
            message = Message()
            message.message_id = message_id
            message.message_type = message_type
            message.message_time = message_time
            message.message_command = message_command
            message.message_fullname = message_fullname
            message.message_additional_information = message_additional_information
            message.message_string = message_string
            message_list.append(message)

        return message_list