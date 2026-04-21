from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, Ellipse, Triangle, PushMatrix, PopMatrix, Rotate, RoundedRectangle, StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.animation import Animation
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader
import numpy as np
import data.libs.back2048 as back2048

# Variaveis globais
fps_limit = 60
fps_print_delay = 1#frames
width, height = Window.size
# Variavel que define o tamanho da janela do jogo
size = height*0.41
# Variavel que define o espacamento do grid
space = size*0.022
# Dicionario que armazena os dados do touch
click_data = {}

# Dicionario que armazena todas as cores do jogo 2048 original
colors_2048 = {
	"background_window": (0.609, 0.535, 0.472),
	"background_grid": (0.733, 0.678, 0.627),
	"background_game": (0.980, 0.973, 0.937),
	"black_text": (0.467, 0.431, 0.396),
	"white_text": (0.976, 0.965, 0.949),
	"score_text": (0.596, 0.533, 0.462),
	2: (0.933, 0.894, 0.855),
	4: (0.917, 0.843, 0.710),
	8: (0.949, 0.694, 0.475),
	16: (0.961, 0.584, 0.388),
	32: (0.965, 0.486, 0.373),
	64: (0.965, 0.369, 0.231),
	128: (0.929, 0.812, 0.447),
	256: (0.929, 0.800, 0.380),
	512: (0.929, 0.784, 0.314),
	1024: (0.929, 0.773, 0.247),
	2048: (0.929, 0.761, 0.180),
	"super": (0.235, 0.227, 0.196)# Cor para blocos acima de 2048
}

# Classe Click captura dados do clique
class Click(Widget):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
	# on_touch_down() poe os dados do clique no dicionario
	def on_touch_down(self, touch):
		# (estado, posicao_inicial, posicao_atual)
		# estado 1 (por o dedo na tela)
		# estado 2 (mover o dedo na tela)
		# estado 3 (tirar o dedo da tela)
		click_data[touch.uid] = (1, touch.pos, touch.pos)
		return super().on_touch_down(touch)
	# on_touch_move() atualiza os dados do clique no dicionario
	def on_touch_move(self, touch):
		if touch.uid not in click_data.keys():
			click_data[touch.uid] = (2, touch.pos, touch.pos)
		click_data[touch.uid] = (2, click_data[touch.uid][1], touch.pos)
		return super().on_touch_move(touch)
	# on_touch_up() atualiza os dados do clique no dicionario
	def on_touch_up(self, touch):
		if touch.uid not in click_data.keys():
			click_data[touch.uid] = (3, touch.pos, touch.pos)
		click_data[touch.uid] = (3, click_data[touch.uid][1], touch.pos)
		return super().on_touch_up(touch)

