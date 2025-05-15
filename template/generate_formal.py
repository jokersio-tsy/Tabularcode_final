import re


# refine formal
def get_refine_formarlize(text):
    pattern = r"<ans>(.*?)</ans>"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        content = match.group(1)
        result_list = content.split('\n')
    else:
        return "Error"

    # code_format = ["(assert","(declare","(get"]
    codes = []
    for code in result_list:
        # print(code)
        if "(assert" in code.lower() or "(declare" in code.lower() or "(get" in code.lower() or "(check" in code.lower():
            codes.append(code)

    result = "\n".join(codes)
    result_list = result.split("\n")
    return result_list

def fix_multi_arg_minus(expr: str) -> str:  #三元运算换成嵌套二元运算
    pattern = r'\(-\s+([^\s\(\)]+)\s+([^\s\(\)]+)\s+([^\s\(\)]+)\)'
    while re.search(pattern, expr):
        expr = re.sub(pattern, r'(- (- \1 \2) \3)', expr)
    return expr

get_formalize_prompt = {
    "system_prompt": """
    You are an experienced mathematician, and you are familiar with formal languages. I would like you to generate the formal form of a mathematical problem.

    You should express all logic in **SMT-LIB syntax**, using **prefix notation**. For example, multiplication should be written as `(* a b)` instead of `a * b`.

    HIGHLIGHT!!!:
    **All numbers appearing after 'assert' are written as floating point numbers.For example '2' is wrong and it should be replaced with '2.0'.**


    EXAMPLE INPUT:
    "problem": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?"

    EXAMPLE JSON OUTPUT:
    {
    "problem": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?"
    "formal_problem":"   (declare-fun hourly_rate () Int)\n
            (declare-fun minutes_worked () Real)\n
            (declare-fun hours_worked () Real)\n
            (declare-fun earnings () Real)\n\n
            (assert (= hourly_rate 12.0))\n
            (assert (= minutes_worked 50.0))\n
            (assert (= minutes_per_hour 60.0))\n
            (assert (= hours_worked (/ minutes_per_hour)))\n
            (assert (= earnings (* hourly_rate hours_worked)))\n\n
            (check-sat)\n
            (get-value (earnings))"
    }
    """,
    
    "user_prompt": """
                    "problem":{Question}\n
                    """,
    "ans_expr": get_refine_formarlize
}

