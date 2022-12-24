import sys
import time
#cool_list_trick = ['content'] * 70
characters_1_16 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G']
characters = []
size = 0
height = 0
width = 0
board_length = 0
constraint_dictionary = {}
constraint_sets = []


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


def convert_list_to_string(board):
    if board is None:
        return None
    line = ''.join(board)
    return line


def generate_characters(my_size):
    global characters
    characters = characters_1_16[:my_size]


def read_in_files(filename):
    with open(filename) as f:
        x = 0
        for line in f:
            #if x != 150 and x != 269:
            line = line.strip()
            global size, board_length
            board_length = len(line)
            size = int(board_length ** .5)
            generate_characters(size)
            global width, height  #Subblock width and height
            width, height = get_block_width_and_height()
            generate_constraint_sets_and_dictionary(line)
            state = make_board_representation(line)
            #print(str(x) + "    " + str(size))
            new_state = old_csp_backtracking_with_forward_looking_and_constraint_propagation(state)
            #print(str(x))
            new_line = convert_list_to_string(new_state)
            print(new_line)


def other_read_in_files(filename):
    with open(filename) as f:
        for line in f:
            line = line.strip()
            global size, board_length
            size = int(len(line) ** .5)
            board_length = len(line)
            generate_characters(size)
            global width, height  #Subblock width and height
            width, height = get_block_width_and_height()
            generate_constraint_sets_and_dictionary(line)
            state = make_board_representation(line)
            new_state = csp_backtracking_with_forward_looking(state)
            new_line = convert_list_to_string(new_state)
            print(new_line)


def assign(board, index, char):
    temp = list(board)
    temp[index] = char
    return temp


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
    global size
    if len(constraint_sets) == 3 * size:
        return
    constraint_dictionary = {}
    constraint_sets = []
    #First, I want to add the rows as sets of indices into the constraint sets list
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
    temporary_block_dict = {} #block coordinate tuple (0, 1) (1, 0) : index numbers
    for z in range(board_length):
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
    for index in range(board_length):
        constraint_dictionary[index].remove(index) #Removing each index from its own set of neighbors



def make_board_representation(line):
    board = []
    my_char_string = ''.join(characters)
    for char in line:
        if char == '.':
            board.append(my_char_string)
        else:
            board.append(char)
    board = forward_looking(board)
    return board

#The problem is with forward_looking: it's returning None when it shouldn't
#On line 12, the problem is with index 20
#I'm removing too many possibilities. Something is wrong.
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


def new_goal_test(board):
    for char in board:
        if len(char) != 1:
            return False
    return True


def old_csp_backtracking_with_forward_looking_and_constraint_propagation(board):
    if new_goal_test(board):
        return board
    var = get_most_constrained_var(board)
    for val in board[var]:
        new_board = assign(board, var, val)
        checked_board = old_new_forward_looking(new_board, var)
        if checked_board is not None:
            checked_twice_board = propagate_constraints(checked_board)
            if checked_twice_board is not None:
                result = old_csp_backtracking_with_forward_looking_and_constraint_propagation(checked_twice_board)
                if result is not None:
                    return result
    return None


def csp_backtracking_with_forward_looking(board):
    if new_goal_test(board):
        return board
    var = get_most_constrained_var(board)
    for val in board[var]:
        new_board = assign(board, var, val)
        checked_board = old_new_forward_looking(new_board, var)
        if checked_board is not None:
            result = csp_backtracking_with_forward_looking(checked_board)
            if result is not None:
                return result
    return None


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


def new_propagate_constraints(board, old_board):
    changed_squares = {}
    changed = False
    for x in range(board_length):
        if board[x] != old_board[x]:
            temp_list = []
            for character in old_board[x]:
                if character not in board[x]:
                    temp_list.append(character)
            changed_squares[x] = temp_list
    for constraint_set in constraint_sets:
        for changed_square in changed_squares:
            if changed_square in constraint_set:
                for character in changed_squares[changed_square]:
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
                        if index in changed_squares:
                            changed_squares[index].append(character)
                        else:
                            changed_squares[index] = character
                    if character_count == 0:
                        return None
    if changed:
        board = forward_looking(board)
    return board


# def n_values_n_squares(board):
#     for n in range(2, size):
#         for constraint_set in constraint_sets:
#


start = time.perf_counter()
read_in_files(sys.argv[1])
end = time.perf_counter()
print(end - start)

# start = time.perf_counter()
# other_read_in_files(sys.argv[1])
# end = time.perf_counter()
# print(end - start)


