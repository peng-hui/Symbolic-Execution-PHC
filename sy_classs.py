#!/usr/bin/python
'''
@ file: This is a simple draft of symbolic execution with PHP, which 
        uses the CFG from php-cfg.
'''
from z3 import *
import unicodedata as uni

# class SEFunction: which can be put off since now we only focus on single function
# TODO set a class to it
# TODO Other nodes that have to be handled
# TODO United Nodes and function 'Phi'
# TODO Identify LOOPs(Path goes from smaller node to larger one??)
# TODO Support user input identifycation, which should be in Array_Fetch
#      But how to mark it when analysize the loop condition?
# TODO Where to start???
# TODO Identify which path is reachable there.

class ParseFunc(object):
    ReachNode = []
    NodePath = []
    CstList = []
    Var = []
    Parents = []
    block = []
    #read script and read it into blocks
    def __init__(self, script):
        Blocks = script.split('\nBlock#')
        for i in range(len(Blocks)):
            self.block.append(Blocks[i].split('\n'))
        return

    def TravelBlock(self, nblock):
        block = self.block[nblock]
        for j in range(len(block)):
            # handle types with corresponding functions specified
            block[j] = block[j].strip() 
            if block[j].isdigit():
                print('Begin to travel block', block[j])
            elif block[j].find('Parent') != -1:
                abf = 1
                #self.Parents[nblock].append(self.Parent(block[j][8:])) # nothing with parent, not deal with it at this moment.
            elif block[j] == 'Expr_Assign':
                self.Expr_Assign(block[j + 1].strip()[5:], block[j + 2].strip()[6:], block[j + 3].strip()[8:])
                j += 3
            elif block[j] == 'Stmt_Jump': 
                self.Stmt_Jump(block[j+1].strip()[8:], nblock) # there may be a loop
                j += 1
            elif block[j] == 'Terminal_Return':
                self.Terminal_Return(block[j+1].strip()[6:])
                j += 1
            elif(block[j]== 'Expr_Param'):
                self.Expr_Param(block[j+1].strip()[6:], block[j+2].strip()[8:])
                j += 2
            elif block[j] == 'Expr_BinaryOp_Smaller':
                self.Expr_BinaryOp_Smaller(block[j + 1].strip()[6:], block[j + 2].strip()[7:], block[j + 3].strip()[8:])
                j += 3
            elif block[j] == 'Stmt_JumpIf':
                tmp = block[j+1].strip()[6:]
                If_Cst = self.JumpIfCond(tmp)
                If_block_split = block[j+2].split('Block#')
                #self.CstList[int(If_block_split[1])].add(If_Cst)
                self.TravelBlock(int(If_block_split[1]))
                Else_block_split = block[j+3].split('Block#')
                #self.CstList[int(Else_block_split[1])].add(Not(If_Cst))  
                self.TravelBlock(int(Else_block_split[1]))
                j += 3
            elif block[j] == 'Expr_BinaryOp_Plus':
                self.Expr_BinaryOp_Plus(block[j + 1].strip()[6:], block[j + 2].strip()[7:], block[j + 3].strip()[8:])
                j += 3
            elif block[j].find('Phi') != -1:
                a = 1 # make space
                #CstList[i].add(Phi(block[j], i)) # deal with all stuff with function phi
                # this function may be complex since it should combine the constraints together to the next variable
                # something need to do here
            else:
                print("ERROR: unknown expr/stmt")
                print(block[j])
    '''
        for i in range(len(Blocks)):
            print('Block', i)
            print(CstList[i])
            print(CstList[i].check())
            if(CstList[i].check()):
                ReachNode[i] = True
                print(CstList[i].model())
    '''

    '''
    @ function: this is to deal with array fetch in php
    '''
    def Expr_ArrayDimFetch(self, var, dim, result):
        return
    '''
    @function:      Find the parental node
    @param pblock:  Parent block
    @return:        parental block number
    '''
    def Parent(self, pblock):
        return int(pblock[6:])

    # TODO
    '''
    Generally, Stmt_Jump happens when there is a loop...
    '''
    def Stmt_Jump(self, target, nblock):
        target = int(target[6:])
        #if(target in self.NodePath[nblock]):
        #    self.NodePath[nblock].append(target)
        #    print('There is a LOOP:', self.NodePath) # need to mark
        return
    '''
    @ function Phi is the joining point in the control flow graph.
               It requires to handle more than two inputs from its
               parents and output the final result with a new variable
    @ param expr: the expression that contains the parental variables
    @ return:  NULL
    it needs to write the result in the CstList and Varaible
    '''
    # TODO
    def Phi(self, expr, nblock):
        return
        '''
        r1 = expr.find('<') 
        r2 = expr.find('=')
        r = min(r1, r2-1) # there is a space for r2
        reidx = int(expr[4:r])
        left = expr[r2+6: expr.find(',')]
        #print('left', left)
        right = expr[expr.find(',') + 2 : ]
        #print('right', right)
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

        cst = False
        for i in range(len(Parents[nblock])):
            tcst = True
            for c in CstList[Parents[nblock][i]].assertions():
                tcst = And(tcst, c)
            cst = Or(cst,tcst)
        return cst
        '''

    '''
    @function:      return expression or value
    @param expr:    expression
    @return:        NULL
    '''
    def Terminal_Return(self, expr):
        evalue = 'error'
        if expr.find('Var') != -1:
            eidx = expr.find('<') 
            if(eidx == -1):
                eidx = len(expr)
            evalue = self.Var[int(expr[4:eidx])]
        elif expr.find('LITERAL') != -1:
            eidx = expr.find(')')
            evalue = int(expr[8:eidx])
        return evalue
    '''
    @function:      ADD
    @param left:    left param
    @param right:   right param
    @param result:  result
    '''
    def Expr_BinaryOp_Plus(self, left, right, result):
        lvalue = 'error'
        rvalue = 'error'
        if(left.find('Var') != -1):
            lidx = left.find('<') 
            if(lidx == -1):
                lidx = len(left) 
            lvalue = self.Var[int(left[4:lidx])]
        elif(left.find('LITERAL')!= -1):
            lidx = left.find(')')
            lvalue = int(left[8:lidx])

        if(right.find('Var') != -1):
            ridx = right.find('<') 
            if(ridx == -1):
                ridx = len(right) 
            rvalue = self.Var[int(right[4:ridx])]
        elif(right.find('LITERAL')!= -1):
            ridx = right.find(')')
            rvalue = int(right[8:ridx])
        reidx = result.find('<') 
        if(reidx == -1):
            reidx = len(result)

        n = int(result[4:reidx])
        #print(left, right, result)
        #print(lidx, ridx, reidx)
        new_Cst = lvalue + rvalue
        #print('new_Cst',new_Cst)
        self.Assign_Element(self.Var, n, new_Cst)
        #self.Var[n]= new_Cst
        return
    '''
    @function:      assign to variables
    @param var:     
    @param expr:
    @param result:
    '''
    def Assign_Element(self, List, index, value):
        i = len(List)
        n = index
        while i < n:
            List.append(' ')
            i += 1
        List.append(value)
        return
        
        
    def Expr_Assign(self, var, expr, result):
        evalue = 'error'
        if expr.find('Var') != -1:
            eidx = expr.find('<') 
            if(eidx == -1):
                eidx = len(expr)
            evalue = self.Var[int(expr[4:eidx])]
        elif expr.find('LITERAL') != -1:
            eidx = expr.find(')')
            evalue = int(expr[8:eidx])
        vidx = var.find('<') 
        if(vidx == -1):
            vidx = len(var) 
        reidx = result.find('<') 
        if(reidx == -1):
            reidx = len(result)
        n = int(result[4:reidx])
        i = len(self.Var)
        while i < n + 1 :
            self.Var.append(Real('Var' + str(i)))
            i += 1
        #print(expr, evalue)
        self.Assign_Element(self.Var, int(var[4:vidx]),evalue)
        self.Assign_Element(self.Var, int(result[4: reidx]), evalue) # result is equal to var
        return

    # TODO?? seems if initialize at the beginning, then not necessary to do anything here.
    def Expr_Param(self, name, var):
        idx = var.find('<')
        if(idx == -1):
            idx = len(var)
        print(idx, '\n')
        print(var)
        n = int(var[4:idx])
        self.Assign_Element(self.Var, n, Real('Var'+str(n)))
        return
    '''
    compare
    '''
    def Expr_BinaryOp_Smaller(self, left, right, result):
        lvalue = 'error'
        rvalue = 'error'
        if(left.find('Var') != -1):
            lidx = left.find('<') 
            if(lidx == -1):
                lidx = len(left) 
            lvalue = self.Var[int(left[4:lidx])]
        elif(left.find('LITERAL')!= -1):
            lidx = left.find(')')
            lvalue = int(left[8:lidx])

        if(right.find('Var') != -1):
            ridx = right.find('<') 
            if(ridx == -1):
                ridx = len(right) 
            rvalue = self.Var[int(right[4:ridx])]
        elif(right.find('LITERAL')!= -1):
            ridx = right.find(')')
            rvalue = int(right[8:ridx])
        reidx = result.find('<') 
        if(reidx == -1):
            reidx = len(result)
        n = int(result[4:reidx])

        #print(left, right, result)
        #print(lidx, ridx, reidx)
        new_Cst = lvalue < rvalue
        #print('new_Cst',new_Cst)
        #self.Var[int(result[4: reidx])]= new_Cst
        self.Assign_Element(self.Var, n, new_Cst)
        return

    '''
    This function is to calculate Jump If Conditon
    @ param CstIn: Constraint Input
    @ param cond: the condition from condition statement, php-cfg
    @ return New_Cst: return the New Constraints of If statement
    '''

    def JumpIfCond(self, cond):
        idx = cond.find('<')
        if(idx == -1):
            idx = len(cond)
        Var_idx = int(cond[4:idx])
        new_Cst = self.Var[Var_idx]
        #print(new_Cst, type(new_Cst))
        return new_Cst 


# run here
script = open('file.txt','r')
script = script.read()
start = ParseFunc(script)
start.TravelBlock(0)
start.TravelBlock(1)