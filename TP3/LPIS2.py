
from tkinter.tix import Tree
from lark import Discard
from lark import Lark,Token
from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
import graphviz

import geraHTML as html

# Note que a nova vers ̃ao dessa linguagem, que ser ́a designada por LPIS2, deve permitir declarar vari ́aveis at ́omicas e
# estruturadas (incluindo como no Python as estruturas: conjunto, lista, tuplo, dicionario), instru ̧c ̃oes condicionais e
# pelo menos 3 variantes de ciclos.

class MyInterpreter (Interpreter):
    
    def varStatus(self, DEC = 0, ND = False, UNI = False, DN = False):
        return {"DEC" : DEC, "ND" : ND, "UNI" : UNI, "DN" : DN}

    def geraCodigoLivre(self, dicionario):
        string = ""
        if(type(dicionario) == dict):
            if dicionario["type"] == "if":
                string += "if(" + dicionario["cond"] + "){\n"
            elif dicionario["type"] == "while":
                string += "while(" + dicionario["cond"] + "){\n"
            for elem in dicionario["inst"]:
                string += self.geraCodigoLivre(elem)
            string += "};\n"
        elif(type(dicionario) == list):
            for elem in dicionario:
                string += elem + ";\n"
        else:
            string += dicionario + ";\n"
        return string

    def geraCodigoSimples(self, dicionario):
        while dicionario["type"] == "if" and dicionario["inst_type"][0] == "conditional":
            dicionario["cond"] += " and " + dicionario["inst"][0]["cond"]
            dicionario["inst_type"] = dicionario["inst"][0]["inst_type"]
            dicionario["inst"] = dicionario["inst"][0]["inst"]
        return self.geraCodigoLivre(dicionario)


    # DEC: valor numérico de declarações 
    # ND: Não declarada 
    # UNI : Usada mas Não Inicializada 
    # DN : Declarada, mas não usada

    def __init__(self):
        self.graph = graphviz.Digraph('graph', filename='graph.gv')
        self.status = {'if': 0, 'ifs' : 0, 'if_start' : 0}
        self.last = 'inicio'
        self.variaveis = {}  # {var: {DEC: 0, ND:False, UNI:True, DN:False}} DEC: # de declarações | ND: Não declarada | UNI : Usada mas Não Inicializada | DN : Declarada, mas não usada
        self.totVarsDec = 0
        self.totEstruturas = {"dicts" : 0, "listas" : 0, "tuplos" : 0, "conjuntos" : 0}
        self.totInst = {"atribuicao" : 0, "rw" : 0, "cond" : 0, "ciclo" : 0 }
        self.totEstruturasAninh = {"mm" : 0, "dif" : 0}
        self.controloAninh = {} # {ifAninhado : ifSolo}

    def start(self,tree):
        self.visit(tree.children[0])
        data = {}
        data["vars"] = self.variaveis
        data["#varsDec"] = self.totVarsDec
        data["#estruturas"] = self.totEstruturas
        data["#inst"] = self.totInst
        data["#estruturasAninh"] = self.totEstruturasAninh
        data["estruturasAninhadas"] = self.controloAninh
        self.graph.edge(self.last,'fim')
        self.graph.render(directory='graphs',view=False)
        #self.graph.view()
        return data

    def atribuicao(self, tree):
        # atribuicao : VAR "=" define
        q = tree.children[0]
        next = self.visit(tree.children[1])
        if q not in self.variaveis.keys():
            self.variaveis[str(q)] = self.varStatus(ND = True)
        else: 
            self.variaveis[str(q)]["DN"] = False
        return str(q) + ' = ' + str(next)
        
    # CICLOS


    def ciclos(self, tree):
        dicionario = self.visit(tree.children[0])[1]
        if 'conditional' in dicionario["inst_type"]:
            self.totEstruturasAninh["dif"] += 1
        elif 'ciclo' in dicionario["inst_type"]:
            self.totEstruturasAninh["mm"] += 1
        return dicionario,tree

    def ciclo1(self, tree):
        # "while" "(" condition ")" "{" instrucoes "}"
        var = self.visit_children(tree)
        return tree,{ "type" : "while", "cond" : var[0], "inst_type":var[1][0], "inst" : var[1][1]}
    
    def ciclo2(self,tree):
        # "repeat" "{" instrucoes "}" "until" "(" condition ")"
        var = self.visit_children(tree)
        return tree,{ "type" : "reapeat", "cond" : var[1], "inst_type":var[0][0], "inst" : var[0][1]}
    
    def ciclo3(self,tree):
        #"for" "(" (declare | atribuicao )? ";" condition ";" atribuicao? ")" "{" instrucoes "}"
        var = self.visit_children(tree)
        return tree,{ "type" : "for", "cond" : var[1], "inst_type":var[3][0], "inst" : var[3][1]}


    # CONDICIONAL LOGIC

    def condition(self, tree): 
        #     condition "and" condition2
        #   | condition2
        q = tree.children
        if len(q) == 1:
            return self.visit(q[0])
        else:
            return self.visit(q[0]) + ' and ' + self.visit(q[1])

    def condition2(self,tree):
        # condition2 "or" condition3
        # | condition3
        q = tree.children
        if len(q) == 1:
            return self.visit(q[0])
        else:
            return self.visit(q[0]) + ' or ' + self.visit(q[1])

    def condition3(self, tree): 
        # "(" condition ")"
        #    | exprel
        #    | "!" condition 
        q = tree.children
        return self.visit(q[0])

    # CONDITIONAL 

    def conditional(self, tree):
        # "if" "(" condition ")" "{" instrucoes "}" ("else" "{" instrucoes "}")?
        
        return tree

    def conta(self, tree):
        # conta : valor TIMES valor
        #       | valor DIV valor
        #       | valor MOD valor 
        #       | valor
        q = self.visit_children(tree)
        
        if len(q) == 1:
            return str(q[0])
        elif q[1].type == "TIMES":
            return str(q[0]) + '*' + str(q[2])
        elif q[1].type == "DIV":
            return str(q[0]) + '/' + str(q[2]) 
        elif q[1].type == "MOD":
            return str(q[0]) + '%' + str(q[2]) 
    


    def declare(self,tree):
        #   "var" atribuicao
        # | "var" VAR
        self.totVarsDec += 1
        var = tree.children[0]
        if not isinstance(var, Token):
            q = self.visit(var)
            var = q.split(' =')[0]
            self.totInst["atribuicao"] += 1
            if var not in self.variaveis.keys():
                self.variaveis[var] = self.varStatus(DEC=1)
            else: 
                self.variaveis[var]["DEC"] += 1
                self.variaveis[var]["ND"] = False
                self.variaveis[var]["UNI"] = False
        elif var not in self.variaveis.keys():
            self.variaveis[str(var)] = self.varStatus(DEC=1, DN = True)
        else:
            self.variaveis[str(var)]["DEC"] += 1

        return 'var ' + str(var)


    def define(self,tree):
        #      expression
        #    | estruturas
        #    | input
        #    | INT
        #    | STRING
        q = tree.children[0]
        if isinstance(q,Token):
            if q.type == "INT":
                return int(q)
            else:
                string = str(q)
                return string
        else:
            return self.visit(q)

    def dicionario(self,tree):
        var = self.visit_children(tree)
        
        dicionarios = {}
        for i in range(0, len(var), 2):
            dicionarios[var[i]] = var[i+1]
        self.totEstruturas["dicts"] += 1
        return dicionarios
        
    def estruturas(self, tree):
        return self.visit(tree.children[0])

    def exprel(self, tree):
        # expression oprel expression
        var = self.visit_children(tree) 
        return var[0] + " "+ str(var[1][0]) + " " + var[2]

    def expression(self,tree):
        #      expression PLUS conta
        #    | expression MINUS conta
        #    | conta
        q = self.visit_children(tree)
        if len(q) == 1:
            return str(q[0])
        else:
            if q[1].type == 'PLUS':
                return str(q[0]) + '+' + str(q[2])
            else:
                return str(q[0]) + '-' + str(q[2])

    def input(self,tree):
        self.totInst["rw"]+=1
        return "input()"


