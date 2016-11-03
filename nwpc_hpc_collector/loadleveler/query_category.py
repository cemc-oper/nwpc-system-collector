import copy


class QueryCategory(object):
    def __init__(self):
        self.id = ".valid_id"

        self.record_parser = None
        self.value_saver = None

    def __deepcopy__(self, memodict={}):
        new_object = QueryCategory()

        new_object.id = self.id
        if self.record_parser:
            new_object.record_parser = copy.deepcopy(self.record_parser)

        new_object.value_saver = self.value_saver
        return new_object
