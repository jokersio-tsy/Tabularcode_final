import json
import re

def is_direct_assignment(line):
    """判断是否为直接赋值断言 (= var value) 形式"""
    line = line.strip()
    if not line.startswith('(assert (= '):
        return False

    pattern = r'\(assert\s*\(=\s*([^\s]+)\s*([^\(\)]+)\)\)'
    match = re.fullmatch(pattern, line)
    if not match:
        return False

    _, value = match.groups()
    return not any(op in value for op in ['+', '-', '*', '/', 'to_real', 'div'])


def extract_declared_variables(formal_problem):
    """提取已声明的变量"""
    declared_vars = set()
    for line in formal_problem.split('\n'):
        line = line.strip()
        if line.startswith('(declare-fun '):
            match = re.match(r'\(declare-fun\s+([^\s]+)\s*\(\)\s*([^\)]+)\)', line)
            if match:
                declared_vars.add(match.group(1))
    return declared_vars


def modify_formal_problem(formal_problem, table_data):
    if not formal_problem:
        return formal_problem

    lines = formal_problem.split('\n')
    modified_lines = []
    declared_vars = extract_declared_variables(formal_problem)
    new_declarations = []
    new_assertions = []

    for line in lines:
        line_stripped = line.strip()
        if not is_direct_assignment(line):
            modified_lines.append(line)  #保留不需要修改的行

    if table_data:
        for key, value in table_data[0].items():
            if value is not None and key != 'name':
                if key not in declared_vars:
                    var_type = 'Real' if isinstance(value, float) else 'Int'
                    new_declarations.append(f'(declare-fun {key} () {var_type})')
                    declared_vars.add(key)

                new_assertions.append(f'(assert (= {key} {value}))')

    # 添加新声明
    if new_declarations:
        for i, line in enumerate(modified_lines):
            if line.strip():
                modified_lines[i:i] = new_declarations
                break

    # 调整语句位置
    check_sat_pos = -1
    get_value_pos = -1
    for i, line in enumerate(modified_lines):
        line_stripped = line.strip()
        if line_stripped.startswith('(check-sat') and check_sat_pos == -1:
            check_sat_pos = i
        elif line_stripped.startswith('(get-value') and get_value_pos == -1:
            get_value_pos = i

    insert_pos = check_sat_pos if check_sat_pos != -1 else get_value_pos

    if insert_pos == -1:
        modified_lines.extend(new_assertions)
    else:
        modified_lines[insert_pos:insert_pos] = new_assertions

    return '\n'.join(modified_lines)