from sympy import symbols, parse_expr, solve, minimum, lambdify, Piecewise, floor, binomial, isprime
from sympy import Eq, Le, Lt, asin, acos
from sympy.codegen.cfunctions import log2, log
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from sympy.core import SympifyError
from sympy.polys.polyerrors import NotAlgebraic
from mpmath.libmp.libhyper import NoConvergence
from tokenize import TokenError

import sys
from pysmt.smtlib.parser import SmtLibParser, SmtLibScript
from io import StringIO
from pysmt.shortcuts import Solver, REAL, INT, get_env
from pysmt.exceptions import PysmtValueError, PysmtModeError

import numpy as np
from scipy.optimize import minimize, differential_evolution

class sym_solver:
    def __init__(self):
        self.transformations = (standard_transformations + (implicit_multiplication_application,) + (convert_xor,))
        self.word_dict = {"log": log, "prime": isprime, "log2": log2, "binomial": binomial, 'asin': asin, 'acos': acos}
        self.tol = 1e-6

    def sympy_solve(self, statement):
        self.vars, self.exprs, self.terms = [], [], []
        self.sympy_vars = {}
        id_counter = 0
        self.obj = None
        smt_parser = SmtLibParser()
        try:
            for cmd in smt_parser.get_command_generator(StringIO(statement)):
                # Note: cmd.args[0] is fnode
                if cmd.name == "declare-fun" or cmd.name == "declare-const":
                    tmp_name, tmp_type = cmd.args[0].symbol_name(), cmd.args[0].symbol_type()
                    self.vars.append({'name': tmp_name, 'type': tmp_type, 'id': id_counter})
                    self.sympy_vars[tmp_name] = symbols(tmp_name, real=True)
                    id_counter += 1
                elif cmd.name == "define-fun":
                    continue # ignore it
                elif cmd.name == "assert":
                    ok = self.parse_formula(cmd.args[0])
                    if ok == False: return False, "sympy is still not support this type of expression %s" %(cmd.args[0])
                elif cmd.name == "minimize":
                    ok = self.parse_objective(cmd.args[0], minimize=True)
                    if ok == False: return False, "sympy is still not support this type of expression %s" %(cmd.args[0])
                elif cmd.name == "maximize":
                    ok = self.parse_objective(cmd.args[0], minimize=False)
                    if ok == False: return False, "sympy is still not support this type of expression %s" %(cmd.args[0])
                elif cmd.name == "check-sat":
                    if len(self.vars) == 0: return False, "no vars to be solved"
                    try:
                        if self.obj:
                            sol_res = "infeasible due to the problem is optimization task"
                            ok = False
                        else:
                            solutions = solve(self.exprs, [self.sympy_vars[key] for key in self.sympy_vars.keys()], dict=True)
                            ok, sol_res = self.type_check(solutions)
                    except (NotImplementedError, ValueError, IndexError, NotAlgebraic, NoConvergence) as e:
                        ok, sol_res = False, e
                    if ok == False:
                        ok, solutions = self.optimize()
                        ok, opt_res = self.type_check(solutions)
                    if ok == False: return False, "sympy solve: %s; and sympy opt: %s" %(sol_res, opt_res)
                elif cmd.name == "get-value":
                    try:
                        return True, [self.solution[str(var)] for var in cmd.args]
                    except KeyError as e:
                        return False, "sympy solver fail due to that get-value is not well-formed"
                elif cmd.name == "get-model":
                    return True, [f"{var['name']} := {self.solution[var['name']]}" for var in self.vars]
        except (PysmtValueError, PysmtModeError, ZeroDivisionError, RecursionError) as e:
            return False, "sympy solver fail due to %s" %str(e)
        return False, "the last command in smtlib is not get-value"
    
    def type_check(self, solutions):
        ## may have multiple solutions
        if not isinstance(solutions, list) or len(solutions) == 0: return False, "no solution exists"
        for solution in solutions:
            if len(solution.keys()) != len(self.vars): 
                msg = "the problem cannot be properly solved"
                continue
            valid = True
            final_sol = {}
            for var in self.vars:
                if var['type'] == INT:
                    if self.sympy_vars[var['name']] not in solution: 
                        valid, msg = False, "variable %s is missing" %(var['name'])
                        continue
                    tmp_res = solution[self.sympy_vars[var['name']]]
                    final_sol[var['name']] = str(tmp_res)                        
                    try:
                        if abs(tmp_res - int(tmp_res)) > self.tol:
                            valid, msg = False, "type check fail in %s = %s" %(var['name'], str(tmp_res))
                    except TypeError as e:
                        valid, msg = False, "variable %s is invalid: %s" %(var['name'], str(tmp_res))
                else:
                    tmp_res = solution[self.sympy_vars[var['name']]]
                    final_sol[var['name']] = str(tmp_res)
            if valid:
                self.solution = final_sol
                return True, "solve sucessfully"
        return False, msg
    
    def parse_formula(self, formula):
        try:
            lhs, rhs = formula.args()
            lhs = parse_expr(str(lhs.serialize()), local_dict={**self.sympy_vars, **self.word_dict}, transformations=self.transformations, evaluate=False)
            rhs = parse_expr(str(rhs.serialize()), local_dict={**self.sympy_vars, **self.word_dict}, transformations=self.transformations, evaluate=False)
            if formula.is_equals():
                self.exprs.append(Eq(lhs, rhs))   
                self.terms.append((lhs-rhs)**2) 
                return True    
            elif formula.is_le():
                self.exprs.append(Le(lhs, rhs))
                relu = Piecewise((0, lhs<=rhs), ((lhs-rhs)**2, lhs>rhs))
                self.terms.append(relu)
                return True
            elif formula.is_lt():
                self.exprs.append(Lt(lhs, rhs))   
                relu = Piecewise((0, lhs<=rhs-self.tol), ((lhs-rhs)**2, lhs>rhs-self.tol))
                self.terms.append(relu)
                return True
            # elif formula.is_and():
                # """e.g. lhs = (0 <= final_ahmed); rhs = (final_ahmed <= 100)"""
                # raise NotImplementedError
        except (ValueError, SyntaxError, TypeError, SympifyError, TokenError):
            return False
        return False   
    
    def parse_objective(self, formula, minimize=True):
        sign = 1 if minimize else -1
        try:
            obj = parse_expr(str(formula.serialize()), local_dict={**self.sympy_vars, **self.word_dict}, transformations=self.transformations)
            self.obj = sign * obj
        except (ValueError, SyntaxError):
            return False
        return True
    
    def optimize(self, eps=1e5):
        """build and solve the objective function"""
        num_vars = len(self.vars)
        is_int = False
        for var in self.vars:
            if var['type'] == INT:
                is_int = True
                self.terms.append((self.sympy_vars[var['name']] - floor(self.sympy_vars[var['name']] + 0.5))**2)
        if self.obj:
            sympy_expr = self.obj + eps*sum(self.terms)
            obj = lambdify([self.sympy_vars[key] for key in self.sympy_vars.keys()], self.obj, modules='numpy')
        else:
            sympy_expr = sum(self.terms)
        try:
            loss = lambdify([self.sympy_vars[key] for key in self.sympy_vars.keys()], sympy_expr, modules='numpy')
        except KeyError as e: # KeyError: 'ComplexInfinity' due to zero division
            return False, []
        # wrap the loss function
        def target_func(params): 
            return loss(*params) 
        try:
            if is_int == True:
                with np.errstate(divide='ignore', invalid='ignore'):
                    res = differential_evolution(target_func, maxiter=1000, bounds=[(-100,100) for _ in range(num_vars)], x0=[0.0 for _ in range(num_vars)])
            else:
                with np.errstate(divide='ignore', invalid='ignore'):
                    res = minimize(target_func, x0=[0.0 for _ in range(num_vars)])
        except (TypeError, OverflowError, RuntimeError, ValueError) as e:
            return False, []
        # valid the result
        if self.obj:
            feasibility = res.fun - obj(*res.x)
        else:
            feasibility = res.fun
        if feasibility < self.tol:
            final_sol = {}
            for var in self.vars:
                tol = abs(round(res.x[var['id']]) - res.x[var['id']])
                if var['type'] == INT or tol < self.tol:
                    final_sol[self.sympy_vars[var['name']]] = round(res.x[var['id']])
                else:
                    final_sol[self.sympy_vars[var['name']]] = (res.x[var['id']])
            return True, [final_sol]
        return False, []
    
    
    