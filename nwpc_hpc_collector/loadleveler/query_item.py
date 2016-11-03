# coding=utf-8
from nwpc_hpc_collector.loadleveler.query_property import QueryProperty


class QueryItem(list):
    @staticmethod
    def build_from_category_list(record, category_list):
        item = QueryItem()

        for a_category in category_list:
            p = QueryProperty.build_from_category(record, a_category)
            item.append(p)

        return item
