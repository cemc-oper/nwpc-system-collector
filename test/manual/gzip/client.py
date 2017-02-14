# coding=utf-8
import requests
import os
import json
import datetime
import gzip

normal_url = 'http://10.28.32.175:6220/api/normal'
gzip_url = 'http://10.28.32.175:6220/api/gzip'

# normal_url = 'https://www.nwpcmonitor.cc/api/v1/test/gzip/normal'
# gzip_url = 'https://www.nwpcmonitor.cc/api/v1/test/gzip/compress'


def send_normal(data_file_path):
    with open(data_file_path, 'r') as f:
        print("reading file...")
        content = f.read()
        print("reading file...done")
        json_content = json.loads(content)
        message_content = json.dumps(json_content)

        start_time = datetime.datetime.now()
        result = requests.post(normal_url, data={
            'message': message_content
        })
        end_time = datetime.datetime.now()
        print(result)
        print(len(message_content))
        return end_time - start_time


def send_gzip(data_file_path):
    with open(data_file_path, 'r') as f:
        print("reading file...")
        content = f.read()
        print("reading file...done")
        json_content = json.loads(content)
        message_content = json.dumps(json_content)

        start_time = datetime.datetime.now()
        message_gzip_content = gzip.compress(bytes(json.dumps({
            'message': message_content
        }), 'utf-8'))

        result = requests.post(gzip_url, data=message_gzip_content, headers={
            'content-encoding': 'gzip'
        })
        end_time = datetime.datetime.now()
        print(result)

        print(len(message_gzip_content))
        return end_time - start_time


if __name__ == "__main__":

    file_path = os.path.join(os.path.dirname(__file__), 'data_eps_nwpc_qu.json')
    print(send_normal(file_path))
    print(send_gzip(file_path))
