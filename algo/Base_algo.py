class Base_Solver:
    def __init__(self):
        pass

    def json2se(self,json_data, separator=", "):
        if not json_data or not isinstance(json_data, list):
            return ""
        
        result_lines = []
        
        for item in json_data:
            # 使用原始字段名，按字母顺序排列
            fields = [(k.replace('_#contra', '').title(), str(v)) 
                    for k, v in item.items()]
            
            # 构建键值对字符串
            keyvalue_pairs = [f"{k}: {v}" for k, v in fields]
            line = separator.join(keyvalue_pairs)
            result_lines.append(line)
        
        return "\n".join(result_lines)

    def json2md(self,json_data, column_mapping=None):
        if not json_data or not isinstance(json_data, list):
            return ""
        
        # 获取所有可能的列（取第一个元素的键）
        all_columns = list(json_data[0].keys())
        

        columns = all_columns
        headers = [col.replace('_#contra', '').title() for col in columns]
        
        # 生成表头
        markdown = "| " + " | ".join(headers) + " |\n"
        # 生成分隔线
        markdown += "|" + "|".join(["---"] * len(headers)) + "|\n"
        
        # 生成数据行
        for row in json_data:
            markdown += "| " + " | ".join([
                str(row.get(col, "")) for col in columns
            ]) + " |\n"
        
        return markdown
    
