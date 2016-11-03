# coding=utf-8


class QueryProperty(dict):
    @staticmethod
    def build_from_category(record, category):
        item = QueryProperty()

        item['category'] = category
        value = category.record_parser.parse(record)
        category.value_saver.set_item_value(item, value)
        return item
