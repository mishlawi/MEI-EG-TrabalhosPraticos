from lark import Discard
from lark import Lark,Token
from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
import geraHTML as html

# Note que a nova vers ̃ao dessa linguagem, que ser ́a designada por LPIS2, deve permitir declarar vari ́aveis at ́omicas e
# estruturadas (incluindo como no Python as estruturas: conjunto, lista, tuplo, dicionario), instru ̧c ̃oes condicionais e
# pelo menos 3 variantes de ciclos.


class MyInterpreter (Interpreter):
    
    def varStatus(self, DEC = 0, ND = False, UNI = False, DN = False):
        return {"DEC" : DEC, "ND" : ND, "UNI" : UNI, "DN" : DN}

    # DEC: valor numérico de declarações 
    # ND: Não declarada 
    # UNI : Usada mas Não Inicializada 
    # DN : Declarada, mas não usada

    def __init__(self):
        self.variaveis = {}  # {var: {DEC: 0, ND:False, UNI:True, DN:False}} DEC: # de declarações | ND: Não declarada | UNI : Usada mas Não Inicializada | DN : Declarada, mas não usada
        self.totVarsDec = 0
        self.totEstruturas = {"dicts" : 0, "listas" : 0, "tuplos" : 0, "conjuntos" : 0}
        self.totInst = {"atribuicao" : 0, "rw" : 0, "cond" : 0, "ciclo" : 0 }
        self.totEstruturasAninh = {"mm" : 0, "dif" : 0}
        self.controloAninh = {} # {ifAninhado : ifSolo}



    def start(self,tree):
        r = self.visit(tree.children[0])
        print("\nstart\n")
        print(tree)
        data = {}
        data["vars"] = self.variaveis
        data["#varsDec"] = self.totVarsDec
        data["#estruturas"] = self.totEstruturas
        data["#inst"] = self.totInst
        data["#estruturasAninh"] = self.totEstruturasAninh
        data["estruturasAninhadas"] = self.controloAninh
        return data

    def instrucoes(self,tree):
        print("\nconjunto de instrucoes\n")
        var = self.visit_children(tree)
        # print(var)
        # for elem in var:
        #     print("instrucao")
        #     #self.visit(elem)
        #     print(elem)
        # r = self.visit(tree.children[0])
        return var



    def instrucao(self,tree):
        q = tree.children[0]
        if (not isinstance(q, Token)):
            if( q.data == 'atribuicao'):
                self.totInst["atribuicao"]+=1
            elif (q.data == 'conditional'):
                self.totInst["cond"]+=1
            elif (q.data == 'ciclos'):
                self.totInst["ciclo"]+=1
            elif (q.data == 'print'):
                self.totInst["rw"]+=1
                print("\nPRINT")
            print(tree.children[0])
            n = self.visit(tree.children[0])
            return n
        else:
          self.visit(tree.children[0])
          return 0

    def declare(self,tree):
        q = tree.children[0]
        print("\nDEFINE")
        self.totVarsDec += 1
        if len(tree.children) == 2:
            self.totInst["atribuicao"] += 1
        if q not in self.variaveis.keys():
            self.variaveis[str(q)] = self.varStatus(DEC=1, DN=True)
        else: 
            self.variaveis[str(q)]["DEC"] += 1

        return self.visit_children(tree)


    def atribuicao(self, tree):
        q = tree.children[0]
        print("\nDEFINE")
        if q not in self.variaveis.keys():
            self.variaveis[str(q)] = self.varStatus(ND = True)
        else: 
            self.variaveis[str(q)]["DN"] = False

        return self.visit_children(tree)
   
    def valor(self,tree):
        q = tree.children[0]

        if q.type == 'VAR':
            print("ENTROU NOVAR")
        
             
            if q not in self.variaveis.keys():
                self.variaveis[str(q)] = self.varStatus(ND=True,UNI = True)
            else: 
                self.variaveis[str(q)]["DN"] = False

    def input(self,tree):
        self.totInst["rw"]+=1

    def lista(self,tree):
        var = self.visit_children(tree)
        self.totEstruturas["listas"] += 1
        for elem in var:
            print("estrutura lista")
            #self.visit(elem)
            print(elem)
        return var


    def tuple(self,tree):
        self.totEstruturas["tuplos"] += 1
        var = self.visit_children(tree)
        for elem in var:
            print("estrutura tuplo")
            #self.visit(elem)
            print(elem)
        return var        
        

    def dicionario(self,tree):
        self.totEstruturas["dicts"] += 1
        var = self.visit_children(tree)
        for elem in var:
            print("estrutura dicionario")
            #self.visit(elem)
            print(elem)
        return var

    def set(self, tree):
        self.totEstruturas["conjuntos"]+=1
        var = self.visit_children(tree)
        for elem in var:
            print("estrutura set")
            #self.visit(elem)
            print(elem)
        return var

    def conditional(self, tree):
        q = self.visit(tree.children[1])
        
        print("----------------------------------")
        #print("CONDITIONAL: " , self.visit_children(tree))
        print()
        print(tree)
        print("----------------------------------")
        #if q != "NONE":
         #   self.totEstruturasAninh["mm"] += 1


