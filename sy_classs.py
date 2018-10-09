#!/usr/bin/python
'''
@ file: This is a simple draft of symbolic execution with PHP, which 
        uses the CFG from php-cfg.
'''
from z3 import *
import unicodedata as uni
import os

# TODO Other nodes that have to be handled
# TODO Identify LOOPs(Path goes from smaller node to larger one??)
# TODO Support user input identifycation, which should be in Array_Fetch #      But how to mark it when analysize the loop condition?
# TODO Where to start???
# TODO Identify which path is reachable there.

class ParseFunc(object):
    BlockPath = []
    CstList = []
    Var = []
    Parents = []
    block = []
    #read script and read it into blocks
    def __init__(self, script):
        Blocks = script.split('\nBlock#')
        for i in range(len(Blocks)):
            self.block.append(Blocks[i].split('\n'))
            self.BlockPath.append([])
            self.Parents.append([])
            s = Solver()
            self.CstList.append(s)
        return

    def TravelBlock(self, nblock):
        self.BlockPath[nblock].append(nblock)
        #print('path',nblock, self.BlockPath[nblock])
        block = self.block[nblock]
        j = 1
        while j < len(block):
            # handle types with corresponding functions specified
            block[j] = block[j].strip() 
            if block[j].isdigit():
                print('Begin to travel block', block[j])
            elif block[j].find('Parent') != -1:
                self.Parents[nblock].append(int(block[j][14:]))
                #self.Parents[nblock].append(self.Parent(block[j][8:])) # nothing with parent, not deal with it at this moment.
            elif block[j] == 'Expr_Assign':
                self.Expr_Assign(block[j + 1].strip()[5:], block[j + 2].strip()[6:], block[j + 3].strip()[8:])
                j += 3
            elif block[j] == 'Stmt_Jump': 
                self.CstList[int(block[j+1].strip()[14:])].add(self.CstList[nblock].assertions())
                self.BlockPath[int(block[j+1].strip()[14:])] = self.BlockPath[nblock][:]
                self.TravelBlock(int(block[j+1].strip()[14:])) # there may be a loop
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
                self.CstList[int(If_block_split[1])].add(self.CstList[nblock].assertions())
                self.CstList[int(If_block_split[1])].add(If_Cst) #need to add current cst
                Else_block_split = block[j+3].split('Block#')
                self.CstList[int(Else_block_split[1])].add(self.CstList[nblock].assertions())
                self.CstList[int(Else_block_split[1])].add(Not(If_Cst)) #need to add current cst
                ###########
                #self.BlockPath[int(If_block_split[1])] = self.BlockPath[nblock][:]
                #self.TravelBlock(int(If_block_split[1]))

                pid = os.fork()
                if pid == 0:
                    self.BlockPath[int(If_block_split[1])] = self.BlockPath[nblock][:]
                    self.TravelBlock(int(If_block_split[1]))
                else:
                    self.BlockPath[int(Else_block_split[1])] = self.BlockPath[nblock][:]
                    self.TravelBlock(int(Else_block_split[1]))
                j += 3
            elif block[j] == 'Expr_BinaryOp_Plus':
                self.Expr_BinaryOp_Plus(block[j + 1].strip()[6:], block[j + 2].strip()[7:], block[j + 3].strip()[8:])
                j += 3
            elif block[j].find('Phi') != -1:
                self.Phi(block[j].strip())# deal with all stuff with function phi
            else:
                print("ERROR: unknown expr/stmt")
                #print(block[j])
            j +=1

    '''
    @ function: this is to deal with array fetch in php
    '''
    def Expr_ArrayDimFetch(self, var, dim, result):
        return var[dim]

    '''
    @function:      Find the parental node
    @param pblock:  Parent block
    @return:        parental block number
    '''
    def Parent(self, pblock):
        return int(pblock[6:])

    '''
    @ function Phi is the joining point in the control flow graph.
               It requires to handle more than two inputs from its
               parents and output the final result with a new variable
    @ param expr: the expression that contains the parental variables
    @ return:  NULL
    it needs to write the result in the CstList and Varaible
    '''
    # TODO
    def Phi(self, expr):
        nvar = expr.split('Var#')
        r1 = nvar[1].find('<') 
        r2 = nvar[1].find('=')
        kk = 0
        if r1 == -1:
            kk = r2
        else: 
            kk = r1 
        reidx = int(nvar[1][0:kk])
        self.Assign_Element(self.Var, reidx, '')
        i = 1
        while i < len(nvar):
            rt1 = nvar[i].find('<')
            rt2 = len(nvar[i])
            if rt1 == -1:
                kk = rt2 -2
            else:
                kk = rt1
            rtidx = int(nvar[i][0:kk])
            if type(self.Var[rtidx]) != str: # here needsed to assin value to new var, but cannot 
                                             # compare str with symbolic expressions
                self.Var[reidx] = self.Var[rtidx]
                return
            i +=1
        print('ERROR: PHI Var[%d] not initialized', reidx)
        return

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
        new_Cst = lvalue + rvalue
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
            List.append('')
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
        self.Assign_Element(self.Var, int(var[4:vidx]),evalue)
        self.Assign_Element(self.Var, int(result[4: reidx]), evalue) # result is equal to var
        return

    # TODO?? seems if initialize at the beginning, then not necessary to do anything here.
    def Expr_Param(self, name, var):
        idx = var.find('<')
        if(idx == -1):
            idx = len(var)
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

        new_Cst = lvalue < rvalue
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
        return new_Cst 


# run here
script = open('file.txt','r')
script = script.read()
start = ParseFunc(script)
start.TravelBlock(1)
for i in range(len(start.BlockPath)):
    print(i, ':')
    print('BlockPath:', start.BlockPath[i])
    print('CstList:', start.CstList[i])

