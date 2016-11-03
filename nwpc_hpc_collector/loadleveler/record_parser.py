# coding=utf-8


class RecordParser(object):
    def __init__(self):
        self.type = self.__class__

    def parse(self, record):
        pass


class DetailLabelParser(RecordParser):
    def __init__(self, label):
        RecordParser.__init__(self)
        self.type = self.__class__

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
            value = line[index+2: -1].strip()
            return value
        return ""
