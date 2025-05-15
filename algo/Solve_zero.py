from algo.Base_algo import Base_Solver
class Zero_Solver(Base_Solver):
    def __init__(self):
        super(Base_Solver,self).__init__()
        pass
    
    def solve_text(self,question):
        text_system_prompt = "You are an experienced mathematician. Please answer the following math problems. " \
        "You can think about it first and then enter your answer between <ans> </ans>. " 
        text_user_prompt = "Question:{question}"
        message = [
                {'role': "system", "content": text_system_prompt},
                {'role': "user", "content": text_user_prompt.format(question = question)}
                ]
        return message

    def solve_table(self,question,table,format = "se", with_reject = False):
        table_system_prompt = "You are an experienced math teacher. I will give you a math problem and a table. " \
        "This table contains hidden information essential to solving the math problem. Please use the data in the table to solve the problem."  \
        "You can think about it first and then enter your answer between <ans> </ans>. " 

        if with_reject == True:
            table_system_prompt = "You are an experienced math teacher. I will give you a math problem and a table. " \
            "This table contains hidden information essential to solving the math problem. Please use the data in the table to solve the problem."  \
            "These problems may be unsolvable due to conflicting or missing descriptions. " \
            "If you believe the problem cannot be solved, please answer \"This problem is unsolvable\"; otherwise, request a solution to the problem."
            "You can think about it first and then enter your answer between <ans> </ans>. " 
        
        if format == "se":
            table_data = Base_Solver.json2se(self,json_data = table)
        elif format == "md": 
            table_data = Base_Solver.json2md(self,json_data = table)

        table_user_prompt = "Question:{question} \n Table information:{table}"
        message = [
                {'role': "system", "content": table_system_prompt},
                {'role': "user", "content": table_user_prompt.format(question = question,table = table_data)}
                ]
        return message