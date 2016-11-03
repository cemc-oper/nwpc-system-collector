# coding=utf-8
from nwpc_hpc_collector.loadleveler.query_property import QueryProperty


class QueryItem(object):
    def __init__(self):
        self.props = list()

    @staticmethod
    def build_from_category_list(record, category_list):
        item = QueryItem()

        for a_category in category_list:
            p = QueryProperty.build_from_category(record, a_category)
            item.props.append(p)

        return item
