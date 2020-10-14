import copy
import random
import math
import os.path
import pygame
import game_structure as gs

class Player:
    current_player_id_available = 0
    def __init__(self, isYourTurn, symbol, player_type, name):
        self.isYourTurn = isYourTurn
        self.symbol = symbol
        self.play = []
        self.type = player_type
        self.player_id = Player.current_player_id_available
        self.name = name
        Player.current_player_id_available += 1

                    
class User(Player):
    def __init__(self,isYourTurn, symbol, name):
        super().__init__(isYourTurn, symbol, 'User', name)
        self.name = name

    def click(self, game_array):
        # Mouse position
        m_x, m_y = pygame.mouse.get_pos()

        for i in range(len(game_array.grid)):
            for j in range(len(game_array.grid[i])):
                x, y, char, can_play = game_array.grid[i][j]

                # Distance between mouse and the centre of the square
                dis = math.sqrt((x - m_x) ** 2 + (y - m_y) ** 2)

                # If it's inside the square
                if dis < gs.WIDTH // gs.ROWS // 2 and can_play:
                    game_array.markSymbolInSquare(self.symbol, i, j)
                    self.play.append((i,j))
                    return True


class Computer(Player):
    def __init__(self, isYourTurn, symbol):
        super().__init__(isYourTurn, symbol, 'Computer', 'Computer')
        
        self.known_plays = []
        self.discarded_known_plays_indeces = []

        self.plan = None #this must be a list
        self.plan_failed = False
        if os.path.isfile('plays.txt'):
            with open('plays.txt', 'r') as playsFile:
                lines = playsFile.readlines()
                for line in lines:
                    isRow = True
                    play = [] 
                    self.known_plays.append(play)
                    row = None
                    col = None
                    for character in line:
                        if character.isnumeric():
                            if isRow:
                                row = int(character)
                                isRow = False
                            else:
                                col = int(character)
                                play.append((row, col))
                                isRow = True

    #adapts the plan to the current game's situation and return True  if the plan is well adapted to win
    def adaptsThePlan(self, game_array):
        #if the square in the plan isn't empty, put it in the adaptedPlan list
        adaptedPlan_1 = [ square for square in self.plan if game_array.grid[square[0]][square[1]][3] ]

        for last_index_square in range(1, len(adaptedPlan_1)+1):
            virtual_game_array = gs.Game_array(copy.deepcopy(game_array.grid))
            adaptedPlan_1_copy = copy.deepcopy(adaptedPlan_1)
            adaptedPlan_2 = adaptedPlan_1_copy[: last_index_square]
            for square in adaptedPlan_2:
                x = virtual_game_array.grid[square[0]][square[1]][0]
                y = virtual_game_array.grid[square[0]][square[1]][1]
                virtual_game_array.grid[square[0]][square[1]] = (x,y, self.symbol, False)
            if virtual_game_array.has_won():
                self.plan = adaptedPlan_2
                return True
        return False

    #evaluates if the adapted current plan is possible
    def isThePlanPossibleNow(self, turn):
            return  turn + 2*(len(self.plan)-1) <= 8
    
    def choose_square(self, game_array, turn):
        #if there is current plan and the current plant hasn't failed
        if self.plan != None and not self.plan_failed:
            #adapts the plan to the current game's situation
            winnable = self.adaptsThePlan(game_array)
            #test if the current plan can be executed to achieve victory in time
            if winnable and self.isThePlanPossibleNow(turn) :
                row, col = self.plan[0]
                return row, col

        #determines which plays are possible by their indices discarding all that are stored in computer.discarded_known_plays_indices
        computer_plays_known_possible_indeces = [index for index in range(len(self.known_plays)) if index not in self.discarded_known_plays_indeces]

        #determines how many possible plays the computer still know
        num_known_possible_plays = len(computer_plays_known_possible_indeces)
        #sees if there is no one left and then chooses a square randomly
        if num_known_possible_plays == 0:
            row = random.randint(0,2)
            col = random.randint(0,2)
            return row, col

        #chooses randomly the order in which it will try the possible plays
        try_play_indices_order = random.sample(computer_plays_known_possible_indeces, k=num_known_possible_plays)
            
        #tries in order each play referring to them by their index in computer.known_plays
        for index in try_play_indices_order:
            #estabilishes the computer plan to be the play using index in computer.known_plays
            self.plan = self.known_plays[index]
            #adapts the plan to the current game's situation
            winnable = self.adaptsThePlan(game_array)
            #test if the plan is possible in the current situation of the game and, then, if it is possible, chooses the square by the plan 
            if winnable and self.isThePlanPossibleNow(turn):
                row, col = self.plan[0]
                return row, col
            else:
                #discard the plan by its index in computer.known_plays, so, next time, this plan won't be included and tested again
                self.discarded_known_plays_indeces.append(index)

        #if no plans are possible, all will be discarded, then chooses square randomly 
        self.plan = None
        row = random.randint(0,2)
        col = random.randint(0,2)
        return row, col

    def logic(self, game_array, turn):
        valid_play = False
        while not valid_play:
            row, col = self.choose_square(game_array, turn)
            #validates if the square located at the row and col specified is empty or not by the game_array variable
            can_play = game_array.grid[row][col][3]
            if can_play:
                game_array.markSymbolInSquare(self.symbol, row, col)
                self.plan_failed = False
                self.play.append( (row, col) )
                valid_play = True
            else:
                self.plan_failed = True 
        return True