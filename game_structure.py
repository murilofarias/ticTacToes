import pygame
import player

# Initializing Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

#screen
WIDTH = 300
ROWS = 3
win = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("TicTacToe")

# Images
X_IMAGE = pygame.transform.scale(pygame.image.load("images/x.png"), (80, 80))
O_IMAGE = pygame.transform.scale(pygame.image.load("images/o.png"), (80, 80))


# Fonts'
END_FONT = pygame.font.SysFont('courier', 25)



def quitting():
    pygame.quit()

def display_message(content):
    pygame.time.delay(500)
    win.fill(WHITE)
    end_text = END_FONT.render(content, 1, BLACK)
    win.blit(end_text, ((WIDTH - end_text.get_width()) // 2, (WIDTH - end_text.get_height()) // 2))
    pygame.display.update()
    pygame.time.delay(3000)


def render(game_array, symbols_repre_image):
    win.fill(WHITE)
    game_array.draw_grid()

    # Drawing X's and O's
    game_array.draw_symbols(symbols_repre_image)

    pygame.display.update()


def store_play(play):
    with open('plays.txt', 'a') as playsFile:
        for move in play:
            playsFile.write(str(move))
        playsFile.write('\n')

def gameloop(computer_begins):

    x_symbol = Symbol('x', X_IMAGE)
    o_symbol = Symbol('o', O_IMAGE)
    
    print('1')
    user = player.User(not computer_begins, x_symbol, 'User')
    #computer = player.Computer(computer_begins, o_symbol)
    computer = player.Computer(computer_begins, o_symbol)
    #the current game's turn
    turn = 0
    #game_array stores the current's game situation and the centre position of each square
    game_array = Game_array()
    #variable to control if the gameloop continues running or not
    run = True
    print('2')

    players = {user.player_id: user, computer.player_id: computer}
    symbols_repre_image = {user.symbol.representation: user.symbol.image, computer.symbol.representation: computer.symbol.image}
    #keeps track which player we are referring in the turn and initializes it.
    current_player_id = None
    if user.isYourTurn:
        current_player_id = user.player_id
    else:
        current_player_id = computer.player_id
    
    print('3')
    while run:
        #keeps track if the turn will be changed in this loop after a valid action by some player
        change_turn = False

        #Queries for some action from the player in his own turn
        if players[current_player_id].type == 'User':
            # User player
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    change_turn = players[current_player_id].click(game_array)
        else:
            # Computer player
            change_turn = players[current_player_id].logic(game_array, turn)
            pygame.time.delay(500)
        print('4')
        render(game_array, symbols_repre_image)

        #checks if someone has won or the game ended in a draw
        if game_array.has_won():
                end_message = players[current_player_id].name + ' has won!'
                store_play(players[current_player_id].play)
                break
        elif game_array.has_drawn():
            end_message = "It's a draw!"
            break
        #change the the current player playing
        if change_turn:
            next_player_id = None
            for player_id in players:
                if current_player_id != player_id:
                    next_player_id = player_id
            current_player_id = next_player_id
            turn += 1

    #displays end message
    display_message(end_message)

class Symbol:
    def __init__(self, representation, image):
        self.representation = representation
        self.image = image

class Game_array:
    def __init__(self, grid=None):
        if grid == None:                       
            self.initialize_grid()
        else:
            self.grid = grid

    def draw_symbols(self, symbols_repre_image):
        for row in self.grid:
            for square in row:
                if square[2] != '':
                    x = square[0]
                    y = square[1]
                    IMAGE = symbols_repre_image[square[2]]
                    win.blit(IMAGE, (x - IMAGE.get_width() // 2, y - IMAGE.get_height() // 2))
    
    def draw_grid(self):
        gap = WIDTH // ROWS

        # Starting points
        x = 0
        y = 0

        for i in range(ROWS):
            x = i * gap

            pygame.draw.line(win, GRAY, (x, 0), (x, WIDTH), 3)
            pygame.draw.line(win, GRAY, (0, x), (WIDTH, x), 3)

    
    def initialize_grid(self):
        dis_to_cen = WIDTH // ROWS // 2

        # Initializing the array
        self.grid = [[None, None, None], [None, None, None], [None, None, None]]

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                x = dis_to_cen * (2 * j + 1)
                y = dis_to_cen * (2 * i + 1)

                # Adding centre coordinates
                self.grid[i][j] = (x, y, '', True)
    
    def markSymbolInSquare(self, symbol, row, col):

        #xCentre and yCentre are the coordinates of square's centre
        xCentre = self.grid[row][col][0]
        yCentre = self.grid[row][col][1]
        self.grid[row][col] = (xCentre, yCentre, symbol.representation, False)

    # Checking if someone has won
    def has_won(self):
    # Checking rows
        for row in range(len(self.grid)):
            if (self.grid[row][0][2] == self.grid[row][1][2] == self.grid[row][2][2]) and self.grid[row][0][2] != '':
                return True

        # Checking columns
        for col in range(len(self.grid)):
            if (self.grid[0][col][2] == self.grid[1][col][2] == self.grid[2][col][2]) and self.grid[0][col][2] != '':
                return True

        # Checking main diagonal
        if (self.grid[0][0][2] == self.grid[1][1][2] == self.grid[2][2][2]) and self.grid[0][0][2] != '':
            return True

        # Checking reverse diagonal
        if (self.grid[0][2][2] == self.grid[1][1][2] == self.grid[2][0][2]) and self.grid[0][2][2] != '':
            return True
    
    def has_drawn(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j][2] == '':
                    return False

        return True