grammar = r'''

start: instrucoes

instrucoes : instrucao ";" (instrucao ";")*

instrucao : declare
          | atribuicao
          | conditional
          | ciclos
          | print

// CICLOS 

ciclos : ciclo1
       | ciclo2
//     | ciclo3

ciclo1 : "while" "(" condition ")" "{" instrucoes "}"
ciclo2 : "repeat" "{" instrucoes "}" "until" "(" condition ")"
ciclo3 : "for" "(" (declare | atribuicao | ) ";" condition ";" atribuicao ")" "{" instrucoes "}"

// LEITURA 
print : "print" "(" VAR ")"

// ESCRITA
input : "input" "(" ")"


// CONDICIONAL
conditional : "if" "(" condition ")" "{" instrucoes "}" ("else" "{" instrucoes "}")? // verificar /n nestes casos é necessario?

condition : condition "and" condition2
          | condition2

condition2 : condition2 "or" condition3
           | condition3

condition3 : "(" condition ")"
           | exprel
           | "!" condition 

exprel : expression oprel expression

oprel : MAIORIG
      | MENORIG
      | MAIOR
      | MENOR
      | IGUAL
      | DIF 

// ATRIBUICOES e INICIALIZACOES

declare : "var" VAR  "=" define
        | "var" VAR

atribuicao : VAR "=" define

define : expression
       | estruturas
       | input
       | INT


// VALORES E CONTAS ELEMENTARES

expression : expression "+" conta
           | expression "-" conta
           | conta

conta : valor "*" valor
      | valor "/" valor
      | valor "%" valor 
      | valor

valor : INT
      | VAR
      | "(" expression ")"

// TIPOS DE ESTRUTURAS
estruturas : lista
           | tuple
           | dicionario
           | set

// ESTRUTURAS

set : "{" key ("," key) *"}"

lista : "[" "]"   
      | "[" value ("," value)* "]"


dicionario : "{" "}"
           | "{" key ":" value ("," key ":" value )* "}"


tuple : "(" value ("," value)* ")" // pode ter listas e dicionarios

tuplecomp : "(" key ("," key)* ")" // NAO pode ter listas e dicionarios

key : (STRING | INT | tuplecomp) // tipos de estruturas/dados que são imutáveis/comparaveis

value : (estruturas | STRING | INT)

// TERMINAIS

STRING : /\"/ (WORD|" ")* /\"/
VAR : LETTER (LETTER | DIGIT)*

MAIOR : ">"
MAIORIG : ">="
MENOR: "<"
MENORIG : "<="
IGUAL : "=="
DIF : "!="


// IMPORTS

%import common.WS
%import common.WORD
%import common.LETTER
%import common.INT
%import common.DIGIT


// IGNORES

%ignore WS
'''

def varStatus(varS):
    sVar = {"RED" : [], "ND" : [], "UNI" : [], "DN" : []}
    for var in varS.keys():
        if(varS[var]["DEC"] > 1):
            sVar["RED"].append(var)
        if(varS[var]["ND"] == True):
            sVar["ND"].append(var)
        if(varS[var]["UNI"] == True):
            sVar["UNI"].append(var)
        if(varS[var]["DN"] == True):
            sVar["DN"].append(var)        
    return sVar

f = open("frase.txt", "r")

frase = f.read()

#frase = """int var = 4 * ( x + 3);"""
p = Lark(grammar)
parse_tree = p.parse(frase)
#print(parse_tree.pretty())
data = MyInterpreter().visit(parse_tree)
#print("Número de números ",data[0]," Somatório: ",data[1])
print(data)

data["vars"] = varStatus(data["vars"])
# print(data)
# print(html.geraHTML(data))
