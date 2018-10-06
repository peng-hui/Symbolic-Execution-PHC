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
for k in range(10):
    CstList.append(s)
    Var.append(Real('Var_'+str(k)))#Variable formats as  Var_i

def Function(CstIn):
    # read the cfg in
    script = open('file.txt','r')
    if(script[0:7] != 'Function') 
        return False
    CstOut = CstIn
    Blocks = script.split('\nBlock#')
    # temperally initializa a List for the constraints of each block.

    for i in range(len(Blocks)):
        if( ! uni.isdigit(Block[i][0])):
            continue
        block = Blocks[i].split('\n')
        for j in range(len(block)):
            # handle types with corresponding functions specified
            if block[j] == 'Parent':
                Parent(block[j])
            elif block[j] == 'Expr_Assign':
                Expr_Assign(block[j + 1], block[j + 2], block[j + 3])
            elif block[j] == 'Stmt_Jump':
                Stmt_Jump(block[j+1])
            elif block[j] == 'Terminal_Return':
                Terminal_Return(block[j+1])
            elif(block[j]== 'Expr_Param'):
                Expr_Param(block[j + 1], block[j+2])
                j += 2
            elif block[j] == 'Expr_BinaryOp_Smaller':
                Expr_BinaryOp_Smaller(block[j + 1], block[j + 2], block[j + 3])
                j += 3
            elif block[j] == 'Stmt_JumpIf':
                If_Cst = Stmt_JumpIf(CstList[i],block[j + 1])
                If_block_split = block[j+2].split('Block#')
                CstList[int(If_block_split[1])].add(If_Cst)
                Else_block_split = block[j+3].split('Block#')
                CstList[int(Else_block_split[1])].add(Not(If_Cst))  
            else:
                continue
    return CstOut

def Expr_Param(name, var):
    # here simplly ignore name first
    idx = var.find('<')
    if(idx == -1):
        idx = len(var)
    Var[var[4: idx]] = True
    return


def Expr_BinaryOp_Smaller(left, right, result):
    lidx = left.find('<')
    if(lidx == -1):
        lidx = len(left)
    ridx = right.find('<')
    if(ridx == -1):
        ridx = len(right)
    reidx = result.find('<')
    if(reidx == -1):
        reidx = len(result)
    new_Cst = Var[left[4:lidx]] < Var[right[4:ridx]]
    Var[result[4: reidx]]= new_Cst
    return

'''
This function is to calculate Jump If Conditon
@ param CstIn: Constraint Input
@ param cond: the condition from condition statement, php-cfg
@ return New_Cst: return the New Constraints of If statement
'''
def JumpIfCond(CstIn,cond):
    idx = cond.find('<')
    if(idx == -1):
        idx = len(cond)
    Var_idx = int(cond[4:idx])
    new_Cst = CstIn And Var[Var_idx] != 0
    return new_Cst
