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


Refine_formalize_prompt = {
    "system_prompt": 'You are an experienced mathematician, and you are familiar with formal languages. \
        I would like you to improve the formal form of a mathematical problem.',
    "user_prompt": '''Question:{Question}
    Origin Formalize:{Origin}
    The formal form of the math problem above can be seen as three parts: variable definition, variable assignment, and constraint construction.\
    Now these three parts are a bit confusing. I hope to refine the form: any numbers that originally appeared in the constraint construction part will be replaced by variables. \
    These variables will be defined in the first part and assigned in the second part. \
    In other words, there will be no numbers in the new constraint part. You can think about it first, and then output your answer between <ans> XXX </ans>
    ''',
    "ans_expr": get_refine_formarlize
}


def get_formlize2tabular(text):
    pass

Formlize2Tabular_prompt = {
    "system_prompt": """
The user will provide a problem and its formal representation. You need to convert the **explicitly assigned known data** of the problem into a tabular form. 
The table should **only include variables that are directly assigned values in the problem** (e.g., via assertions like `(= variable value)`). 
Do not include derived or calculated values (e.g., values defined as fractions or multiples or addition and subtraction of other variables).

Replace the variables that appear in the table in the original problem with the unknowns, to generate a generalized problem (i.e., table + generalization = original problem). 
Set a value range for each variable, ensuring the ranges conform to common sense (they can be fixed values if appropriate).


EXAMPLE INPUT:
{
"problem": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?\n",
"formal_problem": "(declare-fun hourly_rate () Real)\n
                    (declare-fun minutes_worked () Int)\n
                    (declare-fun hours_worked () Real)\n
                    (declare-fun earnings () Real)\n\n
                    (assert (= hourly_rate 12.0))\n
                    (assert (= minutes_worked 50))\n
                    (assert (= minutes_per_hour 60))\n
                    (assert (= hours_worked (/ minutes_per_hour)))\n
                    (assert (= earnings (* hourly_rate hours_worked)))\n\n
                    (check-sat)\n
                    (get-value (earnings))"
}
EXAMPLE JSON OUTPUT:
{
  "problem": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?",
  "formal_problem": "(declare-fun hourly_rate () Real)\n
                    (declare-fun minutes_worked () Int)\n
                    (declare-fun hours_worked () Real)\n
                    (declare-fun earnings () Real)\n\n
                    (assert (= hourly_rate 12.0))\n
                    (assert (= minutes_worked 50))\n
                    (assert (= hours_worked (/ (to_real minutes_worked) 60)))\n
                    (assert (= earnings (* hourly_rate hours_worked)))\n\n
                    (check-sat)\n
                    (get-value (earnings))"
  "table":  [
    {
      "name": "Weng", 
      "hourly_rate": 12, 
      "minutes_worked": 50,
      "minutes_per_hour": 60
    }
  ]
  "generalization": "Weng earns $x an hour for babysitting. Yesterday, she just did t minutes of babysitting. How much did she earn?"
  "value_ranges": {
    "name":None,
    "hourly_rate": {
      "min": 7.25,
      "max": 100,
      "unit": "dollars"
    },
    "minutes_worked": {
      "min": 10,
      "max": 1440,
      "unit": "minutes"
    }
    "minutes_per_hour":{
      "min": 60,
      "max": 60,
      "unit": "minutes"
    }
  }
}
""",
    "user_prompt": """
"problem":{Question}\n
"formal_problem":{Formal_problem}
""",
    "ans_expr": get_formlize2tabular
}