from itertools import combinations

dictonary = {
    "@": "shtrudel",
    "+": "plus",
    "$": "dollar",
    "*": "star",
    "#": "solamit",
    ".": "dot",
    "-": "minus"
}


class SMVWriter:
    def __init__(self, board_path=None, specs_path=None, board=None):
        if board is None: # Define the board either by path or the board itself
            self.board = self.get_board(board_path)
        else:
            self.board = board
        
        self.specs = self.get_specs(specs_path) # Specifications to check

        self.x, self.y = self.get_coords() # Position of the kepper
        self.n, self.m = len(self.board), len(self.board[0]) # Size of the board

        self.content = '' # Content of SMV file

    # Export the content to the SMV file
    def export_smv(self, path):
        with open(path, 'w') as f:
            f.write(self.content)

    # Writing the content for the SMV file 
    def write_smv(self):
        self.content += 'MODULE main\n'

        self.add_define() # Add the defines
        self.add_var() # Add the vars
        self.add_assign() # Add the assigns
        self.add_specs() # Add the specs

    # Writing the specs for the SMV file
    def add_specs(self):
        for spec in self.specs:
            self.content += f'\n{spec}'

    # Writing the assigns for the SMV file
    def add_assign(self):
        self.content += f'\nASSIGN'

        self.add_init() # Add the inits
        self.add_transitions() # Add the transitions

    # Writing the inits for the SMV file
    def add_init(self):
        for i in range(self.n):
            for j in range(self.m):
                # Init board[i][j] var
                self.content += f'\n\tinit(v_{i}{j}) := {dictonary.get(self.board[i][j])};'
        self.content += '\n'

        # Init possible_up
        self.content += f'\n\tinit(possible_up) := '
        if self.y == 0: # If on edge
            self.content += 'FALSE;'
        elif self.y == 1: # If one square from edge
            self.content += f'!(v_{self.y-1}{self.x} = solamit);'
        else:
            self.content += f'!((v_{self.y-1}{self.x} = solamit) | (((v_{self.y-1}{self.x} = dollar) | (v_{self.y-1}{self.x} = dollar)) & ((v_{self.y-2}{self.x} = dollar) | (v_{self.y-2}{self.x} = dollar) | (v_{self.y-2}{self.x} = solamit))));'

        # Init possible_down
        self.content += f'\n\tinit(possible_down) := '
        if self.y == self.n - 1: # If on edge
            self.content += 'FALSE;'
        elif self.y == self.n - 2: # If one square from edge
            self.content += f'!(v_{self.y+1}{self.x} = solamit);'
        else:
            self.content += f'!((v_{self.y+1}{self.x} = solamit) | (((v_{self.y+1}{self.x} = dollar) | (v_{self.y+1}{self.x} = dollar)) & ((v_{self.y+2}{self.x} = dollar) | (v_{self.y+2}{self.x} = dollar) | (v_{self.y+2}{self.x} = solamit))));'

        # Init possible_right
        self.content += f'\n\tinit(possible_right) := '
        if self.x == self.m - 1: # If on edge
            self.content += 'FALSE;'
        elif self.x == self.m - 2: # If one square from edge
            self.content += f'!(v_{self.y}{self.x+1} = solamit);'
        else:
            self.content += f'!((v_{self.y}{self.x+1} = solamit) | (((v_{self.y}{self.x+1} = dollar) | (v_{self.y}{self.x+1} = dollar)) & ((v_{self.y}{self.x+2} = dollar) | (v_{self.y}{self.x+2} = dollar) | (v_{self.y}{self.x+2} = solamit))));'

        # Init possible_left
        self.content += f'\n\tinit(possible_left) := '
        if self.x == 0: # If on edge
            self.content += 'FALSE;'
        elif self.x == 1: # If one square from edge
            self.content += f'!(v_{self.y}{self.x-1} = solamit);'
        else:
            self.content += f'!((v_{self.y}{self.x-1} = solamit) | (((v_{self.y}{self.x-1} = dollar) | (v_{self.y}{self.x-1} = dollar)) & ((v_{self.y}{self.x-2} = dollar) | (v_{self.y}{self.x-2} = dollar) | (v_{self.y}{self.x-2} = solamit))));'

        # Init turn and kepper position
        self.content += f'\n\tinit(turn) := none;'\
                        f'\n\tinit(x) := {self.x};'\
                        f'\n\tinit(y) := {self.y};\n'

    # Writing the transitions for the SMV file
    def add_transitions(self):
        self.add_possible_transition()
        self.add_turn_transition()
        self.add_x_transition()
        self.add_y_transition()
        self.add_board_transition()

    # Transition board
    def add_board_transition(self):
        for i in range(self.n):
            for j in range(self.m):
                # Transition board[i][j] var

                # If its the kepper, change if moving and depending on target or floor
                self.content += f'\n\tnext(v_{i}{j}) := case'\
                                f'\n\t\t(y = {i}) & (x = {j}) & (v_{i}{j} = shtrudel) & (next(turn) != none) : minus;'\
                                f'\n\t\t(y = {i}) & (x = {j}) & (v_{i}{j} = plus) & (next(turn) != none) : dot;'
                # If there is square to the left, change if the kepper move to here from the left
                if j > 0:
                    self.content += f'\n\t\t(y = {i}) & (x = {j-1}) & ((v_{i}{j} = minus) | (v_{i}{j} = dollar)) & (next(turn) = r) : shtrudel;'\
                                    f'\n\t\t(y = {i}) & (x = {j-1}) & ((v_{i}{j} = dot) | (v_{i}{j} = star)) & (next(turn) = r) : plus;'
                # If the kepper pushed a box from the left, change
                if j > 1:
                    self.content += f'\n\t\t(y = {i}) & (x = {j-2}) & ((v_{i}{j-1} = star) | (v_{i}{j-1} = dollar)) & (v_{i}{j} = minus) & (next(turn) = r) : dollar;'\
                                    f'\n\t\t(y = {i}) & (x = {j-2}) & ((v_{i}{j-1} = star) | (v_{i}{j-1} = dollar)) & (v_{i}{j} = dot) & (next(turn) = r) : star;'
                # If there is square to the right, change if the kepper move to here from the right
                if j < self.m - 1:
                    self.content += f'\n\t\t(y = {i}) & (x = {j+1}) & ((v_{i}{j} = minus) | (v_{i}{j} = dollar)) & (next(turn) = l) : shtrudel;'\
                                    f'\n\t\t(y = {i}) & (x = {j+1}) & ((v_{i}{j} = dot) | (v_{i}{j} = star)) & (next(turn) = l) : plus;'
                # If the kepper pushed a box from the right, change
                if j < self.m - 2:
                    self.content += f'\n\t\t(y = {i}) & (x = {j+2}) & ((v_{i}{j+1} = star) | (v_{i}{j+1} = dollar)) & (v_{i}{j} = minus) & (next(turn) = l) : dollar;'\
                                    f'\n\t\t(y = {i}) & (x = {j+2}) & ((v_{i}{j+1} = star) | (v_{i}{j+1} = dollar)) & (v_{i}{j} = dot) & (next(turn) = l) : star;'
                # If there is square to the up, change if the kepper move to here from the up
                if i > 0:
                    self.content += f'\n\t\t(y = {i-1}) & (x = {j}) & ((v_{i}{j} = minus) | (v_{i}{j} = dollar)) & (next(turn) = d) : shtrudel;'\
                                    f'\n\t\t(y = {i-1}) & (x = {j}) & ((v_{i}{j} = dot) | (v_{i}{j} = star)) & (next(turn) = d) : plus;'
                # If the kepper pushed a box from the up, change
                if i > 1:
                    self.content += f'\n\t\t(y = {i-2}) & (x = {j}) & ((v_{i-1}{j} = star) | (v_{i-1}{j} = dollar)) & (v_{i}{j} = minus) & (next(turn) = d) : dollar;'\
                                    f'\n\t\t(y = {i-2}) & (x = {j}) & ((v_{i-1}{j} = star) | (v_{i-1}{j} = dollar)) & (v_{i}{j} = dot) & (next(turn) = d) : star;'
                # If there is square to the down, change if the kepper move to here from the down
                if i < self.n - 1:
                    self.content += f'\n\t\t(y = {i+1}) & (x = {j}) & ((v_{i}{j} = minus) | (v_{i}{j} = dollar)) & (next(turn) = u) : shtrudel;'\
                                    f'\n\t\t(y = {i+1}) & (x = {j}) & ((v_{i}{j} = dot) | (v_{i}{j} = star)) & (next(turn) = u) : plus;'
                # If the kepper pushed a box from the down, change
                if i < self.n - 2:
                    self.content += f'\n\t\t(y = {i+2}) & (x = {j}) & ((v_{i+1}{j} = star) | (v_{i+1}{j} = dollar)) & (v_{i}{j} = minus) & (next(turn) = u) : dollar;'\
                                    f'\n\t\t(y = {i+2}) & (x = {j}) & ((v_{i+1}{j} = star) | (v_{i+1}{j} = dollar)) & (v_{i}{j} = dot) & (next(turn) = u) : star;'
                # Else, stay the same
                self.content += f'\n\t\tTRUE : v_{i}{j};'\
                                f'\n\tesac;\n'

    # Transition keeper x position
    def add_x_transition(self):
        self.content += f'\n\tnext(x) := case'\
                        f'\n\t\t(next(turn) = r) & (x < m - 1) : x + 1;'\
                        f'\n\t\t(next(turn) = l) & (x > 0) : x - 1;'\
                        f'\n\t\tTRUE : x;'\
                        f'\n\tesac;\n'

    # Transition keeper y position
    def add_y_transition(self):
        self.content += f'\n\tnext(y) := case'\
                        f'\n\t\t(next(turn) = d) & (y < n - 1) : y + 1;'\
                        f'\n\t\t(next(turn) = u) & (y > 0) : y - 1;'\
                        f'\n\t\tTRUE : y;'\
                        f'\n\tesac;\n'

    # Transition turn
    def add_turn_transition(self):
        # If done, don't move
        self.content += f'\n\tnext(turn) := case'\
            f'\n\t\tdone : none;'

        turns = ['u', 'd', 'r', 'l']
        for i in range(4, 0, -1):
            for combination in list(combinations(turns, i)):
                # For each combinations of up, down, right and left 

                flag = False

                # If up, add that only of possible_up
                if 'u' in combination:
                    self.content += f'\n\t\tnext(possible_up) '
                    flag = True

                # If down, add that only of possible_down
                if 'd' in combination:
                    if flag:
                        self.content += f'& '
                    else:
                        self.content += f'\n\t\t'

                    flag = True
                    self.content += f'next(possible_down) '

                # If right, add that only of possible_right
                if 'r' in combination:
                    if flag:
                        self.content += f'& '
                    else:
                        self.content += f'\n\t\t'

                    flag = True
                    self.content += f'next(possible_right) '

                # If left, add that only of possible_left
                if 'l' in combination:
                    if flag:
                        self.content += f'& '
                    else:
                        self.content += f'\n\t\t'

                    flag = True
                    self.content += f'next(possible_left) '

                self.content += ': {' + ', '.join(combination) + ', none};'

        # Else, if no move pissible turn in none
        self.content += f'\n\t\tTRUE : none;'
        self.content += f'\n\tesac;\n'

    # Transition possible up/down/right/left
    def add_possible_transition(self):
        # Transition possible_up
        self.content += f'\n\tnext(possible_up) := case'
        for i in range(self.n):
            for j in range(self.m):
                if i == 0: # If on edge, if this is where the keeper than false
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : FALSE;'
                elif i == 1: # If one square from edge, if this is where the keeper than only if there isn't a wall
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : !((v_{i-1}{j} = solamit));'
                else: # If this is the keeper than only if there isn't a wall or a box that have after her a wall or box
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : !((v_{i-1}{j} = solamit) | (((v_{i-1}{j} = dollar) | (v_{i-1}{j} = star)) & ((v_{i-2}{j} = dollar) | (v_{i-2}{j} = star) | (v_{i-2}{j} = solamit))));'
        # Else, set to False
        self.content += f'\n\t\tTRUE : FALSE;'\
                        f'\n\tesac;\n'

        # Transition possible_down
        self.content += f'\n\tnext(possible_down) := case'
        for i in range(self.n):
            for j in range(self.m):
                if i == self.n - 1: # If on edge, if this is where the keeper than false
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : FALSE;'
                elif i == self.n - 2: # If one square from edge, if this is where the keeper than only if there isn't a wall
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : !((v_{i+1}{j} = solamit));'
                else: # If this is the keeper than only if there isn't a wall or a box that have after her a wall or box
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : !((v_{i+1}{j} = solamit) | (((v_{i+1}{j} = dollar) | (v_{i+1}{j} = star)) & ((v_{i+2}{j} = dollar) | (v_{i+2}{j} = star) | (v_{i+2}{j} = solamit))));'
        # Else, set to False
        self.content += f'\n\t\tTRUE : FALSE;'\
                        f'\n\tesac;\n'
        
        # Transition possible_right
        self.content += f'\n\tnext(possible_right) := case'
        for i in range(self.n):
            for j in range(self.m):
                if j == self.m - 1: # If on edge, if this is where the keeper than false
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : FALSE;'
                elif j == self.m - 2: # If one square from edge, if this is where the keeper than only if there isn't a wall
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : !((v_{i}{j+1} = solamit));'
                else: # If this is the keeper than only if there isn't a wall or a box that have after her a wall or box
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : !((v_{i}{j+1} = solamit) | (((v_{i}{j+1} = dollar) | (v_{i}{j+1} = star)) & ((v_{i}{j+2} = dollar) | (v_{i}{j+2} = star) | (v_{i}{j+2} = solamit))));'
        # Else, set to False
        self.content += f'\n\t\tTRUE : FALSE;'\
                        f'\n\tesac;\n'

        # Transition possible_left
        self.content += f'\n\tnext(possible_left) := case'
        for i in range(self.n):
            for j in range(self.m):
                if j == 0: # If on edge, if this is where the keeper than false
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : FALSE;'
                elif j == 1: # If one square from edge, if this is where the keeper than only if there isn't a wall
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : !((v_{i}{j-1} = solamit));'
                else: # If this is the keeper than only if there isn't a wall or a box that have after her a wall or box
                    self.content += f'\n\t\t(y = {i}) & (x = {j}) : !((v_{i}{j-1} = solamit) | (((v_{i}{j-1} = dollar) | (v_{i}{j-1} = star)) & ((v_{i}{j-2} = dollar) | (v_{i}{j-2} = star) | (v_{i}{j-2} = solamit))));'
        # Else, set to False
        self.content += f'\n\t\tTRUE : FALSE;'\
                        f'\n\tesac;\n'

    # Writing the vars for the SMV file
    def add_var(self):
        self.content += f'\nVAR'\
                        f'\n\tturn: {{u, d, r, l, none}};'\
                        f'\n\tpossible_up: boolean;'\
                        f'\n\tpossible_down: boolean;'\
                        f'\n\tpossible_right: boolean;'\
                        f'\n\tpossible_left: boolean;'\
                        f'\n\ty: 0..{self.n - 1};'\
                        f'\n\tx: 0..{self.m - 1};'

        for i in range(self.n):
            for j in range(self.m):
                self.content += f'\n\tv_{i}{j}: {{shtrudel, plus, dollar, star, solamit, dot, minus}};'
        self.content += '\n'

    # Writing the defines for the SMV file
    def add_define(self):
        self.content += f'\nDEFINE'\
                        f'\n\tn := {self.n}; m := {self.m};'

        self.add_done()

    # Define done
    def add_done(self):
        self.content += f'\n\tdone :='
        for i in range(self.n):
            for j in range(self.m):
                # Each square isn't box on floor
                self.content += f' (v_{i}{j} != dollar)'
                if (i != self.n - 1) | (j != self.m - 1):
                    self.content += f' &'
                else:
                    self.content += ';\n'

    # Find the position of the kepper given the board
    def get_coords(self):
        for y, row in enumerate(self.board):
            for x, col in enumerate(row):
                if col in ["@", "+"]:
                    return (x, y)

        return (-1, -1)

    # Extract specs from txt file
    def get_specs(self, path):
        with open(path, 'r') as f:
            specs = f.readlines()

        return specs

    # Extract board from txt file
    def get_board(self, path):
        board = []
        with open(path, 'r') as f:
            for line in f.readlines():
                if line[-1] == "\n":
                    line = line[:-1]
                row = list(line)
                board.append(row)

        return board