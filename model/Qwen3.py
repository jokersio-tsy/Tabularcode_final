import tqdm
import json
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import AutoTokenizer, AutoModelForCausalLM
from model.Base import BaseModel
import torch
import os

class Qwen3(BaseModel):
    def __init__(self, model,enable_thinking=True):
        self.base_path = "/home/tiansy/4090tiansy/model_download/Qwen/"
        if model == "Qwen38b":
            self.model_name = self.base_path + "Qwen3-8B/"
        elif model == "Qwen314b":
            self.model_name = self.base_path + "Qwen3-14B/"
        elif model == "Qwen332b":
            self.model_name = self.base_path + "Qwen3-14B/"
        elif model == "Qwen34b":
            self.model_name = self.base_path + "Qwen3-14B/"
        else:
            raise ValueError
        
        self.enable_thinking=enable_thinking
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
            add_generation_prompt=True,
            enable_thinking=self.enable_thinking
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_length = 3000,
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

        # parsing thinking content
        try:
            # rindex finding 151668 (</think>)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
        print(thinking_content)
        print(content)
        return content

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