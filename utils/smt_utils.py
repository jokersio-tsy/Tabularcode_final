from io import StringIO
import z3

from pysmt.smtlib.parser import SmtLibParser, SmtLibScript
from io import StringIO
from pysmt.shortcuts import Solver
from pysmt.exceptions import UnsupportedOperatorError, ConvertExpressionError, NonLinearError
from pysmt.exceptions import PysmtValueError, PysmtModeError, InternalSolverError
from pysmt.exceptions import NoSolverAvailableError, SolverReturnedUnknownResultError

from multiprocessing import Pool, TimeoutError

from utils.solver import sym_solver

errors = (UnsupportedOperatorError, ConvertExpressionError, NonLinearError, \
            SolverReturnedUnknownResultError, InternalSolverError, IndexError, AttributeError, ValueError, ZeroDivisionError)

def pysmt_solver(statement, solver_name='z3'):
    smt_parser = SmtLibParser()
    smt_parser.env.enable_div_by_0 = False
    try:
        script = smt_parser.get_script(StringIO(statement))  
    except (ZeroDivisionError, NotImplementedError, AssertionError, TypeError) as e:
        return False, f"Parse error: {e}"
    
    Opt = Solver
    try:
        with Opt(name=solver_name) as opt:
            logs = script.evaluate(opt)
        if len(logs) == 0: return False, "no results"
        cmd, res = logs[-1] 
        if cmd == "get-value":
            return (True, [str(res[key]).replace("?", "") for key in res]) 
        elif cmd == "get-model":
            res = str(res).replace("?", "").split('\n') # remove ? in the model
            return (True, res)
        else:
            (False, "the last command in smtlib is not get-value or get-models")  
    except Exception as e:
        return False, f"Solver error: {e.__class__.__name__} {e}"

def solve(statement, sympy=True, verbose=False):
    pool = Pool(4)
    future_res = {}
    solver_res = {}
    smt_solvers = ["z3", "cvc4", "msat"]
    if sympy: 
        sym_solvers = ["sympy"] 
    else: 
        sym_solvers = []
    try:
        for s in smt_solvers:
            tmp_solver = pool.apply_async(pysmt_solver, (statement, s))
            future_res[s] = tmp_solver
        for s in sym_solvers:
            tmp_solver = pool.apply_async(sym_solver().sympy_solve, (statement,))
            future_res[s] = tmp_solver
        for s in smt_solvers + sym_solvers:
            try:
                ok, res = future_res[s].get(10)
            except (TimeoutError, KeyError, PysmtValueError, PysmtModeError, Exception) as e:
                ok, res = False, f"{e.__class__.__name__}: {str(e)}"
            solver_res[s] = res
            if verbose: print(s, ok, res)
            if ok == True: 
                break
    finally:
        pool.terminate()
        pool.join()

    if ok == True: # if solved, only return the res
        return ok, res
    else:
        return ok, solver_res



