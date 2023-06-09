# ----------------------------------
# Exemplo para Busca Não -Informada
# ----------------------------------

from logging import raiseExceptions
import string
import sys
import time 
from scipy.spatial.distance import cityblock

# Classe No com 3 atributos: estado, pai e ação
class No():
    def __init__(self, estado, pai, acao, custo, heuristica):
        self.estado = estado
        self.pai = pai
        self.acao = acao
        self.custo = custo
        self.heuristica = heuristica

# Classe para tratar Nós Fronteira
# Deep First Search (DFS)
class PilhaFronteira():
    # Inicializa Fronteira vazia
    def __init__(self):
        self.fronteira = []
    
    # Insere na pilha	
    def add(self, no):
        self.fronteira.append(no)
    
    # Procura no pilha por um estado
    def contem_estado(self, estado):
        return any(no.estado == estado for no in self.fronteira)

    # Verifica se Fronteira está vazia
    def empty(self):
        return len(self.fronteira) == 0

    # Remove estado da Fronteira do tipo Pilha
    def remove(self):
        if self.empty():
            raise Exception("fronteira vazia")
        else:
            no = self.fronteira[-1]
            self.fronteira = self.fronteira[:-1]
            return no

# Breadth First Search (BFS) herdando métodos da DFS
# Só muda a remoção do nó da fronteira
class FilaFronteira(PilhaFronteira):

    # Remove estado da Fronteira do tipo Fila
    def remove(self):
        if self.empty():
            raise Exception("fronteira vazia")
        else:
            no = self.fronteira[0]
            self.fronteira = self.fronteira[1:]
            return no

# Implementação da remoção de nos da fronteira usando 
# algoritmo A*
class ListaFronteira(PilhaFronteira):

    # Remove estado da Fronteira do tipo Lista
    def remove(self):
        if self.empty():
            raise Exception("fronteira vazia")
        else:
            menorNo = self.fronteira[0]
            A = menorNo.custo + menorNo.heuristica
            for no in self.fronteira:
                if(no.custo + no.heuristica < A):
                    A = no.custo + no.heuristica
                    menorNo = no
                    
            self.fronteira.remove(menorNo)
            return menorNo
                

