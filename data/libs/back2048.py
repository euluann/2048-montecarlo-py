import numpy as np
import time

rng = np.random.default_rng()

# new_board() zera todos os numeros de board e gera 2 numeros que variam de 2 ou 4
def new_board():
	board = np.zeros((4, 4), dtype=int)
	# Escolher 2 posições aleatórias únicas sem sobreposicao
	positions = np.random.choice(16, size=2, replace=False)  # 16 = 4*4
	# Transformar posição linear em coordenadas 2D
	rows, cols = positions // 4, positions % 4
	# Sorteia 2 ou 4 pra cada posição
	values = np.random.choice([2, 4], size=2, p=[0.9, 0.1])
	# Preenche o tabuleiro
	board[rows, cols] = values
	return board

# sort_board() gera 2 numeros que variam de 2 ou 4
def sort_board(preboard):
	# Faz uma copia do board pra evitar modificacoes na matriz original
	board = preboard.copy()
	# Encontra indices de zeros
	zero_positions = np.argwhere(board == 0)
	num_zeros = len(zero_positions)
	
	if num_zeros == 0:
		return preboard  # nao ha onde colocar novos numeros
	
	# Quantos numeros adicionar: 2 ou menos se zeros forem poucos
	num_to_add = min(1, num_zeros)
	
	# Escolhe posicoes aleatorias entre os zeros
	selected_idx = np.random.choice(num_zeros, size=num_to_add, replace=False)
	selected_positions = zero_positions[selected_idx]
	
	# Sorteia os valores 2 ou 4
	values = np.random.choice([2, 4], size=num_to_add, p=[0.9, 0.1])
	# Atribui de forma vetorizada
	board[selected_positions[:, 0], selected_positions[:, 1]] = values
	return board

# move_board_right() move os numeros a esquerda somando os numeros em pares
def move_board_right(board):
	# Inverte o tabuleiro horizontalmente
	inverted_board = np.fliplr(board)
	
	# Cria uma mascara, uma array 2d de False's pra diferente de zero e True's pra igual
	mask = inverted_board == 0
	
	# Ordena a mascara pondo os False's primeiro horizontalmente
	idx = np.argsort(mask, axis=1)
	
	# Reordena os elementos de inverted_board pondo os diferentes de zero primeiro
	compact_board = np.take_along_axis(inverted_board, idx, axis=1)
	
	# Inicializa shifted com zeros
	shifted_1 = np.zeros_like(board)
	shifted_2 = np.zeros_like(board)
	shifted_3 = np.zeros_like(board)
	
	# Cria uma copia de compact_board porem com todos os numeros movidos a esquerda 1 casa
	shifted_1[:, 1:] = compact_board[:, :-1]
	# Cria uma copia de compact_board porem com todos os numeros movidos a esquerda 2 casas
	shifted_2[:, 2:] = compact_board[:, :-2]
	# Cria uma copia de compact_board porem com todos os numeros movidos a esquerda 3 casas
	shifted_3[:, 3:] = compact_board[:, :-3]
	
	# Cria uma mascara, uma array 2d com True's para numeros que devem ser dobrados
	mask_merge = (compact_board == shifted_1) & ((compact_board != shifted_2) | (shifted_2 == shifted_3)) & (compact_board != 0)
	
	# Cria uma copia do compact_board
	merged_board = compact_board.copy()
	
	
	# Dobra os numeros que devem ser dobrados em merged_board
	merged_board[mask_merge] *= 2
	
	# Armazena em add_score todos os numeros que foram dobrados
	add_score = np.sum(merged_board[mask_merge])
	
	# Zerar os elementos que foram absorvidos
	merged_board[:, :-1][mask_merge[:, 1:]] = 0
	
	 #Cria uma mascara, uma array 2d de False's pra diferente de zero e True's pra igual
	mask = merged_board == 0
	
	# Ordena a mascara pondo os False's primeiro horizontalmente
	idx = np.argsort(mask, axis=1)
	
	# Reordena os elementos de inverted_board pondo os diferentes de zero primeiro
	compact_merge_board = np.take_along_axis(merged_board, idx, axis=1)
	
	# Inverte o tabuleiro horizontalmente
	board = np.fliplr(compact_merge_board)
	
	return (board, add_score)