# Classe System, classe principal 
class System(App):
	def build(self):
		# Codigos de inicio
		layout = FloatLayout()
		click = Click()
		self.layout = layout
		self.count = 0
		# Inicializa a variavel fps e desenha na tela
		self.fps = 1
		self.fps_label = Label(text=f"FPS: {self.fps}", pos=(0,0), font_size=20, color=(0,0,0,1))
		self.fps_label.pos = (-width/2+60,height/2-10)
		layout.add_widget(click)
		# Outros codigos
		
		# Variavel que sinaliza se os quadrados ainda estao em movimento
		self.board_while_animation = 0
		
		# Variavel que armazena o score
		self.score = 0
		
		# Variavel que armazena o score incremental
		self.add_score = 0
		
		# Variavel que define a duracao das animacoes
		self.animation_duration = 0.12# segundos
		
		# Matriz 4x4 que salva cada numero do grid
		self.board = back2048.new_board()
		
		# Muda a cor do background desenhando um quadrado preenchendo o fundo inteiro
		with layout.canvas.before:
			background_color = Color(*colors_2048["background_game"], 1)
			Rectangle(pos=(0,0), size=(width,height))
		
		# Imprime o titulo na tela com fonte especifica e com tamanho de fonte relativa a altura da tela
		self.title_label = Label(text=f"Kivy2048", pos=(0,height/2-height*0.06), font_size=height*0.06, font_name="data/font/font.ttf", color=(*colors_2048["black_text"], 1))
		layout.add_widget(self.title_label)
		
		# Imprime o score na tela com fonte especifica e com tamanho de fonte relativa a altura da tela
		self.score_label = Label(text=f"{self.score}", pos=(0,size/2-space/4+height*0.07), font_size=height*0.07, font_name="data/font/font.ttf", color=(*colors_2048["score_text"], 1))
		layout.add_widget(self.score_label)
		
		# Dicionario que vai guardar dados do grid como texto de cada quadrado e cor de cada quadrado, para facil modificacao
		self.grid = {}
		with layout.canvas:
			# Desenha a janela de grid
			Color(*colors_2048["background_window"], 1)
			RoundedRectangle(pos=(width/2-size/2-space/4,height/2-size/2-space/4), size=(size+space/2,size+space/2), radius=[size/30])
			for y in range(4):
				for x in range(4):
					# Desenha o fundo de cada quadrado do grid
					Color(*colors_2048["background_grid"], 1)
					RoundedRectangle(pos=(width/2-size/2+space/2+(size/4)*x,height/2-size/2+space/2+(size/4)*y), size=(size/4-space,size/4-space), radius=[size/30])
					
			# Desenha o todo o fundo primeiro e os quadrados depois os quadrados para o fundo nao sobrepor os quadrados durante a animação
			for y in range(4):
				for x in range(4):
					# Desenha cada quadrado do grid
					color = Color(*colors_2048[2], 0)
					rect = RoundedRectangle(pos=(width/2-size/2+space/2+(size/4)*x,height/2-size/2+space/2+(size/4)*y), size=(size/4-space,size/4-space), radius=[size/30])
					# Imprime o texto de cada quadrado
					label = Label(text=f"", pos=((size/4)*(x+0.5)-size/2,(size/4)*(y+0.5)-size/2), font_size=size*0.1, font_name="data/font/font.ttf", color=(0,0,0,0))
					layout.add_widget(label)
					# Armazena no dicionario os dados do quadrado atual
					self.grid[(x,y)] = {
						"rect": rect,
						"color": color,
						"label": label
					}
		
		self.update_grid()
		# Executa update_moves periodicamente
		Clock.schedule_interval(self.update_moves, 1/fps_limit)
		# Executa update_fps periodicamente
		Clock.schedule_interval(self.update_fps, 1/fps_limit)
		# Executa update_count periodicamente
		Clock.schedule_interval(self.update_count, 1/fps_limit)
		# Executa update_click periodicamente
		Clock.schedule_interval(self.update_click, 1/fps_limit)
		layout.add_widget(self.fps_label)
		return layout
	
	# update_grid() atualiza o grid na tela
	def update_grid(self):
		# Atualiza self.board_while_animation
		self.board_while_animation = 0
		
		# Acrescenta o score incremental ao score global
		self.score += self.add_score
		if self.add_score:
			# Animacao de pulsar o score na tela ao aumentar
			anim = Animation(font_size=height*0.07*1.4, duration=0.018)+Animation(font_size=height*0.07, duration=0.018)
			anim.start(self.score_label)
		self.score_label.text = f"{self.score}"
		
		# Zera o score incremental
		self.add_score = 0
		
		# Loop que percorre todos os quadrados do grid
		for y in range(4):
			for x in range(4):
				self.grid[(x,y)]["label"].font_size = size*0.1
				self.grid[(x,y)]["rect"].pos = (width/2-size/2+space/2+(size/4)*x,height/2-size/2+space/2+(size/4)*y)
				self.grid[(x,y)]["label"].pos = ((size/4)*(x+0.5)-size/2,(size/4)*(y+0.5)-size/2)
				self.grid[(x,y)]["label"].text = f""
				self.grid[(x,y)]["label"].texture_update()
				if self.board[3-y][x] > 2048:
					# Desenha o quadrado na cor dos numeros acima de 2048
					self.grid[(x,y)]["color"].r = colors_2048["super"][0]
					self.grid[(x,y)]["color"].g = colors_2048["super"][1]
					self.grid[(x,y)]["color"].b = colors_2048["super"][2]
					self.grid[(x,y)]["color"].a = 1
				elif self.board[3-y][x] > 0:
					# Desenha o quadrado na cor respectiva ao numero
					self.grid[(x,y)]["color"].r = colors_2048[self.board[3-y][x]][0]
					self.grid[(x,y)]["color"].g = colors_2048[self.board[3-y][x]][1]
					self.grid[(x,y)]["color"].b = colors_2048[self.board[3-y][x]][2]
					self.grid[(x,y)]["color"].a = 1
				else:
					# Torna o quadrado invisivel caso o seu numero seja 0
					self.grid[(x,y)]["color"].a = 0
				
				if self.board[3-y][x] > 4:
					# Atualiza o texto para o numero do quadrado (caso seja diferente de zero)
					self.grid[(x,y)]["label"].text = f"{self.board[3-y][x]}"
					if len(str(self.board[3-y][x])) > 2: 
						# Ajusta o tamanho da fonte de acordo com a quantidade de caracteres
						self.grid[(x,y)]["label"].font_size = size*0.1/((len(str(self.board[3-y][x]))-1)/1.8)
					# Atualiza a cor do texto para uma cor clara
					self.grid[(x,y)]["label"].color = (*colors_2048["white_text"],1)
					# Atualiza a textura do texto
					self.grid[(x,y)]["label"].texture_update()
				elif self.board[3-y][x] > 0:
					# Atualiza o texto para o numero do quadrado (caso seja diferente de zero)
					self.grid[(x,y)]["label"].text = f"{self.board[3-y][x]}"
					# Atualiza a cor do texto para uma cor escura
					self.grid[(x,y)]["label"].color = (*colors_2048["black_text"],1)
					# Atualiza a textura do texto
					self.grid[(x,y)]["label"].texture_update()
	# board_animation() executa as animaicoes do grid 
	def board_animation(self, direction):
		# Percorre o grid inteiro
		for y in range(4):
			for x in range(4):
				# move_x e move_y define a quantidade de quadrados que o quadrado atual ira se mover
				move_x = 0
				move_y = 0
				
				# Calcula quantos por quadrados o quadrado atual se movera no movimento para esquerda
				if direction == "right" and self.board[3-y][x]:
					# last_number guarda o ultimo numero para prever pares
					last_number = self.board[3-y][x]
					
					# Percorre todo o caminho a frente do quadrado atual
					for path_x in range(3-x)[::-1]:
						# Inverte o sentido do caminho e alinha com quadrado
						path_x = 3-path_x
						# Adiciona um quadrado de movimento a cada zero encontrado no caminho
						if self.board[3-y][path_x] == 0:
							move_x += 1
						else:
							# Se o ultimo numero for igual ao numero atual no loop do caminho
							if last_number == self.board[3-y][path_x]:
								# Adiciona um quadrado de movimento
								move_x += 1
								# last_number se torna zero para evitar pares com numeros de outros pares
								last_number = 0
							else:
								# Atualiza last_number com o ultimo numero
								last_number = self.board[3-y][path_x]
				
				# Calcula quantos por quadrados o quadrado atual se movera no movimento para esquerda
				if direction == "left" and self.board[3-y][x]:
					# last_number guarda o ultimo numero para prever pares
					last_number = self.board[3-y][x]
					
					# Percorre todo o caminho a frente do quadrado atual
					for path_x in range(x)[::-1]:
						# Adiciona um quadrado de movimento a cada zero encontrado no caminho
						if self.board[3-y][path_x] == 0:
							move_x -= 1
						else:
							# Se o ultimo numero for igual ao numero atual no loop do caminho
							if last_number == self.board[3-y][path_x]:
								# Adiciona um quadrado de movimento
								move_x -= 1
								# last_number se torna zero para evitar pares com numeros de outros pares
								last_number = 0
							else:
								# Atualiza last_number com o ultimo numero
								last_number = self.board[3-y][path_x]
				
				# Calcula quantos por quadrados o quadrado atual se movera no movimento para cima
				if direction == "up" and self.board[3-y][x]:
					# last_number guarda o ultimo numero para prever pares
					last_number = self.board[3-y][x]
					
					# Percorre todo o caminho a frente do quadrado atual
					for path_y in range(3-y)[::-1]:
						# Inverte o sentido do caminho e alinha com quadrado 
						path_y = 3-path_y
						# Adiciona um quadrado de movimento a cada zero encontrado no caminho
						if self.board[3-path_y][x] == 0:
							move_y += 1
						else:
							# Se o ultimo numero for igual ao numero atual no loop do caminho
							if last_number == self.board[3-path_y][x]:
								# Adiciona um quadrado de movimento
								move_y += 1
								# last_number se torna zero para evitar pares com numeros de outros pares
								last_number = 0
							else:
								# Atualiza last_number com o ultimo numero
								last_number = self.board[3-path_y][x]
				
				# Calcula quantos por quadrados o quadrado atual se movera no movimento para baixo
				if direction == "down" and self.board[3-y][x]:
					# last_number guarda o ultimo numero para prever pares
					last_number = self.board[3-y][x]
					
					# Percorre todo o caminho a frente do quadrado atual
					for path_y in range(y)[::-1]:
						
						# Adiciona um quadrado de movimento a cada zero encontrado no caminho
						if self.board[3-path_y][x] == 0:
							move_y -= 1
						else:
							# Se o ultimo numero for igual ao numero atual no loop do caminho
							if last_number == self.board[3-path_y][x]:
								# Adiciona um quadrado de movimento
								move_y -= 1
								# last_number se torna zero para evitar pares com numeros de outros pares
								last_number = 0
							else:
								# Atualiza last_number com o ultimo numero
								last_number = self.board[3-path_y][x]
				
				# Verifica se ha animacao
				if move_x or move_y:
					# Atualiza self.board_while_animation
					self.board_while_animation = 1
					# pos_rect guarda a posicao final do quadrado atual
					pos_rect = (width/2-size/2+space/2+(size/4)*(x+move_x),height/2-size/2+space/2+(size/4)*(y+move_y))
					# Cria a animacao
					anim_rect = Animation(pos=pos_rect, duration=self.animation_duration)
					# Atualiza o grid na tela apos a animacao
					anim_rect.bind(on_complete=lambda *args: self.update_grid())
					# pos_rect guarda a posicao final do texto do quadrado atual
					pos_label = ((size/4)*(x+move_x+0.5)-size/2,(size/4)*(y+move_y+0.5)-size/2)
					# Cria a animacao
					anim_label = Animation(pos=pos_label, duration=self.animation_duration)
					anim_label.bind(on_complete=lambda *args: self.update_grid())
					# Inicia as animacoes
					anim_rect.start(self.grid[(x,y)]["rect"])
					anim_label.start(self.grid[(x,y)]["label"])
	# Funcao para atualizar movimentos
	def update_moves(self, dt):
		pass
	# Funcao pra atualizar e reagir ao clique
	def update_click(self, dt):
		toremove = []
		for i in click_data:
			if click_data[i][0] == 3:
				# Execute alguma acao aqui ao soltar o dedo
				# Veirifica se o movimentos do dedo eh maior que 1 vigesimo da altura da tela, para evitar que cliques sejam interpretados como movimento
				if max(abs(click_data[i][2][0]-click_data[i][1][0]),abs(click_data[i][2][1]-click_data[i][1][1])) > height/20:
					move = 0
					# Verifica se o movimento predominante eh horizontal
					if abs(click_data[i][2][0]-click_data[i][1][0]) > abs(click_data[i][2][1]-click_data[i][1][1]):
						# Verifica se o movimento predominante eh para esquerda
						if click_data[i][2][0]-click_data[i][1][0] < 0:
							# Move o grid para a esquerda e salva o score incremental
							moved_board, self.add_score = back2048.move_board_left(self.board)
							move = "left"
						else:
							# Move o grid para a direita e salva o score incremental
							moved_board, self.add_score = back2048.move_board_right(self.board)
							move = "right"
					else:
						# Verifica se o movimento predominante eh para baixo
						if click_data[i][2][1]-click_data[i][1][1] < 0:
							# Move o grid para baixo e salva o score incremental
							moved_board, self.add_score = back2048.move_board_down(self.board)
							move = "down"
						else:
							# Move o grid para cima e salva o score incremental
							moved_board, self.add_score = back2048.move_board_up(self.board)
							move = "up"
					
					# Verifica se houve movimento e se nao tem um movimento acontecendo
					if not np.array_equal(moved_board, self.board) and not self.board_while_animation:
						# Anima o movimento
						self.board_animation(move)
						
						# Atualiza a array self.board com o movimento
						self.board = moved_board
						# Sorteia mais um numero no grid
						self.board = back2048.sort_board(self.board)
						# Atualiza o grid na tela
						#self.update_grid()
						
				# Adiciona o clique na lista de remocao para remover do dicionario ao acabar o loop
				toremove.append(int(i))
		for i in toremove:
			# Remove o clique do dicionario
			click_data.pop(int(i), None)
		
		# Teste para verificar multiply touch
#		if len(click_data) > 5:
#			for i in range(len(click_data)):
#				print(click_data[i], i)
#			raise Exception("Debug")
	
	# update_count() atualiza o contador
	def update_count(self, dt):
		self.count = int(self.count+1*dt*1000)
	# update_fps() atualiza o fps
	def update_fps(self, dt):
		# Atualiza o numero do fps
		self.fps = 1/dt
		if self.count % fps_print_delay == 0:
			# Atualiza o texto e a textura
			self.fps_label.text = f"FPS: {int(self.fps)}"
			self.fps_label.texture_update()

# Inicia o app
System().run()