# Classe do Problema de Busca
class Labirinto():

    # Inicializa instância do problema com o arquivo TXT filename
    def __init__(self, filename):

        # Lê arquivo e configura altura e largura do labirinto
        with open(filename) as f:
            contents = f.read()

        # Valida Largada e Chegada
        if contents.count("A") != 1:
            raise Exception("labirinto deve ter exatamente um ponto de partida")
        if contents.count("B") != 1:
            raise Exception("labirinto deve ter exatamente uma chegada")

        # Determina altura e largura do labirinto
        contents = contents.splitlines()
        self.altura = len(contents)
        self.largura = max(len(line) for line in contents)

        # Manter as paredes
        self.paredes = []
        for i in range(self.altura):
            row = []
            for j in range(self.largura):
                try:
                    if contents[i][j] == "A":
                        self.inicio = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.objetivo = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.paredes.append(row)

        self.solucao = None

    # Imprime na tela a solução
    def print(self):
        solucao = self.solucao[1] if self.solucao is not None else None
        print()
        for i, row in enumerate(self.paredes):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.inicio:
                    print("A", end="")
                elif (i, j) == self.objetivo:
                    print("B", end="")
                elif solucao is not None and (i, j) in solucao:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()


    # Identifica os vizinhos do estado 
    def vizinhos(self, estado):
        linha, coluna = estado
        candidatos = [
            ("up", (linha - 1, coluna)),
            ("down", (linha + 1, coluna)),
            ("left", (linha, coluna - 1)),
            ("right", (linha, coluna + 1))
        ]

        resultado = []
        for acao, (l, c) in candidatos:
            if 0 <= l < self.altura and 0 <= c < self.largura and not self.paredes[l][c]:
                resultado.append((acao, (l, c)))
        return resultado


    # Invoca o método solve() para encontrar a solução 
    def solve(self, metodo):
        """Encontrar uma solução para labirinto, se existe."""

        # Acompanhar o número de estados explorados
        self.num_explored = 0

        # Escolhe um peso para w que multiplicara a heuristica -> f(n)=g(n)+wh(n)
        valores_w = [(1, 1)]
        # [multiplica a linha, multiplica a coluna]
        w = valores_w[0]

        # Inicializa a fronteira apenas para o posição inicial
        metodo = metodo.upper()
        inicio = No(estado=self.inicio, pai=None, acao=None, custo=0, heuristica=cityblock(self.inicio, self.objetivo, w))
        if(metodo == "P"):
            fronteira = PilhaFronteira() #Pilha -> Profundidade
        elif(metodo == "L"):
            fronteira = FilaFronteira() #Fila -> Largura
        elif(metodo == "A"):
            fronteira = ListaFronteira() #Lista -> A*
        else:
            raise Exception("Erro na escolha de metodo: P, L, A")
    

        fronteira.add(inicio)

        # Inicializa um conjunto vazio de estados não explorados
        self.explored = set()
        self.listaExplorados = []

        # Mantem laço até encontrar solução
        while True:

            # Se não sobrar nada na fronteira, então não há caminho
            if fronteira.empty():
                raise Exception("sem solução")

            # Escolha um nó da fronteira
            no = fronteira.remove()
            self.num_explored += 1

            # Se o nó é objetivo, então temos uma solução
            if no.estado == self.objetivo:
                acoes = []
                celulas = []
                heuristica = []
                while no.pai is not None:
                    acoes.append(no.acao)
                    celulas.append(no.estado)
                    heuristica.append((no.estado, no.heuristica, no.custo))
                    no = no.pai
                acoes.reverse()
                celulas.reverse()
                heuristica.reverse()
                self.solucao = (acoes, celulas, heuristica)
                return

            # Marca nó como explorado
            self.explored.add(no.estado)
            self.listaExplorados.append((no.estado, no.heuristica, no.custo))

            # Adiciona vizinhos a fronteira
            for acao, estado in self.vizinhos(no.estado):
                if not fronteira.contem_estado(estado) and estado not in self.explored:
                    filho = No(estado=estado, pai=no, acao=acao, custo=(no.custo+1), heuristica=cityblock(estado, self.objetivo, w))
                    fronteira.add(filho)

    # Imprime o labirinto com os estados explorados
    def output_image(self, filename, show_solution=True, show_explored=False, ):
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 50
        cell_border = 2

        # Cria uma tela preta
        img = Image.new(
            "RGBA",
            (self.largura * cell_size, self.altura * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)
        myFont = ImageFont.truetype('Roboto-Black.ttf', 10)
       
        solucao = self.solucao[1] if self.solucao is not None else None
        for i, row in enumerate(self.paredes):
            for j, col in enumerate(row):

                # Paredes
                if col:
                    fill = (40, 40, 40)

                # Inicio
                elif (i, j) == self.inicio:
                    fill = (255, 0, 0)

                # Objetivo
                elif (i, j) == self.objetivo:
                    fill = (0, 171, 28)

                # Solução
                elif solucao is not None and show_solution and (i, j) in solucao:
                    fill = (220, 235, 113)

                # Exploroda
                elif solucao is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Celula Vazia
                else:
                    fill = (237, 240, 252)
                    

                # Desenha celula
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )
      
        # Imprime na imagem os valores de heuristica(azul), custo(vermelho), e total f(n)(preto)
        for v in self.listaExplorados:
            draw.text((((v[0][1] * cell_size)+5), ((v[0][0] * cell_size))+1), str(v[1]), fill =(0, 0, 250),font=myFont)
            draw.text((((v[0][1] * cell_size)+5), ((v[0][0] * cell_size))+10), str(v[2]), fill =(200, 0, 0),font=myFont)
            draw.text((((v[0][1] * cell_size)+5), ((v[0][0] * cell_size))+35), str((v[2]+v[1])), fill =(50 ,50, 50),font=myFont)

        img.save(filename)




# ----------------------
# Programa Principal 
# ----------------------

if len(sys.argv) != 3:
    sys.exit("Uso: python labirinto.py labirinto.txt A(A ou L ou P)")

m = Labirinto(sys.argv[1])
metodo = sys.argv[2]
print("Labirinto: ")
m.print()
print("Solucionando...")

t1 = time.time()
m.solve(metodo)
t2 = time.time()
tempo_execucao = t2 - t1 
print("Tempo de Execução: ", tempo_execucao)

print("Estados Explorados:", m.num_explored)
print("Custo Solução:", m.solucao[2][-1][2])
print("Solução: ")
m.print()
m.output_image("labirinto.png", show_explored=True)
