import re
import logging
import os
from datetime import datetime
import sys
import json

def is_equiv(answer, solution):
    if answer == "Reject" and solution == "Reject":
        return True
    """ check whether the answer is equivalent to the solution """
    try:
        if eval(f"abs({answer.replace(',','')} - {solution.replace(',','')})") < 1e-5:
            return True
        else:
            return False
    except (SyntaxError, TypeError, NameError):
        return False
    
def parse_answer(sol):
    match = re.search(r'####(.*)', sol)  
    if match:
        return match.group(1)
    else:
        return 0
    
common_names_60 = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "James", "Isabella", "Oliver",
    "Mia", "Benjamin", "Charlotte", "Elijah", "Amelia", "Lucas", "Harper", "Mason", "Evelyn", "Logan",
    "Abigail", "Alexander", "Emily", "Ethan", "Elizabeth", "Jacob", "Avery", "Michael", "Sofia", "Daniel",
    "Ella", "Henry", "Madison", "Jackson", "Scarlett", "Sebastian", "Victoria", "Aiden", "Grace", "Matthew",
    "Chloe", "Samuel", "Camila", "David", "Penelope", "Joseph", "Riley", "Carter", "Layla", "Owen",
    "Zoey", "Wyatt", "Nora", "John", "Lily", "Jack", "Eleanor", "Luke", "Hannah", "Jayden", "Lillian"
]

common_row_ranges = {
    "Age": (20, 75),          # 年龄（成年人范围）
    "Height": (150, 200),     # 身高（cm，正常成人范围）
    "Weight": (40, 100),      # 体重（kg，正常成人范围）
    "BodyTemp": (35, 40),     # 体温（°C，正常范围）
    "HeartRate": (60, 100),   # 心率（次/分钟，静息状态）
    "SleepHours": (4, 10),    # 每日睡眠时长（小时）
}

def setup_logger(experiment_name, log_dir='./logs', level=logging.INFO):
    """
    设置并返回一个配置好的logger对象
    
    参数:
        experiment_name (str): 实验名称，用于日志文件名
        log_dir (str): 日志文件保存目录
        level: 日志级别 (logging.INFO, logging.DEBUG等)
        
    返回:
        logging.Logger: 配置好的logger对象
    """
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger(experiment_name)
    logger.setLevel(level)
    
    # 防止重复添加handler
    if logger.handlers:
        logger.handlers.clear()
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件handler - 将日志写入文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{experiment_name}_{timestamp}.log"
    log_path = os.path.join(log_dir, log_filename)
    file_handler = logging.FileHandler(os.path.join(log_dir, experiment_name + ".log"))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台handler - 将日志输出到控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 记录初始信息
    logger.info(f"Initialized logger for experiment: {experiment_name}")
    logger.info(f"Log file: {log_path}")
    
    return logger

def read_last_line_of_jsonl(file_path):
    """
    逐行读取JSONL文件并返回最后一行
    
    参数:
        file_path (str): JSONL文件路径
        
    返回:
        dict: 最后一行的JSON对象，如果文件为空则返回None
    """
    last_line = None
    cnt = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # 跳过空行
                last_line = line
                cnt+=1
    
    if last_line:
        return json.loads(last_line),cnt
    return None