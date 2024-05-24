from smv_writer import SMVWriter, dictonary

class SMVWriterIterative(SMVWriter):
    def __init__(self, board_path=None, specs_path=None, board=None):
        super().__init__(board_path, specs_path, board)

        self.box_y, self.box_x = self.get_first_box() # Position of the tracked box

    # Modify the vars for the SMV file
    def add_var(self):
        super().add_var()

        self.content += f'\n\tbox_y: 0..{self.n - 1};'\
                        f'\n\tbox_x: 0..{self.m - 1};'

    # Modify the vars for the SMV file
    def add_init(self):
        super().add_init()

        # Init box position
        self.content += f'\n\tinit(box_y) := {self.box_y};'\
                        f'\n\tinit(box_x) := {self.box_x};'

    # Modify the vars for the SMV file
    def add_transitions(self):
        super().add_transitions()

        # If the keeper moved to the box and not on edge, move box x position
        self.content += f'\n\tnext(box_x) := case'\
                        f'\n\t\t(next(turn) = r) & (x = box_x - 1) & (y = box_y) & (box_x < m - 1) : box_x + 1;'\
                        f'\n\t\t(next(turn) = l) & (x = box_x + 1) & (y = box_y) & (box_x > 0) : box_x - 1;'\
                        f'\n\t\tTRUE : box_x;'\
                        f'\n\tesac;\n'

        # If the keeper moved to the box and not on edge, move box y position
        self.content += f'\n\tnext(box_y) := case'\
                        f'\n\t\t(next(turn) = u) & (y = box_y + 1) & (x = box_x) & (box_y > 0) : box_y - 1;'\
                        f'\n\t\t(next(turn) = d) & (y = box_y - 1) & (x = box_x) & (box_y < n - 1) : box_y + 1;'\
                        f'\n\t\tTRUE : box_y;'\
                        f'\n\tesac;\n'
    
    # Modify the done for the SMV file
    def add_done(self):
        self.content += f'\n\tdone := '
        for i in range(self.n):
            for j in range(self.m):
                # If the box became a box on target
                self.content += f'((box_x = {j}) & (box_y = {i}) & (v_{i}{j} = star))'
                if (i != self.n - 1) | (j != self.m - 1):
                    self.content += f' | '
                else:
                    self.content += ';\n'

    # Get position of the box in the board
    def get_first_box(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == '$':
                    return (i, j)
                    
        return (-1, -1)