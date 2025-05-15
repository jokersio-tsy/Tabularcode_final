import tqdm
import json
from openai import OpenAI
from model.Base import BaseModel
from zhipuai import ZhipuAI
from model.Base import BaseModel

class GLM(BaseModel):
    def __init__(self):
        self.api = "Your_GLM_API_Key"  # Replace with your actual API key
        self.client = ZhipuAI(api_key=self.api)
        self.model = "glm-4-plus"


    def chat(self, my_prompt):
        """
        Send a prompt to the ChatGLM4 API and return the response.
        """
        response = self.client.chat.completions.create(
        model=self.model,
        messages=my_prompt,
        do_sample=False
    )
        
        # print(type(response.choices[0].message))
        return response.choices[0].message.content