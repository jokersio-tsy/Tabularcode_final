class BaseModel():
    """
    A class to interact with chat_model
    """
    def __init__(self, model):
        pass

    def chat(self, my_prompt):
        """
        Input: text prompt 
        Output: model response
        """
        pass

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