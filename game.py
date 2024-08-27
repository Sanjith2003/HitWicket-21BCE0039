class Character:
    def __init__(self, name, char_type, position, player):
        self.name = name
        self.type = char_type
        self.position = position
        self.player = player

    def get_possible_moves(self, board):
        possible_moves = []
        if self.type == 'P':
            possible_moves = ['L', 'R', 'F', 'B']
        elif self.type == 'H1':
            possible_moves = ['L', 'R', 'F', 'B']
        elif self.type == 'H2':
            possible_moves = ['FL', 'FR', 'BL', 'BR']
        return [move for move in possible_moves if self.move(move, board)]

    def move(self, direction, board):
        row, col = self.position
        if self.type == 'P':
            return self.move_pawn(direction, row, col, board)
        elif self.type == 'H1':
            return self.move_hero1(direction, row, col, board)
        elif self.type == 'H2':
            return self.move_hero2(direction, row, col, board)
        return None

    def move_pawn(self, direction, row, col, board):
        moves = {
            'L': (0, -1),
            'R': (0, 1),
            'F': (-1, 0),
            'B': (1, 0),
        }
        if direction in moves:
            d_row, d_col = moves[direction]
            new_row, new_col = row + d_row, col + d_col
            if 0 <= new_row < 5 and 0 <= new_col < 5:
                if board.grid[new_row][new_col] == '' or board.grid[new_row][new_col][0] != self.player:
                    if self.update_position(new_row, new_col, board):
                        return (new_row, new_col)  # Return the new position as a tuple
        return None

    def move_hero1(self, direction, row, col, board):
        moves = {
            'L': (0, -2),
            'R': (0, 2),
            'F': (-2, 0),
            'B': (2, 0),
        }
        if direction in moves:
            d_row, d_col = moves[direction]
            new_row, new_col = row + d_row, col + d_col
            if 0 <= new_row < 5 and 0 <= new_col < 5:
                if board.grid[new_row][new_col] == '' or board.grid[new_row][new_col][0] != self.player:
                    if self.update_position(new_row, new_col, board, kill_opponent=True):
                        return (new_row, new_col)  # Return the new position as a tuple
        return None

    def move_hero2(self, direction, row, col, board):
        moves = {
            'FL': (-2, -2),
            'FR': (-2, 2),
            'BL': (2, -2),
            'BR': (2, 2),
        }
        if direction in moves:
            d_row, d_col = moves[direction]
            new_row, new_col = row + d_row, col + d_col
            if 0 <= new_row < 5 and 0 <= new_col < 5:
                if self.update_position(new_row, new_col, board, kill_opponent=True):
                    return (new_row, new_col)  # Return the new position as a tuple
        return None

    def update_position(self, new_row, new_col, board, kill_opponent=False):
        if board.grid[new_row][new_col] != '' and board.grid[new_row][new_col][0] != self.player:
            if kill_opponent:
                board.remove_character(board.grid[new_row][new_col])
        board.grid[self.position[0]][self.position[1]] = ''
        board.grid[new_row][new_col] = self.name
        self.position = (new_row, new_col)
        return True


class Board:
    def __init__(self):
        self.grid = [['' for _ in range(5)] for _ in range(5)]
        self.characters = {}

    def place_character(self, character):
        row, col = character.position
        self.grid[row][col] = character.name
        self.characters[character.name] = character

    def get_character_by_name(self, name):
        return self.characters.get(name)

    def move_character(self, char_name, direction):
        if char_name in self.characters:
            character = self.characters[char_name]
            if character.move(direction, self):
                return True
        return False

    def is_valid_move(self, char_name, direction):
        if char_name in self.characters:
            character = self.characters[char_name]
            return character.move(direction, self)
        return False

    def remove_character(self, char_name):
        if char_name in self.characters:
            char = self.characters.pop(char_name)
            row, col = char.position
            self.grid[row][col] = ''


class Game:
    def __init__(self):
        self.board = Board()
        self.turn = 'A'
        self.game_over = False
        self.characters_to_place = {
            'A': ['A-P1', 'A-P2', 'A-P3', 'A-H1', 'A-H2'],
            'B': ['B-P1', 'B-P2', 'B-P3', 'B-H1', 'B-H2'],
        }

    def make_move(self, char_name, direction):
        if char_name in self.board.characters:
            character = self.board.get_character_by_name(char_name)
            new_position = character.move(direction, self.board)
            if new_position:
                self.check_game_over()
                self.switch_turn()
                return new_position  # Return the new position
        return None
    
    def switch_turn(self):
        self.turn = 'B' if self.turn == 'A' else 'A'
    
    def check_game_over(self):
        a_alive = any(char.player == 'A' for char in self.board.characters.values())
        b_alive = any(char.player == 'B' for char in self.board.characters.values())
        if not a_alive:
            self.game_over = True
            return "B"
        elif not b_alive:
            self.game_over = True
            return "A"
        return None

    def get_status(self):
        available = {'A': [], 'B': []}
        killed = {'A': [], 'B': []}

        for char in self.board.characters.values():
            if char.player == 'A':
                available['A'].append(char.name)
            else:
                available['B'].append(char.name)

        return {
            'available': available,
            'killed': killed,
            'turn': self.turn  # Add turn information to the status
        }

    def place_initial_characters(self):
        initial_positions = {
            'A': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
            'B': [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]
        }
        for player, chars in self.characters_to_place.items():
            for i, char_name in enumerate(chars):
                char_type = char_name.split('-')[1]
                position = initial_positions[player][i]
                character = Character(char_name, char_type, position, player)
                self.board.place_character(character)
