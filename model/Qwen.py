import tqdm
import json
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import AutoTokenizer, AutoModelForCausalLM
from model.Base import BaseModel
import torch
import os

class Qwen(BaseModel):
    def __init__(self, model):
        self.base_path = "/home/tiansy/4090tiansy/model_download/Qwen/"
        if model == "Qwen7b":
            self.model_name = self.base_path + "Qwen2___5-7B-Instruct/"
        elif model == "Qwen14b":
            self.model_name = self.base_path + "Qwen2___5-14B-Instruct/"
        elif model == "Qwen3b":
            self.model_name =  self.base_path + "Qwen2___5-3B-Instruct/"
        elif model == "Qwen32b":
            self.model_name =  self.base_path + "Qwen2___5-32B-Instruct/"
        elif model == "Qwen7bmath":
            self.model_name = self.base_path + "Qwen2___5-Math-7B-Instruct/"
        elif model == "Qwen7bcoder":
            self.model_name = self.base_path + "Qwen2___5-Coder-7B-Instruct/"
        elif model == "Qwen14bcoder":
            self.model_name = self.base_path + "Qwen2___5-Coder-14B-Instruct/"
        else:
            raise ValueError
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def chat(self, my_prompt):
        
        text = self.tokenizer.apply_chat_template(
            my_prompt,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_length = 3000,
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        # print(type(response.choices[0].message))
        return response

    def ans_expr(self,response):
        """
        Input: model response
        Output: model prediction
        """
        import re
        if "unsolvable" in response:
            return "Reject"
        pattern = r'<ans>\s*[^\d]*([\d,]+)\s*<\/ans>'  

        match = re.search(pattern, response)
        if match:
            return match.group(1) # under <ans>/ <ans> format
        # otherwise last int number
        match = re.search(r'(\d+)(?=[^\d]*$)', response)
        last_number = match.group(1) if match else None
        return last_number