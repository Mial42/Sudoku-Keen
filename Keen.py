import time
import sys

size = 0
board_length = 0
characters_1_6 = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
characters = []
constraint_sets = [] #Rows and columns
constraint_dictionary = {} #index: rows and columns indices
block_dictionary = {} #Character representation 'A': [Indices]
operator_dictionary = {} #Character representation 'A': (goalnumber, operator) #See about doing this in the read_in_lines method


def generate_characters():
    global characters, size
    characters = characters_1_6[:size]


def generate_constraint_sets_dictionaries():
    global constraint_dictionary
    global constraint_sets
    constraint_sets = []
    constraint_dictionary = {}
    #First, I add the rows to the constraint sets
    for x in range(0, board_length, size):
        row = set(range(x, x + size))
        constraint_sets.append(row)
        for square in row:
            constraint_dictionary[square] = row
    #Next, I want to do the same thing for the columns
    for y in range(0, size):
        col = set(range(y, board_length, size))
        constraint_sets.append(col)
        for square in col:
            constraint_dictionary[square] = constraint_dictionary[square].union(col)
            constraint_dictionary[square].remove(square)


def read_in_lines(filename):
    pick_1 = True
    state = False
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if ' ' not in line: #If this is a new puzzle rather than puzzle info
                global size, board_length
                board_length = len(line)
                if not pick_1:
                    break
                size = int(board_length ** .5)
                #Remember to RESET all the globals
                generate_characters()
                generate_constraint_sets_dictionaries()
                generate_block_dictionary(line)
                state = make_board_representation()
                pick_1 = False
            else:
                temp = line.split(' ')
                operator_dictionary[temp[0]] = (int(temp[1]), temp[2])
    if state:
        new_state = csp_keen(state)
        final_state = ''.join(new_state)
        print(final_state)
    else:
        print("None")


def print_puzzle(board):
    board = convert_unfinished_board_to_string(board)
    for i in range(0, len(board), size):
        x = board[i: i + size]
        temp = '  '.join(x)
        print(temp)


def convert_unfinished_board_to_string(board):
    result = ''
    for char in board:
        if len(char) == 1:
            result = result + char
        else:
            result = result + '-'
    return result


def generate_block_dictionary(line):
    for x in range(board_length):
        if line[x] in block_dictionary:
            block_dictionary[line[x]].append(x)
        else:
            block_dictionary[line[x]] = [x]


def make_board_representation():
    board = []
    my_char_string = ''.join(characters)
    for x in range(board_length):
        board.append(my_char_string)
    return board


def goal_test(state):
    for char in state:
        if len(char) != 1:
            return False
    return True


def csp_keen(state):
    # print(state)
    # print_puzzle(state)
    # print(state)
    # print()
    if goal_test(state):
        return state
    var = get_most_constrained_var(state)
    for val in state[var]:
        new_board = assign(state, var, val)
        checked_board = old_new_forward_looking(new_board, var)
        if checked_board is not None:
            checked_twice_board = propagate_constraints(checked_board)
            if checked_twice_board is not None:
                checked_thrice_board = check_math_blocks(checked_twice_board)
                if checked_thrice_board is not None:
                    result = csp_keen(checked_thrice_board)
                    if result is not None:
                        return result
    return None


def assign(board, index, char):
    temp = list(board)
    temp[index] = char
    return temp


def get_most_constrained_var(board):
    len_smallest_set_of_possible_answers = 9999
    smallest_set_of_possible_answers = 0
    for x in range(board_length):
        string_length = len(board[x])
        if string_length == 2:
            return x
        if string_length > 1:
            if string_length < len_smallest_set_of_possible_answers:
                len_smallest_set_of_possible_answers = string_length
                smallest_set_of_possible_answers = x
    return smallest_set_of_possible_answers


def old_new_forward_looking(board, index_to_look_at):  #Try passing as an argument of the index just changed - this should make things more efficient
    list_of_solved_indices = [index_to_look_at]
    for index in list_of_solved_indices:
        set_of_neighbors = constraint_dictionary[index]
        for neighbor in set_of_neighbors: #Indices of all the neighbors of the solved indices
            if board[index] in board[neighbor]:
                board[neighbor] = board[neighbor].replace(board[index], '')
                string_length = len(board[neighbor])
                if string_length == 0:
                    return None
                if string_length == 1:
                    list_of_solved_indices.append(neighbor)
    return board


def propagate_constraints(board):
    changed = False
    for constraint_set in constraint_sets:
        for character in characters:
            character_count = 0
            index = None
            for square in constraint_set:
                if character in board[square]:
                    index = square
                    character_count = character_count + 1
                    if character == board[square]:
                        break
                if character_count > 1:
                    break
            if character_count == 1:
                board[index] = character
                changed = True
            if character_count == 0:
                return None
    if changed:
        board = forward_looking(board)
    return board


def forward_looking(board):  #Try passing as an argument of the index just changed - this should make things more efficient
    list_of_solved_indices = []
    for x in range(board_length): #Makes a list of solved indiced
        string_length = len(board[x])
        if string_length == 0:
            return None
        if string_length == 1:
            list_of_solved_indices.append(x)
    for index in list_of_solved_indices:
        set_of_neighbors = constraint_dictionary[index]
        for neighbor in set_of_neighbors: #Indices of all the neighbors of the solved indices
            if board[index] in board[neighbor]:
                board[neighbor] = board[neighbor].replace(board[index], '')
                string_length = len(board[neighbor])
                if string_length == 0:
                    return None
                if string_length == 1:
                    list_of_solved_indices.append(neighbor)
    return board


def check_math_blocks(board):
    for block in block_dictionary:
        indices = block_dictionary[block]
        goal_number = operator_dictionary[block][0]
        operator = operator_dictionary[block][1]
        solved = are_indices_solved(board, indices)
        if solved:
            temp = 1
            values = values_at_indices(board, indices)
            larger_number = max(values)
            smaller_number = min(values)
            if operator == '+':
                temp = sum(values)
            elif operator == '-':
                temp = larger_number - smaller_number
            elif operator == 'x':
                for index in indices:
                    temp = temp * int(board[index])
            elif operator == '/':
                temp = larger_number / smaller_number
            if temp != goal_number:
                return None
    return board


def are_indices_solved(board, indices):
    for index in indices:
        if len(board[index]) != 1:
            return False
    return True


def values_at_indices(board, indices):
    temp = []
    for index in indices:
        temp.append(int(board[index]))
    return temp

start = time.perf_counter()
read_in_lines(sys.argv[1])
print(str(time.perf_counter() - start))
# print(operator_dictionary)
# print(constraint_dictionary)
# print(block_dictionary)