# move_board_left() move os numeros a esquerda somando os numeros em pares
def move_board_left(board):
	# Cria uma mascara, uma array 2d de False's pra diferente de zero e True's pra igual
	mask = board == 0
	
	# Ordena a mascara pondo os False's primeiro horizontalmente
	idx = np.argsort(mask, axis=1)
	
	# Reordena os elementos de board pondo os diferentes de zero primeiro
	compact_board = np.take_along_axis(board, idx, axis=1)
	
	# Inicializa shifted com zeros
	shifted_1 = np.zeros_like(board)
	shifted_2 = np.zeros_like(board)
	shifted_3 = np.zeros_like(board)
	
	# Cria uma copia de compact_board porem com todos os numeros movidos a esquerda 1 casa
	shifted_1[:, 1:] = compact_board[:, :-1]
	# Cria uma copia de compact_board porem com todos os numeros movidos a esquerda 2 casas
	shifted_2[:, 2:] = compact_board[:, :-2]
	# Cria uma copia de compact_board porem com todos os numeros movidos a esquerda 3 casas
	shifted_3[:, 3:] = compact_board[:, :-3]
	
	# Cria uma mascara, uma array 2d com True's para numeros que devem ser dobrados
	mask_merge = (compact_board == shifted_1) & ((compact_board != shifted_2) | (shifted_2 == shifted_3)) & (compact_board != 0)
	
	# Cria uma copia do compact_board
	merged_board = compact_board.copy()
	
	# Dobra os numeros que devem ser dobrados em merged_board
	merged_board[mask_merge] *= 2
	
	# Armazena em add_score todos os numeros que foram dobrados
	add_score = np.sum(merged_board[mask_merge])
	
	# Zerar os elementos que foram absorvidos
	merged_board[:, :-1][mask_merge[:, 1:]] = 0
	
	 #Cria uma mascara, uma array 2d de False's pra diferente de zero e True's pra igual
	mask = merged_board == 0
	
	# Ordena a mascara pondo os False's primeiro horizontalmente
	idx = np.argsort(mask, axis=1)
	
	# Reordena os elementos de board pondo os diferentes de zero primeiro
	compact_merge_board = np.take_along_axis(merged_board, idx, axis=1)
	
	board = compact_merge_board
	
	return (board, add_score)


# move_board_up() move os numeros para cima somando os numeros em pares
def move_board_up(board):
	# Cria uma mascara, uma array 2d de False's pra diferente de zero e True's pra igual
	mask = board == 0
	
	# Ordena a mascara pondo os False's primeiro verticalmente
	idx = np.argsort(mask, axis=0)
	
	# Reordena os elementos de board pondo os diferentes de zero primeiro
	compact_board = np.take_along_axis(board, idx, axis=0)
	
	# Inicializa shifted com zeros
	shifted_1 = np.zeros_like(board)
	shifted_2 = np.zeros_like(board)
	shifted_3 = np.zeros_like(board)
	
	# Cria uma copia de compact_board porem com todos os numeros movidos para baixo 1 casa
	shifted_1[1:, :] = compact_board[:-1, :]
	# Cria uma copia de compact_board porem com todos os numeros movidos para baixo 2 casas
	shifted_2[2:, :] = compact_board[:-2, :]
	# Cria uma copia de compact_board porem com todos os numeros movidos para baixo 3 casas
	shifted_3[3:, :] = compact_board[:-3, :]
	
	# Cria uma mascara, uma array 2d com True's para numeros que devem ser dobrados
	mask_merge = (compact_board == shifted_1) & ((compact_board != shifted_2) | (shifted_2 == shifted_3)) & (compact_board != 0)
	
	# Cria uma copia do compact_board
	merged_board = compact_board.copy()
	
	# Dobra os numeros que devem ser dobrados em merged_board
	merged_board[mask_merge] *= 2
	
	# Armazena em add_score todos os numeros que foram dobrados
	add_score = np.sum(merged_board[mask_merge])
	
	# Zerar os elementos que foram absorvidos
	merged_board[:-1, :][mask_merge[1:, :]] = 0
	
	 #Cria uma mascara, uma array 2d de False's pra diferente de zero e True's pra igual
	mask = merged_board == 0
	
	# Ordena a mascara pondo os False's primeiro verticalmente
	idx = np.argsort(mask, axis=0)
	
	# Reordena os elementos de board pondo os diferentes de zero primeiro
	compact_merge_board = np.take_along_axis(merged_board, idx, axis=0)
	
	board = compact_merge_board
	
	return (board, add_score)

