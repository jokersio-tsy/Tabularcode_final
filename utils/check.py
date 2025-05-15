import os
import time
import json

from pysmt.smtlib.parser import SmtLibParser
from pysmt.shortcuts import Solver
from io import StringIO
from pysmt.exceptions import PysmtSyntaxError, PysmtTypeError, UnknownSmtLibCommandError

import utils.smt_utils as smt_utils
import utils.misc as utils

error_tuples = (AttributeError, TypeError, AssertionError, PysmtSyntaxError, PysmtTypeError, NotImplementedError, UnknownSmtLibCommandError)

def check(formal_problem, answer = None):
    #start chec
    if formal_problem == "" or formal_problem is None: raise TypeError("no formal problem exists")
    ok, solution = smt_utils.solve(formal_problem)
    if ok == True:
        tmp_sol = ",".join(solution)
    else:
        tmp_sol = "unsat"
    correct = utils.is_equiv(answer, tmp_sol)
    print("###iscorrect",correct)
    print("###solution",solution)
    return tmp_sol,correct

        
                        
