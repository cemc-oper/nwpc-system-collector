# coding=utf-8


class RecordParser(object):
    def __init__(self):
        pass

    def parse(self, record):
        pass


class DetailLabelParser(RecordParser):
    def __init__(self, label):
        RecordParser.__init__(self)

        self.label = label

    def __deepcopy__(self, memodict={}):
        return DetailLabelParser(self.label)

    def parse(self, record):
        for line in record:
            index = line.find(': ')
            if index == -1:
                continue
            label = line[0:index].strip()
            if label != self.label:
                continue
            value = line[index+2:].strip()
            return value
        return ""


class LlqJobScriptParser(RecordParser):
    def __init__(self):
        RecordParser.__init__(self)

    @staticmethod
    def find_step_type_value(record):
        parser = DetailLabelParser("Step Type")
        value = parser.parse(record)
        return value

    def parse(self, record):
        step_type = LlqJobScriptParser.find_step_type_value(record)

        if step_type == "General Parallel":
            script_label = "Executable"
        elif step_type == "Serial":
            script_label = "Cmd"
        else:
            return ""

        for line in record:
            index = line.find(': ')
            if index == -1:
                continue
            label = line[0:index].strip()
            if label != script_label:
                continue
            value = line[index+2:].strip()
            return value
        return ""


class TableRecordParser(RecordParser):
    def __init__(self, begin_pos, end_pos):
        RecordParser.__init__(self)
        self.begin_pos = int(begin_pos)
        self.end_pos = int(end_pos)

    def parse(self, record):
        return record[self.begin_pos:self.end_pos].strip()
