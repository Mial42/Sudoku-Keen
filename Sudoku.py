import time
from collections import deque
from heapq import heappush, heappop
from random import *
import sys

characters_1_16 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G']
characters = []
size = 0
height = 0
width = 0
constraint_dictionary = {}
constraint_sets = [] #List of sets - each set contains row, column, or block indices


def get_sorted_values(board, square):
    ans = []
    set_of_banned_chars = set()
    for neighbor in constraint_dictionary[square]:
        set_of_banned_chars.add(board[neighbor])
    for char in characters:
        if char not in set_of_banned_chars:
            ans.append(char)
    return ans

def print_puzzle(board):
    for i in range(0, len(board), size):
        x = board[i: i + size]
        temp = '  '.join(x)
        print(temp)


def generate_characters(my_size):
    global characters
    characters = characters_1_16[:my_size]


def recursively_solve_puzzle(board):
    if goal_test(board):
        return board
    square = board.index('.')
    for num in get_sorted_values(board, square):
        new_board = create_new_board(board, square, num)
        result = recursively_solve_puzzle(new_board)
        if result is not None:
            return result
    return None


def goal_test(board):
    if '.' in set(board):
        return False
    return True


def read_in_files(filename):
    with open(filename) as f:
        x = 0
        for line in f:
            if x == 12:
                line = line.strip()
                global size
                size = int(len(line) ** .5)
                generate_characters(size)
                global width, height  #Subblock width and height
                width, height = get_block_width_and_height()
                generate_constraint_sets_and_dictionary(line)
                new_state = recursively_solve_puzzle(line)
                print(new_state)
            x = x + 1


def create_new_board(board, square, num):
    new_board = list(board)
    new_board[square] = num
    new_board = ''.join(new_board)
    return new_board


def coords_to_index(row, col):
    index = row * size + col
    return index


def index_to_coords(index):
    row = index // size
    col = index % size
    return row, col



def get_block_width_and_height():
    if (size ** .5) % 1 == 0:
        return int(size ** .5), int(size ** .5)
    else:
        factors = []
        for factor in range(1, int(size**.5) + 1):
            if size % factor == 0:
                factors.append(factor)
        closest_factor = factors.pop()
        return int(size / closest_factor), int(closest_factor)


def generate_constraint_sets_and_dictionary(board):
    global constraint_sets
    global constraint_dictionary
    #First, I want to add the rows as sets of indices into the constraint sets list
    for x in range(0, len(board), size):
        row = set(range(x, x + size))
        constraint_sets.append(row)
        for square in row:
            constraint_dictionary[square] = row
    #Next, I want to do the same thing for the columns
    for y in range(0, size):
        col = set(range(y, len(board), size))
        constraint_sets.append(col)
        for square in col:
            constraint_dictionary[square] = constraint_dictionary[square].union(col)
    temporary_block_dict = {} #block coordinate tuple (0, 1) (1, 0) : index numbers
    for z in range(len(board)):
        row, col = index_to_coords(z)
        block_row, block_col = row // height, col // width
        if (block_row, block_col) not in temporary_block_dict:
            temporary_block_dict[(block_row, block_col)] = {z}
        else:
            temporary_block_dict[(block_row, block_col)].add(z)
    for block in temporary_block_dict:
        constraint_sets.append(temporary_block_dict[block])
        for index in temporary_block_dict[block]:
            constraint_dictionary[index] = constraint_dictionary[index].union(temporary_block_dict[block])
    for index in range(len(board)):
        constraint_dictionary[index].remove(index) #Removing each index from its own set of neighbors


def get_num_of_each_symbol(state):
    for char in characters:
        print(char + ':' + str(state.count(char)))


read_in_files(sys.argv[1])

#Rows and  columns