# self.status = {'last': 'inicio','if': 0,'isIf': False }
    def instrucao(self,tree):

        q = tree.children[0]
        
        if q.data == 'atribuicao':
            print("att")
            var = self.visit(tree.children[0])
            self.graph.edge(self.last, var)
            self.last = var
            self.totInst["atribuicao"]+=1
            #if (self.status['isIf']): print("IF HERE")
            # self.graph.edge(self.status['last'],var)
            self.status['last'] = var
            # print("atribuicao", var)
            return ("atribuicao", var)

        if q.data == 'conditional':
            print("cond")
            self.status["if"] += 1
            self.status["ifs"] += 1

            teste = self.visit(tree.children[0])
            #print("conditional")
            #print(teste)
           # print(teste)
            cond = self.visit(teste.children[0])
            #print(cond)
            self.graph.edge(self.last, 'if ' + cond)
            self.last = 'if ' + cond
            inst_type = self.visit(teste.children[1])
            self.graph.edge('if ' + cond, "fi" + str(self.status["if"]))
            
            self.graph.edge(self.last, "fi" + str(self.status["if"]))
            

            dicionario = {"type": "if", "cond" : cond, "inst_type":inst_type[0], "inst" : inst_type[1]}
            if len(teste.children) == 3:
                self.last = 'if ' + cond
                else_inst = self.visit(teste.children[2])
                dicionario["else_inst_type"] = else_inst[0]
                dicionario["else_inst"] = else_inst[1]
                self.graph.edge(self.last, "fi" + str(self.status["if"]))

            if 'conditional' in dicionario["inst_type"]:
                self.totEstruturasAninh["mm"] += 1
            elif 'ciclo' in dicionario["inst_type"]:
                self.totEstruturasAninh["dif"] += 1

            if dicionario["inst_type"][0] == 'conditional':
                livre = self.geraCodigoLivre(dicionario)
                simples = self.geraCodigoSimples(dicionario)
                self.controloAninh[livre] = simples

            self.last = "fi" + str(self.status["if"])

            self.status["if"] -= 1
            if self.status["if"] == self.status["if_start"]:
                self.status["if"] = self.status["ifs"]
                self.status["if_start"] = self.status["if"]
         
            self.totInst["cond"]+=1

            return ("conditional", dicionario)

        elif q.data == 'ciclos':

            teste = self.visit(tree.children[0])[1]
            cycle = self.visit(teste.children[0])[0]

            # while
            if cycle.data == 'ciclo1':
                cond =self.visit(cycle.children[0])


            # repeat ...  until (condition)           
            if cycle.data == 'ciclo2':
                cond = self.visit(cycle.children[1]) 

            # for
            if cycle.data == 'ciclo3':
                if len(cycle.children)==4:
                    # for (i = 0; i<20; i=i+1)
                    att = self.visit(cycle.children[0])
                    cond = self.visit(cycle.children[1])
                    inc = self.visit(cycle.children[2])
                elif len(cycle.children)==3:
                    # for (; cond ; inc)
                    if cycle.children[0].data=='condition':
                        att = ''
                        cond = self.visit(cycle.children[0])
                        inc = self.visit(cycle.children[1])
                    # for (x = 4; cond; )
                    if cycle.children[0].data=='declare' or cycle.children[0].data=='atribuicao':
                        att = self.visit(cycle.children[0])
                        cond = self.visit(cycle.children[1])
                        inc = ''
                loop = 'for' + ' (' + att + ' ;' + cond + ' ;' + inc + ')' 
                self.graph.edge(self.last,loop)
                self.last = loop
                print(loop)
            
            self.totInst["ciclo"]+=1
            return ("ciclo", teste)

        elif q.data == 'print':
            print("print")
            var = self.visit(tree.children[0])
            self.graph.edge(self.last, var)
            self.last = var
            self.totInst["rw"]+=1
            # print ("print", var)
            return ("print", var)
        else:
            var = self.visit(tree.children[0])
            self.graph.edge(self.last, var)
            self.last = var
            # print ("declaracao", var)
            return ("declaracao", var)

    def instrucoes(self,tree):
        # print(tree.pretty())
        a = []
        for elem in tree.children:
            a.append(self.visit(elem))
        return list(map(list, zip(*a)))

    def lista(self,tree):
        var = self.visit_children(tree)
        listas = []
        for elem in var:
            listas.append(elem)
        self.totEstruturas["listas"] += 1
        return listas

    def print(self,tree):
        # print : "print" "(" VAR ")"
        q = self.visit_children(tree)
        self.totInst["rw"]+=1
        return "print(" + str(q[0]) + ")"

    def set(self, tree):
        var = self.visit_children(tree)
        sets = set()
        for elem in var:
            sets.add(elem)
        self.totEstruturas["conjuntos"]+=1
        return sets
    
    def tuple(self,tree):
        var = self.visit_children(tree)
        tuples = ()
        for elem in var:
            tuples = (*tuples, elem)
        self.totEstruturas["tuplos"] += 1
        return tuples
        
    def valor(self,tree):
        q = tree.children[0]

        if q.type == 'VAR':
            if q not in self.variaveis.keys():
                self.variaveis[str(q)] = self.varStatus(ND=True,UNI = True)
            else: 
                self.variaveis[str(q)]["DN"] = False
            return str(q)
        elif q.type == 'INT':
            return int(q)

    def key(self, tree): 
        # (STRING | INT | tuplecomp) // tipos de estruturas/dados que são imutáveis/comparaveis
        q = tree.children[0]
        if isinstance(q,Token):
            if q.type == "STRING":
                string = str(q)
                return string[1:-1]
            else:
                return int(q)
        else:
            var = self.visit(q)
            return var

    def value(self, tree): 
        # (estruturas | STRING | INT)
        q = tree.children[0]
        if isinstance(q,Token):
            if q.type == "STRING":
                string = str(q)
                return string[1:-1]
            else:
                return int(q)
        else:
            var = self.visit(q)
            return var
    
g = open("grammar.txt","r")
grammar = g.read()

def varStatus(varS):
    sVar = {"RED" : [], "ND" : [], "UNI" : [], "DN" : [], "VARS" : []}
    for var in varS.keys():
        sVar["VARS"].append(var)
        if(varS[var]["DEC"] > 1):
            sVar["RED"].append(var)
        if(varS[var]["ND"] == True):
            sVar["ND"].append(var)
        if(varS[var]["UNI"] == True):
            sVar["UNI"].append(var)
        if(varS[var]["DN"] == True):
            sVar["DN"].append(var)        
    return sVar

f = open("frase3.txt", "r")

frase = f.read()

p = Lark(grammar)
parse_tree = p.parse(frase)
#print(parse_tree.pretty())
data = MyInterpreter().visit(parse_tree)
#print("Número de números ",data[0]," Somatório: ",data[1])
# print(data)


data["vars"] = varStatus(data["vars"])

html.geraRel(data)