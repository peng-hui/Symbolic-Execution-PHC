#!/usr/bin/python
from z3 import *
import unicodedata as uni
'''
# @CstList set the list of Solvers which store the constraints
# each time when update the solver, just And the existing condition
# then x
'''
CstList = []
s = Solver()
s.add(True)
Var = []
Parents = []
for k in range(10):
    s = Solver()
    s.add(True)
    CstList.append(s)
    Var.append(Real('var' + str(k)))#Variable formats as  Var_i
    Parents.append([])
    #print( Var[k], type(Var[k]))

def Function(CstIn):
    # read the cfg in
    script = open('file.txt','r')
    script = script.read()
    #print(script)
    if(script[0:8] != 'Function') :
        print('not function\n')
        print(script[0:8])
        return False
    CstOut = CstIn
    Blocks = script.split('\nBlock#')
    # temperally initializa a List for the constraints of each block.
    #print(len(Blocks))
    i = 1
    while i < len(Blocks):
        #print('Reach the first loop\n')
        block = Blocks[i].split('\n')
        i += 1
        print(len(block))
        j = 0
        while j  < len(block):
            # handle types with corresponding functions specified
            #print('Reach the second loop\n')
            block[j] = block[j].strip()
            if block[j].isdigit():
                print('Begin of block')
            elif block[j].find('Parent') != -1:
                Parents[i -1].append(Parent(block[j][8:])) # nothing with parent, not deal with it at this moment.
            elif block[j] == 'Expr_Assign':
                Expr_Assign(block[j + 1].strip()[5:], block[j + 2].strip()[6:], block[j + 3].strip()[8:])
                j += 3
            elif block[j] == 'Stmt_Jump':
                Stmt_Jump(block[j+1])
                j += 1
            elif block[j] == 'Terminal_Return':
                Terminal_Return(block[j+1].strip()[6:])
                j += 1
            elif(block[j]== 'Expr_Param'):
                block[j+1] = block[j+1].strip()
                block[j+2] = block[j+2].strip()
                name = block[j+1][6:]
                var = block[j+2][8:]
                Expr_Param(name, var)
                j += 2
            elif block[j] == 'Expr_BinaryOp_Smaller':
                Expr_BinaryOp_Smaller(block[j + 1].strip()[6:], block[j + 2].strip()[7:], block[j + 3].strip()[8:])
                j += 3
            elif block[j] == 'Stmt_JumpIf':
                tmp = block[j+1].strip()[6:]
                If_Cst = JumpIfCond(tmp)
                If_block_split = block[j+2].split('Block#')
                CstList[int(If_block_split[1])].add(If_Cst)
                Else_block_split = block[j+3].split('Block#')
                CstList[int(Else_block_split[1])].add(Not(If_Cst))  
                j += 3
            elif block[j] == 'Expr_BinaryOp_Plus':
                Expr_BinaryOp_Plus(block[j + 1].strip()[6:], block[j + 2].strip()[7:], block[j + 3].strip()[8:])
                j += 3
            elif block[j].find('Phi') != -1:
                Phi(block[j]) # deal with all stuff with function phi
                # this function may be complex since it should combine the constraints together to the next variable
            else:
                print("ERROR: unknown expr/stmt")
                print(block[j])
            j += 1
                
    for i in range(len(Blocks)):
        print(CstList[i], Parents[i])
    return CstOut

def Parent(pblock):
    return int(pblock[6:])

def Stmt_Jump(target):
    return

def Phi(expr):
    r1 = expr.find('<') 
    r2 = expr.find('=')
    r = min(r1, r2-1) # there is a space for r2
    reidx = int(expr[4:redix])
    left = expr[r2+2: expr.find(',')]
    right = expr[expr.find(',') + 1 : ]
    return

def Terminal_Return(expr):
    evalue = 'error'
    if expr.find('Var') != -1:
        eidx = expr.find('<') 
        if(eidx == -1):
            eidx = len(expr)
        evalue = Var[int(expr[4:eidx])]
    elif expr.find('LITERAL') != -1:
        eidx = expr.find(')')
        evalue = int(expr[8:eidx])
    return evalue

def Expr_BinaryOp_Plus(left, right, result):
    lvalue = 'error'
    rvalue = 'error'
    if(left.find('Var') != -1):
        lidx = left.find('<') 
        if(lidx == -1):
            lidx = len(left) 
        lvalue = Var[int(left[4:lidx])]
    elif(left.find('LITERAL')!= -1):
        lidx = left.find(')')
        lvalue = int(left[8:lidx])

    if(right.find('Var') != -1):
        ridx = right.find('<') 
        if(ridx == -1):
            ridx = len(right) 
        rvalue = Var[int(right[4:ridx])]
    elif(right.find('LITERAL')!= -1):
        ridx = right.find(')')
        rvalue = int(right[8:ridx])
    reidx = result.find('<') 
    if(reidx == -1):
        reidx = len(result)
    #print(left, right, result)
    #print(lidx, ridx, reidx)
    new_Cst = lvalue + rvalue
    print('new_Cst',new_Cst)
    Var[int(result[4: reidx])]= new_Cst
    return
    
def Expr_Assign(var, expr, result):
    evalue = 'error'
    if expr.find('Var') != -1:
        eidx = expr.find('<') 
        if(eidx == -1):
            eidx = len(expr)
        evalue = Var[int(expr[4:eidx])]
    elif expr.find('LITERAL') != -1:
        eidx = expr.find(')')
        evalue = int(expr[8:eidx])

    vidx = var.find('<') 
    if(vidx == -1):
        vidx = len(var) 
    reidx = result.find('<') 
    if(reidx == -1):
        reidx = len(result)

    print(expr, evalue)
    Var[int(var[4:vidx])]  = evalue
    Var[int(result[4: reidx])]= Var[int(var[4:vidx])] # result is equal to var
    return

def Expr_Param(name, var):
    # here simplly ignore name first
    return
'''
    idx = var.find('<')
    if(idx == -1):
        idx = len(var)
    print(idx, '\n')
    print(var)
    n = int(var[4:idx])
    Var[n] = Real('Var' + str(n))
    return
'''


def Expr_BinaryOp_Smaller(left, right, result):
    lvalue = 'error'
    rvalue = 'error'
    if(left.find('Var') != -1):
        lidx = left.find('<') 
        if(lidx == -1):
            lidx = len(left) 
        lvalue = Var[int(left[4:lidx])]
    elif(left.find('LITERAL')!= -1):
        lidx = left.find(')')
        lvalue = int(left[8:lidx])

    if(right.find('Var') != -1):
        ridx = right.find('<') 
        if(ridx == -1):
            ridx = len(right) 
        rvalue = Var[int(right[4:ridx])]
    elif(right.find('LITERAL')!= -1):
        ridx = right.find(')')
        rvalue = int(right[8:ridx])
    reidx = result.find('<') 
    if(reidx == -1):
        reidx = len(result)
    #print(left, right, result)
    #print(lidx, ridx, reidx)
    new_Cst = rvalue < rvalue
    print('new_Cst',new_Cst)
    Var[int(result[4: reidx])]= new_Cst
    return

'''
This function is to calculate Jump If Conditon
@ param CstIn: Constraint Input
@ param cond: the condition from condition statement, php-cfg
@ return New_Cst: return the New Constraints of If statement
'''
def JumpIfCond(cond):
    idx = cond.find('<')
    if(idx == -1):
        idx = len(cond)
    Var_idx = int(cond[4:idx])
    new_Cst = Var[Var_idx]
    print(new_Cst, type(new_Cst))
    return new_Cst

Function(True)
