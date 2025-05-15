import tqdm
import json
from openai import OpenAI
from model.Base import BaseModel

class DeepSeek_API(BaseModel):
    def __init__(self, model="deepseek-chat"):
        self.apikey = "Your_DeepSeek_API_Key"  # Replace with your actual API key
        if model =="deepseekv3":
            self.model = "deepseek-chat"
        elif model =="deepseekr1": 
            self.model= "deepseek-reasoner"
        else:
            raise ValueError
        self.client = OpenAI(api_key=self.apikey, base_url="https://api.deepseek.com/v1")

    def chat(self, my_prompt,format=None):
        """
        Send a prompt to the ChatGLM4 API and return the response.
        """
        response = self.client.chat.completions.create(
        model=self.model,
        messages=my_prompt,
        temperature=0,
        response_format=format
    )

        return response.choices[0].message.content