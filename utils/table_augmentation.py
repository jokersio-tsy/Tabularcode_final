import argparse
import json
from tqdm import tqdm
import random
import datetime
import signal
from model import *
from utils.check import check
from template.generate_temlate import *
from utils.misc import common_names_60,common_row_ranges
from tabulate import tabulate

def shuffle_columns(data):
    if not data:
        return data
    
    # 获取所有键（列名）
    keys = list(data[0].keys())
    # 打乱键的顺序
    random.shuffle(keys)
    
    # 按照新的键顺序重建每个字典
    shuffled_data = []
    for row in data:
        print(row)
        shuffled_row = {key: row[key] for key in keys}
        shuffled_data.append(shuffled_row)
    
    return shuffled_data

def table_augmentation(table_data, args, value_ranges):

    augmented_data= table_data.copy()
    # InfMut
    if args.InfMut != None:
        if args.InfMut == "Missing":
            for row in augmented_data:
                row = augmented_data[0]
                fields = [key for key in row.keys() if key != "name"]
                if fields: 
                    field_to_null = random.choice(fields)
                    row[field_to_null] = None

        if args.InfMut == "Contra":
            # todo
            pass



    # add colume
    if args.RowAug is not None:
        for _ in range(args.RowAug * len(table_data)):
            new_row = {}

            # 处理姓名字段
            if 'name' in table_data[0]:
                new_row['name'] = random.choice(common_names_60)

            for col, col_range in value_ranges.items():
                if col == 'name' or col_range is None:
                    continue

                try:
                    min = col_range.get('min')
                    max = col_range.get('max')
                    if min is None or max is None:
                        continue

                    if isinstance(min, int) and isinstance(max, int):
                        new_row[col] = random.randint(min, max)
                    else:
                        # 尝试转换为浮点数
                        try:
                            min_float = float(min)
                            max_float = float(max)
                            new_row[col] = round(random.uniform(min_float, max_float), 1)  # 一位小数
                            # 如果原始数据是整数，则转为整数
                            if any(isinstance(row.get(col, 0), int) for row in table_data):
                                new_row[col] = int(round(new_row[col]))
                        except (ValueError, TypeError):
                            continue
                except AttributeError:
                    continue

            augmented_data.append(new_row)        


    # add Column
    if args.ColAug is not None:
        existing_columns = set(augmented_data[0].keys())

        # 从 common_row_ranges 的 key 中筛选出不在原表中的列名
        available_columns = [col for col in common_row_ranges.keys() if col not in existing_columns]

        num_new_columns = args.ColAug
        selected_columns = random.sample(available_columns, num_new_columns)

        # 为每一行添加新列，并从 common_row_ranges 的 value 中随机取值
        for row in augmented_data:
            for col in selected_columns:
                min,max = common_row_ranges[col]
                row[col] = random.randint(min,max)
        
    # shuffle
    if args.OrdShf == True:
        random.shuffle(augmented_data)
        augmented_data = shuffle_columns(augmented_data)

    return augmented_data
