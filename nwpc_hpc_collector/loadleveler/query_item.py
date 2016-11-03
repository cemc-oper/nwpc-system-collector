# coding=utf-8


class QueryItem(dict):
    @staticmethod
    def build_from_record(record, category):
        item = QueryItem()

        item['category'] = category
        value = category.record_parser.parse(record)
        print(value)
        category.value_saver.set_item_value(item, value)
        return item
