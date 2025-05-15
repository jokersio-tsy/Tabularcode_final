import argparse
import json
from tqdm import tqdm
import random
import datetime
import signal
from model import *
from utils.smt_utils import solve
from template.generate_temlate import *
from tabulate import tabulate
from utils.table_augmentation import table_augmentation
from template.generate_temlate import Formlize2Tabular_prompt
from template.generate_formal import get_formalize_prompt
from template.generate_formal import fix_multi_arg_minus
from utils.valid import modify_formal_problem 


import os

def get_args():
    parser = argparse.ArgumentParser(description="Process some arguments.")

    parser.add_argument('--input_path', type=str, default="gen_data\\gsm8k.jsonl")
    parser.add_argument('--algo', type = str, default='zero')
    parser.add_argument('--template', type = str, default='Math')
    parser.add_argument('--gpu', type = str, default='0')
    parser.add_argument('--log',type= str,default=None,help= "results log")
    parser.add_argument('--output_path',type = str, default='results')
    parser.add_argument('--ColAug',type = int, default=0)
    parser.add_argument('--RowAug',type = int, default=0)
    parser.add_argument('--OrdShf',type = str, default=False)
    parser.add_argument('--InfMut',type = str, default=None)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    print(args)

    import datetime

    current_time = datetime.datetime.now()

    args.time = current_time.strftime("%m%d-%H:%M")
    print("Time:", args.time)

    os.environ["CUDA_VISIBLE_DEVICES"]=args.gpu

    chat_model = DeepSeek_API(model = 'deepseekv3')

    output_file = os.path.join(args.output_path,"new_data.jsonl")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    f_out=open(output_file,'w')

    directory = os.path.dirname(output_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    data = []
    with open(args.input_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))

    for data_each in data:

        record = {}
        record['problem'] = data_each['problem']
        record['target'] = data_each['target']
        # record['formal_problem'] = data['formal problem']

        #get formalize problem
        #Todo
        message = [
            {'role': "system", "content": get_formalize_prompt['system_prompt']},
            {'role': "user", "content": get_formalize_prompt['user_prompt'].format(Question=data_each['problem'])}
        ]

        response_format={'type': 'json_object'}

        response_Table = chat_model.chat(my_prompt=message,format=response_format)
        formal_problem = json.loads(response_Table).get("formal_problem", [])
        formal_problem = formal_problem.replace("Int","Real")
        formal_problem = formal_problem.replace("(div","(/")
        formal_problem = fix_multi_arg_minus(formal_problem)



        print(formal_problem)
        # add valid 1
        #Todo
        ok, result = solve(formal_problem)
        if ok is not True or abs(float(result[0]) - float(record['target'])) > 1e-4:
            print(f"solve fail. - {result}")
            continue
        

        # formalize 2 tabular
        message = [
            {'role': "system", "content": Formlize2Tabular_prompt['system_prompt']},
            {'role': "user", "content": Formlize2Tabular_prompt['user_prompt'].format(Question=data_each['problem'],
                                                                                        Formal_problem=formal_problem)}
        ]

        response_format={'type': 'json_object'}

        response_Table = chat_model.chat(my_prompt=message,format=response_format)
        table_data = json.loads(response_Table).get("table", [])
        root_line = table_data[0]
        if "name" not in root_line:
            print(f"No name error.")
            continue            
        generalization_problem=json.loads(response_Table).get("generalization")
        value_ranges=json.loads(response_Table).get("value_ranges")

        # show root table
        headers = table_data[0].keys() if table_data else []
        rows = [list(row.values()) for row in table_data]
        print(tabulate(rows, headers=headers, tablefmt="grid"))

        # add valid 2
        # Todo
        modify_problem = modify_formal_problem(formal_problem, table_data)
        ok, result = solve(modify_problem)
        if ok is not True or abs(float(result[0]) - float(record['target'])) > 1e-4:
            print(f"unvalid. - {result}")
            continue



        # table_augmentation
        augmented_table = table_augmentation(table_data=table_data,args=args,value_ranges=value_ranges)

        record['problem'] = generalization_problem
        record['table'] = augmented_table
        record['target'] = data_each['target']
        print(record)
        f_out.write(json.dumps(record, ensure_ascii=False) + '\n')



