# coding: utf-8
import re
from nwpc_work_flow_model.sms import Bunch, NodeStatus


class SmsStatusAnalyzer(object):
    def __init__(self):
        self.cur_level = 0
        self.cur_node_path = ''

        # level_mapper 结构示例：
        # { level_start_position: level_no }
        self.level_mapper = dict()
        self.level_mapper[0] = 0

        # node_status 结构示例：
        # {
        #   'path': '/obs_reg'
        #   'name': 'obs_reg'
        #   'status': 'com'
        # }
        self.bunch = Bunch()

    def analytic_tokens(self, line_start_pos, line_tokens):
        cur_pos = line_start_pos
        for i in range(0, len(line_tokens)-1, 4):
            node_name_part = line_tokens[i]
            blank_part_one = line_tokens[i + 1]
            status_part = line_tokens[i + 2]
            blank_part_two = line_tokens[i + 3]
            if cur_pos not in self.level_mapper:
                self.level_mapper[cur_pos] = self.cur_level
            else:
                level_no = self.level_mapper[cur_pos]
                self.cur_level = level_no
                cur_node_path_tokens = self.cur_node_path.split('/')
                new_node_path_tokens = cur_node_path_tokens[0: level_no+1]
                self.cur_node_path = '/'.join(new_node_path_tokens)
            self.cur_level += 1
            node_path = self.cur_node_path + '/' + node_name_part
            status_item = {
                'path': node_path,
                'name': node_name_part,
                'status': NodeStatus(status_part)
            }
            self.bunch.add_node_status(status_item)
            self.cur_node_path = node_path
            cur_pos += len(node_name_part) + len(blank_part_one) + len(status_part) + len(blank_part_two)

    def analyse_node_status(self, lines):
        lines_length = len(lines)
        cur_line_no = 0
        while cur_line_no < lines_length and not lines[cur_line_no].startswith('/'):
            cur_line_no += 1

        if cur_line_no == lines_length:
            # 没有获取的数据
            return None

        # 分析第一行，示例
        # /{act}   obs_reg         [que]   aob       [que]   00E      [com]   getgmf              {com}
        cur_line = lines[cur_line_no].rstrip(' ')
        first_level = {
            'path': '/',
            'name': '',
            'status': NodeStatus(cur_line[2:5])
        }
        self.bunch.add_node_status(first_level)
        tokens = re.split('(\W+|\{[a-z]{3}\}|\[[a-z]{3}\])', cur_line)
        start_pos = len(tokens[0]) + len(tokens[1]) + len(tokens[2]) + len(tokens[3])
        self.analytic_tokens(start_pos, tokens[4:])
        cur_line_no += 1
        while not lines[cur_line_no].startswith("# "):
            cur_line = lines[cur_line_no].rstrip(' ')
            # 使用 re.split('( +)', cur_line) 无法处理如下的特殊情况
            # 特殊情况：make_aob_rens_oracle{com}
            tokens = re.split('(\W+|\{[a-z]{3}\}|\[[a-z]{3}\])', cur_line)
            if len(tokens) <= 5:
                cur_line_no += 1
                continue
            start_pos = len(tokens[0]) + len(tokens[1])
            self.analytic_tokens(start_pos, tokens[2:])
            cur_line_no += 1
        return self.bunch
