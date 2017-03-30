from .node_variable import SmsNodeVariable, SmsNodeVariableType


class SmsNode(object):
    def __init__(self):
        self.variable_list = []
        self.generated_variable_list = []
        self.name = ''
        self.status = None
        self.node_type = None

    @staticmethod
    def create_from_cdp_output(cdp_output):
        # find status
        cur_line_no = 0
        line_count = len(cdp_output)

        while cur_line_no < line_count:
            line = cdp_output[cur_line_no]
            if len(line) > 0 and line.startswith('/') and not line.startswith('/-CDP'):
                break
            cur_line_no += 1
        if cur_line_no == line_count:
            return None

        # find show
        while cur_line_no < line_count:
            line = cdp_output[cur_line_no]
            if line == '\n':
                break
            cur_line_no += 1

        cur_line_no += 1
        if cur_line_no >= line_count:
            return None

        line = cdp_output[cur_line_no]
        if line[0].startswith('#'):
            return None

        start_line_no = cur_line_no

        cur_line_no += 1
        end_line_no = -1
        while cur_line_no < line_count:
            line = cdp_output[cur_line_no]
            if not line.startswith('  '):
                end_line_no = cur_line_no
                break
            cur_line_no += 1

        if end_line_no == -1:
            return None

        # get variables
        node_line = cdp_output[start_line_no: end_line_no]
        node = SmsNode()
        tokens = node_line[0].strip().split(' ')
        if len(tokens) > 5:
            node.node_type = tokens[0]
            node.name = tokens[1]
            node.status = tokens[4]

        for line in node_line[1:]:
            line = line.strip()
            if line.startswith('# genvar '):
                index = line.find(' ', 9)
                if index == -1:
                    continue
                variable_name = line[9:index]
                variable_value = line[index + 1:]
                if variable_value[0] == '\'' and variable_value[-1] == '\'':
                    variable_value = variable_value[1:-1]
                variable = SmsNodeVariable(
                    SmsNodeVariableType.GeneratedVariable,
                    variable_name,
                    variable_value
                )
                node.generated_variable_list.append(variable)
            elif line.startswith('edit '):
                index = line.find(' ', 5)
                if index == -1:
                    continue
                variable_name = line[5:index]
                variable_value = line[index + 1:]
                if variable_value[0] == '\'' and variable_value[-1] == '\'':
                    variable_value = variable_value[1:-1]
                variable = SmsNodeVariable(
                    SmsNodeVariableType.Variable,
                    variable_name,
                    variable_value
                )
                node.variable_list.append(variable)
            else:
                pass

        return node

    def to_dict(self):
        return {
            'name': self.name,
            'status': self.status,
            'node_type': self.node_type,
            'variable_list': [var.to_dict() for var in self.variable_list],
            'generated_variable_list': [var.to_dict() for var in self.generated_variable_list]
        }

    @staticmethod
    def create_from_dict(node_dict):
        node = SmsNode()
        node.name = node_dict['name']
        node.status = node_dict['status']
        node.node_type = node_dict['node_type']
        for a_var_dict in node_dict['variable_list']:
            a_var = SmsNodeVariable.create_from_dict(a_var_dict)
            node.variable_list.append(a_var)
        for a_var_dict in node_dict['generated_variable_list']:
            a_var = SmsNodeVariable.create_from_dict(a_var_dict)
            node.generated_variable_list.append(a_var)
        return node

    def get_variable(self, variable_name):
        for var in self.variable_list:
            if var.name == variable_name:
                return var
        for var in self.generated_variable_list:
            if var.name == variable_name:
                return var
        return None

    def get_variable_value(self, variable_name):
        var = self.get_variable(variable_name)
        if var is None:
            return None
        else:
            return var.value