# move_board_down() move os numeros para baixo somando os numeros em pares
def move_board_down(board):
	# Inverte o tabuleiro verticalmente
	inverted_board = np.flipud(board)
	
	# Cria uma mascara, uma array 2d de False's pra diferente de zero e True's pra igual
	mask = inverted_board == 0
	
	# Ordena a mascara pondo os False's primeiro verticalmente
	idx = np.argsort(mask, axis=0)
	
	# Reordena os elementos de board pondo os diferentes de zero primeiro
	compact_board = np.take_along_axis(inverted_board, idx, axis=0)
	
	# Inicializa shifted com zeros
	shifted_1 = np.zeros_like(board)
	shifted_2 = np.zeros_like(board)
	shifted_3 = np.zeros_like(board)
	
	# Cria uma copia de compact_board porem com todos os numeros movidos para baixo 1 casa
	shifted_1[1:, :] = compact_board[:-1, :]
	# Cria uma copia de compact_board porem com todos os numeros movidos para baixo 2 casas
	shifted_2[2:, :] = compact_board[:-2, :]
	# Cria uma copia de compact_board porem com todos os numeros movidos para baixo 3 casas
	shifted_3[3:, :] = compact_board[:-3, :]
	
	# Cria uma mascara, uma array 2d com True's para numeros que devem ser dobrados
	mask_merge = (compact_board == shifted_1) & ((compact_board != shifted_2) | (shifted_2 == shifted_3)) & (compact_board != 0)
	
	# Cria uma copia do compact_board
	merged_board = compact_board.copy()
	
	# Dobra os numeros que devem ser dobrados em merged_board
	merged_board[mask_merge] *= 2
	
	# Armazena em add_score todos os numeros que foram dobrados
	add_score = np.sum(merged_board[mask_merge])
	
	# Zerar os elementos que foram absorvidos
	merged_board[:-1, :][mask_merge[1:, :]] = 0
	
	 #Cria uma mascara, uma array 2d de False's pra diferente de zero e True's pra igual
	mask = merged_board == 0
	
	# Ordena a mascara pondo os False's primeiro verticalmente
	idx = np.argsort(mask, axis=0)
	
	# Reordena os elementos de board pondo os diferentes de zero primeiro
	compact_merge_board = np.take_along_axis(merged_board, idx, axis=0)
	
	# Inverte o tabuleiro verticalmente
	board = np.flipud(compact_merge_board)
	
	return (board, add_score)

# Lista das funcoes de movimento
MOVE_FUNCS = [move_board_up, move_board_down, move_board_right, move_board_left]
# Lista dos nomes dos movimentos
MOVE_NAMES = ["up", "down", "right", "left"]

# Funcao que gera um clone, moves_limit eh o limite de movimento antes do clone morrer
def mc_clone(board, moves_limit):
	score = 0
	# Copia o tabuleiro para nao alterar o tabuleiro original 
	current_board = board.copy()
	# Gera uma array com todos os movimentos do clone aleatoriamente
	random_moves = rng.integers(0, 4, size=moves_limit)
	# Armazena o primeiro movimento do clone
	first_move = MOVE_NAMES[random_moves[0]]
	
	# Loop de movimentos
	for move in random_moves:
		# Faz o movimento salvando o tabuleiro resultante e o score incremental
		moved_board, add_score = MOVE_FUNCS[move](current_board)
		# Atualiza o tabuleiro
		current_board = moved_board
		# Atualiza o score
		score += add_score
		# Sorteia um numero novo no tabuleiro
		current_board = sort_board(current_board)
		
	return (first_move, score)

# Funcao que cria uma quantidade determinada de clones para se movimentar no jogo 2048 e retornar o movimento inicial que resultou em maior score
def monte_carlo_2048(board, moves_limit, clones):
	# Dicionario de score para cada direcao de movimento inicial
	move_scores = {"up": 0, "down": 0, "right": 0, "left": 0}
	# Dicionario de quantidade de cada direcao de movimento inicial
	move_quantity = {"up": 0, "down": 0, "right": 0, "left": 0}
	
	# Loop principal que cria todos os clones
	for c in range(clones):
		# Cria o clone e salva a direcao de movimento inicial e seu score ao acabar o jogo
		first_move, score = mc_clone(board, moves_limit)
		# Aumenta em um a quantidade da direcao de movimento inicial
		move_quantity[first_move] += 1
		# Aumenta o score da direcao de movimento inicial
		move_scores[first_move] += score
		
	# Percorre as 4 direcoes de movimento
	for move in MOVE_NAMES:
		# Se houve algum movimento nesta direcao
		if move_quantity[move] > 0:
			# Tira a media do score para essa direcao
			move_scores[move] = move_scores[move]/move_quantity[move]
			
	# Salva a direcao com maior score
	best_move = max(move_scores, key=move_scores.get)
	
	return best_move