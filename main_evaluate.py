import argparse
import json
from tqdm import tqdm
import random
import datetime
import signal
from model import *
from utils.check import check
from template.generate_temlate import *
from tabulate import tabulate
from algo.Solve_zero import Zero_Solver
from utils.misc import *
from utils.metrictrack import *
import datetime
import signal

import os
os.environ["http_proxy"] = 'http://114.212.20.200:7890'
os.environ["https_proxy"] = 'http://114.212.20.200:7890'
os.environ['all_proxy'] = 'socks5://114.212.20.200:7890'

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException()

def get_args():
    parser = argparse.ArgumentParser(description="Process some arguments.")

    parser.add_argument('--model', type=str, default="deepseekv3")
    parser.add_argument('--dataset', type=str, default='gsm8k')
    parser.add_argument('--algo', type = str, default='zero')
    parser.add_argument('--template', type = str, default='Math')
    parser.add_argument('--gpu', type = str, default='0')
    parser.add_argument('--data_path',type = str, default='gen_data/augmented',help="path of datset")
    parser.add_argument('--sample',type = int, default=2000, help="only test 200 sample on each dataset to fast reason")
    parser.add_argument('--format', default = "se",choices=["se","md"], help="table format")
    parser.add_argument('--final',action="store_true",help="final results")
    parser.add_argument('--log',type= str,default="my_log",help= "results log")
    parser.add_argument('--output_path',type = str, default='results')
    parser.add_argument('--solve_table',action="store_true")
    parser.add_argument('--resume',action="store_true")
    parser.add_argument('--enable_thinking',action="store_true")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    
    logger = setup_logger(experiment_name=args.log)
    logger.info(f"Experiment parameters: {args}")
    logger.info(f"Dataset: {args.dataset}")
    logger.info(f"Algo: {args.algo}")
    logger.info(f"Model: {args.model}")
    logger.info(f"Format: {args.format}")

    # 获取当前时间
    current_time = datetime.datetime.now()

    args.time = current_time.strftime("%m%d-%H:%M")
    print("Time:", args.time)

    os.environ["CUDA_VISIBLE_DEVICES"]=args.gpu

    if "deepseek" in args.model:
        chat_model = DeepSeek_API(model = args.model)
    elif "Qwen3" in args.model:
        chat_model = Qwen3(model=args.model,enable_thinking=args.enable_thinking)
    elif "Qwen" in args.model:
        chat_model = Qwen(model=args.model)
    elif "GLM" in args.model:
        chat_model = GLM()
    elif "GPT4" in args.model:
        chat_model = GPT4()
    elif "Gemini" in args.model:
        chat_model = Gemini()
    elif "TableGPT" in args.model:
        chat_model = TableGPT()
    elif "llama" in args.model.lower():
        chat_model = Llama(model=args.model)
    elif "structlm" in args.model.lower():
        chat_model = StructLM(model=args.model)
    elif "tablellm" in args.model.lower():
        chat_model = TableLLM(model=args.model)

    else:
        raise ValueError
    
    if args.algo == "zero":
        Solver = Zero_Solver()
    else:
        raise ValueError
    
    file_path = args.data_path + "/" + args.dataset + ".jsonl" 
    start_id = 0
    if args.enable_thinking == True:
        output_file = os.path.join(args.output_path,args.model,args.dataset + "_" + args.algo + "_thinking_" + args.format + ".jsonl")
    else:
        output_file = os.path.join(args.output_path,args.model,args.dataset + "_" + args.algo + "_" + args.format + ".jsonl")
    directory = os.path.dirname(output_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if args.resume == True:
        if os.path.exists(output_file):
            last_line,cnt = read_last_line_of_jsonl(file_path=output_file)
            start_id = last_line.get('id',cnt)
        f_out=open(output_file,'a')
    else:
        f_out=open(output_file,'w')


    dataset = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            dataset.append(json.loads(line))
    num = len(dataset)


    if args.sample < 1000:
        dataset = random.sample(dataset,args.sample)

    tracker = AccuracyTracker()
    timeout_seconds = 90
    for id in tqdm(range(start_id,min(num,args.sample))):

        data_each = dataset[id]

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)  

        if args.dataset == "gsm8k":
            message = Solver.solve_text(data_each['problem'])
        else:
            if "robust" in args.dataset.lower():
                message = Solver.solve_table(question=data_each['problem'],table=data_each['table'],format=args.format,with_reject = True)
            else:
                message = Solver.solve_table(question=data_each['problem'],table=data_each['table'],format=args.format)
        print(message)

        try:
            response = chat_model.chat(message)
            ans = chat_model.ans_expr(response)

            record = data_each
            record['response'] = response
            record['prediction'] = ans
            try:
                record['acc'] = is_equiv(ans,str(data_each['target']))
            except:
                record['acc'] = False
            print(record)

            tracker.update(type=data_each.get('type',"well"),acc=record['acc'])       
            f_out.write(json.dumps(record, ensure_ascii=False) + '\n')
            signal.alarm(0)

        except TimeoutException:
            print(f"\nTimeout occurred for id {id}, skipping to next one...")
            continue
        except:
            continue
            
    # acc = sum(results_lst) / len(results_lst)
    type_avg, total_avg = tracker.get_averages()
    logger.info(f"Type Accuracy: {type_avg}")
    logger.info(f"Accuracy: {total_avg}")

# python main_evaluate.py --dataset testau200_Easy
