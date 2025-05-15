from transformers import AutoModelForCausalLM, AutoTokenizer

# Using pandas to read some structured data
import pandas as pd
from io import StringIO
from model.Base import BaseModel

class Llama(BaseModel):
    def __init__(self,model,base_path = "/home/tiansy/4090tiansy/model_download/"):
        if "llama31" in model.lower():
            self.model_name = base_path + "meta-llama/Llama-3___1-8B-Instruct/"
        elif "llama38b" in model.lower():
            self.model_name = base_path + "meta-llama/Meta-Llama-3-8B-Instruct/"
        # elif "l

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def chat(self, my_prompt):

        text = self.tokenizer.apply_chat_template(
            my_prompt, tokenize=False, add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(**model_inputs, max_new_tokens=1024)
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        # print(type(response.choices[0].message))
        return response