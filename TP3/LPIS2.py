from tkinter.tix import Tree
from lark import Discard
from lark import Lark,Token
from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
import graphviz
from re import *

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
        self.cfg = graphviz.Digraph('CFG', filename='CFG.gv', format="png")
        self.cfg.node("inicio", style="filled", fillcolor="chartreuse3")
        self.sdg = graphviz.Digraph('SDG', filename='SDG.gv', format="png")
        self.sdg.node("ENTRY", style="filled", fillcolor="chartreuse3", shape="box")
        self.status = {'if': 0, 'label' : "", "dec" : False, "#nodos" : 2 , "#edges" : 1, "ENTRY" : "ENTRY", "rep" : 0, 'last' : 'inicio'}
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
        self.cfg.node("fim", style="filled", fillcolor="crimson")
        self.cfg.edge(self.status['last'],'fim')
        self.cfg.render(directory='graphs',view=False)
        self.sdg.render(directory='graphs',view=False)
        #self.cfg.view()
        data["complex"] = self.status["#edges"] - self.status["#nodos"] + 2
        data["#edges"] = self.status["#edges"]
        data["#nodos"] = self.status["#nodos"]
        return data


    def atribuicao(self, tree):
        # atribuicao : VAR "=" define

        q = tree.children[0]
        next = self.visit(tree.children[1])
        if q not in self.variaveis.keys():
            self.variaveis[str(q)] = self.varStatus(ND = True)
        else: 
            self.variaveis[str(q)]["DN"] = False
        var =  str(q) + ' = ' + str(next)

        if self.status["dec"] == False:
            node = sub(r':', ';', var)
            self.cfg.edge(self.status['last'], node, label = self.status["label"])
            self.sdg.edge(self.status["ENTRY"], node)
            self.status["label"] = ""
            self.status['last'] = node
            self.status['last'] = node
            self.status["#nodos"] += 1
            self.status["#edges"] += 1

        return var

        
    # CICLOS
    def ciclos(self, tree):
        dicionario = self.visit(tree.children[0])
        if 'conditional' in dicionario["inst_type"]:
            self.totEstruturasAninh["dif"] += 1
        elif 'ciclo' in dicionario["inst_type"]:
            self.totEstruturasAninh["mm"] += 1
        return dicionario


    # WHILE
    def ciclo1(self, tree):
        # "while" "(" condition ")" "{" instrucoes "}"
       
    
        cond = self.visit(tree.children[0])
        self.cfg.node('while ' + cond, shape="diamond")
        self.cfg.edge(self.status['last'], 'while ' + cond, label = self.status["label"])
        self.sdg.edge(self.status["ENTRY"], 'while ' + cond)
        last_entry = self.status["ENTRY"]
        self.status["ENTRY"] = 'while ' + cond
        self.status["label"] = "then"
        self.status['last'] = 'while ' + cond

        inst = self.visit(tree.children[1])

        self.cfg.edge(self.status['last'], 'while ' + cond, label = self.status["label"])
        self.status['last'] = 'while ' + cond
        self.status["label"] = "else"

        self.status["#nodos"] += 1
        self.status["#edges"] += 2
        
        self.status["ENTRY"] = last_entry

        return { "type" : "while", "cond" : cond, "inst_type": inst[0], "inst" : inst[1]}
    

    # REPEAT..UNTIL
    def ciclo2(self,tree):
        # "repeat" "{" instrucoes "}" "until" "(" condition ")"
        
        last_entry = self.status["ENTRY"]
        self.cfg.edge(self.status['last'], 'repeat' + str(self.status["rep"]), label = self.status["label"])

        cond = self.visit(tree.children[1])
        self.sdg.edge(self.status["ENTRY"], 'repeat_until ' + cond)
        self.status['last'] = 'repeat' + str(self.status["rep"])
        self.status["ENTRY"] = 'repeat_until ' + cond
        inst = self.visit(tree.children[0])
        self.cfg.node('until ' + cond, shape="diamond")
        self.cfg.edge(self.status['last'], 'until ' + cond, label = self.status["label"])
        self.cfg.edge('until ' + cond, 'repeat' + str(self.status["rep"]), label = "then")
        self.status["label"] = "else"
        self.status['last'] = 'until ' + cond

        self.status["#nodos"] += 2
        self.status["#edges"] += 3

        self.status["rep"] += 1

        self.status["ENTRY"] = last_entry 

        return { "type" : "reapeat", "cond" : cond, "inst_type": inst[0], "inst" : inst[1]}
    

    # FOR
    def ciclo3(self,tree):
        #"for" "(" (declare | atribuicao )? ";" condition ";" atribuicao? ")" "{" instrucoes "}"

        if len(tree.children) == 4:
            self.visit(tree.children[0])
            
            cond = self.visit(tree.children[1])
            self.cfg.node('for ' + cond, shape="diamond")
            self.cfg.edge(self.status['last'], 'for ' + cond, label = self.status["label"])
            self.sdg.edge(self.status["ENTRY"], 'for ' + cond)
            last_entry = self.status["ENTRY"]
            self.status["ENTRY"] = 'for ' + cond
            self.status["label"] = "then"
            self.status['last'] = 'for ' + cond

            inst = self.visit(tree.children[3])

            self.visit(tree.children[2])
            self.cfg.edge(self.status['last'], 'for ' + cond, label = self.status["label"])
            self.status['last'] = 'for ' + cond
            self.status["label"] = "else"

            self.status["#nodos"] += 1
            self.status["#edges"] += 2
        elif len(tree.children) == 2:
            cond = self.visit(tree.children[0])
            self.cfg.node('for ' + cond, shape="diamond")
            self.cfg.edge(self.status['last'], 'for ' + cond, label = self.status["label"])
            self.sdg.edge(self.status["ENTRY"], 'for ' + cond)
            last_entry = self.status["ENTRY"]
            self.status["ENTRY"] = 'for ' + cond
            self.status["label"] = "then"
            self.status['last'] = 'for ' + cond

            inst = self.visit(tree.children[1])

            self.cfg.edge(self.status['last'], 'for ' + cond, label = self.status["label"])
            self.status['last'] = 'for ' + cond
            self.status["label"] = "else"


            self.status["#nodos"] += 1
            self.status["#edges"] += 2
        else:
            if tree.children[0].data == 'declare' or tree.children[0].data == 'atribuicao':
                self.visit(tree.children[0])
            
                cond = self.visit(tree.children[1])
                self.cfg.node('for ' + cond, shape="diamond")
                self.cfg.edge(self.status['last'], 'for ' + cond, label = self.status["label"])
                self.sdg.edge(self.status["ENTRY"], 'for ' + cond)
                last_entry = self.status["ENTRY"]
                self.status["ENTRY"] = 'for ' + cond
                
                self.status["label"] = "then"
                self.status['last'] = 'for ' + cond

                inst = self.visit(tree.children[2])

                self.cfg.edge(self.status['last'], 'for ' + cond, label = self.status["label"])
                self.status['last'] = 'for ' + cond
                self.status["label"] = "else"
            else:            
                cond = self.visit(tree.children[0])
                self.cfg.node('for ' + cond, shape="diamond")
                self.cfg.edge(self.status['last'], 'for ' + cond, label = self.status["label"])
                self.sdg.edge(self.status["ENTRY"], 'for ' + cond)
                last_entry = self.status["ENTRY"]
                self.status["ENTRY"] = 'for ' + cond
                self.status["label"] = "then"
                self.status['last'] = 'for ' + cond

                inst = self.visit(tree.children[2])

                self.visit(tree.children[1])
                self.cfg.edge(self.status['last'], 'for ' + cond, label = self.status["label"])
                self.status['last'] = 'for ' + cond
                self.status["label"] = "else"
            self.status["#nodos"] += 1
            self.status["#edges"] += 2
            
        self.status["ENTRY"] = last_entry

        

        return { "type" : "for", "cond" : cond, "inst_type":inst[0], "inst" :inst[1]}


    # CONDICIONAL AND
    def condition(self, tree): 
        #     condition "and" condition2
        #   | condition2
        q = tree.children
        if len(q) == 1:
            return self.visit(q[0])
        else:
            return self.visit(q[0]) + ' and ' + self.visit(q[1])


    # CONDICIONAL OR
    def condition2(self,tree):
        # condition2 "or" condition3
        # | condition3
        q = tree.children
        if len(q) == 1:
            return self.visit(q[0])
        else:
            return self.visit(q[0]) + ' or ' + self.visit(q[1])


    # CONDITIONAL REL
    def condition3(self, tree): 
        # "(" condition ")"
        #    | exprel
        #    | "!" condition 
        q = tree.children
        return self.visit(q[0])


    # CONDITIONAL 
    def conditional(self, tree):
        # "if" "(" condition ")" "{" instrucoes "}" ("else" "{" instrucoes "}")?
        self.status["if"] += 1
        if_number = self.status["if"]
        cond = self.visit(tree.children[0])
        self.cfg.node('if ' + cond, shape="diamond")
        self.cfg.edge(self.status['last'], 'if ' + cond, label = self.status["label"])
        self.sdg.edge(self.status["ENTRY"], 'if ' + cond)
        self.sdg.edge('if ' + cond, 'then' + str(if_number))
        last_entry = self.status["ENTRY"]
        self.status["ENTRY"] = 'then' + str(if_number)
        self.status["label"] = ""
        self.status['last'] = 'if ' + cond
        self.status["label"] = "then"
        inst_type = self.visit(tree.children[1])
        
        self.cfg.edge(self.status['last'], "fi" + str(if_number))
        

        dicionario = {"type": "if", "cond" : cond, "inst_type":inst_type[0], "inst" : inst_type[1]}
        if len(tree.children) == 3:
            self.sdg.edge('if ' + cond, 'else' + str(if_number))
            self.status["ENTRY"] = 'else' + str(if_number)
            self.status['last'] = 'if ' + cond
            self.status["label"] = "else"
            else_inst = self.visit(tree.children[2])
            dicionario["else_inst_type"] = else_inst[0]
            dicionario["else_inst"] = else_inst[1]
            self.cfg.edge(self.status['last'], "fi" + str(if_number), label = self.status["label"])
        else:
            self.cfg.edge('if ' + cond, "fi" + str(if_number), label = "else")

        if 'conditional' in dicionario["inst_type"]:
            self.totEstruturasAninh["mm"] += 1
        elif 'ciclo' in dicionario["inst_type"]:
            self.totEstruturasAninh["dif"] += 1

        if dicionario["inst_type"][0] == 'conditional':
            livre = self.geraCodigoLivre(dicionario)
            simples = self.geraCodigoSimples(dicionario)
            self.controloAninh[livre] = simples

        self.status['last'] = "fi" + str(if_number)

        self.status["#nodos"] += 2
        self.status["#edges"] += 3
        self.status["ENTRY"] = last_entry

        return dicionario


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
            self.status["dec"] = True
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

        var = 'var ' + str(var)
        
        if self.status['dec'] == False:
            node = sub(r':', ';', var)
            self.cfg.edge(self.status['last'], node, label = self.status["label"])
            self.sdg.edge(self.status["ENTRY"], node)
            self.status["label"] = ""
            self.status['last'] = node
        else:
            node = 'var ' + sub(r':', ';', q)
            self.cfg.edge(self.status['last'], node, label = self.status["label"])
            self.sdg.edge(self.status["ENTRY"], node)
            self.status["label"] = ""
            self.status['last'] = node
            self.status["dec"] = False
        
        self.status["#nodos"] += 1
        self.status["#edges"] += 1

        return var


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


    def instrucao(self,tree):

        q = tree.children[0]
        var = self.visit(q)
        
        if q.data == 'atribuicao':
            self.totInst["atribuicao"]+=1
            return ("atribuicao", var)
        if q.data == 'conditional':
            self.totInst["cond"]+=1
            return ("conditional", var)
        elif q.data == 'ciclos':
            self.totInst["ciclo"]+=1
            return ("ciclo", var)
        elif q.data == 'print':
            self.totInst["rw"]+=1
            return ("print", var)
        else:
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
        var =  "print(" + str(q[0]) + ")"

        self.cfg.edge(self.status['last'], var, label = self.status["label"])
        self.sdg.edge(self.status["ENTRY"], var)
        self.status["label"] = ""
        self.status['last'] = var
        self.status["#nodos"] += 1
        self.status["#edges"] += 1
        

        return var


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
                string = str(q)[1:-1]
                return string
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

filename = "frase4.txt"
f = open(filename, "r")

frase = f.read()

p = Lark(grammar)
parse_tree = p.parse(frase)
#print(parse_tree.pretty())
data = MyInterpreter().visit(parse_tree)
#print("Número de números ",data[0]," Somatório: ",data[1])
# print(data)


data["vars"] = varStatus(data["vars"])

html.geraRel(data,filename)
