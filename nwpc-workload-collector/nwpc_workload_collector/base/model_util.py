# coding: utf-8
from nwpc_hpc_model.base.query_item import get_property_data


# TODO: move to nwpc hpc model, and do it in a more proper way.
def get_sort_data(job_item, property_id):
    data = get_property_data(job_item, property_id)
    return data


def generate_sort_key_function(sort_keys):
    def sort_key_function(item):
        key_list = []
        for sort_key in sort_keys:
            key_list.append(get_sort_data(item, sort_key))
        return tuple(key_list)
    return sort_key_function


def sort_items(items, sort_keys=None):
    if sort_keys is None:
        return
    items.sort(key=generate_sort_key_function(sort_keys))
