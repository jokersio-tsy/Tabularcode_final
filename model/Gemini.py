import tqdm
import json
from openai import OpenAI
from model.Base import BaseModel
from zhipuai import ZhipuAI
from model.Base import BaseModel
# import google.generativeai as genai


class Gemini(BaseModel):
    def __init__(self):
        self.api = "Your_Gemini_API_Key"
        # self.client = genai.Client(api_key=self.api)

    def chat(self, my_prompt):
        """
        Send a prompt to the ChatGLM4 API and return the response.
        """

        response = self.client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[''.join(i['content']) for i in my_prompt]
        )
        
        # print(type(response.choices[0].message))
        return response.text