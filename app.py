#Michael Li
#CS 4613
#Sudoku

def format_input(file):
    """
        Read file, input content as a string
    """
    raw_grid=""
    for line in open(file, "r").readlines():
        for ch in line:
            if ch in "0123456789":
                raw_grid += ch
    return raw_grid

def cross(A, B):
    """
        Cross product of elements in A and elements in B
    """
    return [a+b for a in A for b in B]

class Sudoku():

    def __init__(self, initial_grid):
        self.rows = 'ABCDEFGHI'
        self.cols = '123456789'
        self.setup()
        self.grid = initial_grid
        self.values = self.grid_to_values()

    def setup(self):
        """
            Set up units:
                boxes = each cell of puzzle
                row,col
                square = sub 3x3 grids

                units = row,col,squares
                peers = neighbors, essentially all cells but itself

        """
        self.boxes = [r + c for r in self.rows for c in self.cols]
        self.row = [cross(r, self.cols) for r in self.rows]
        self.col = [cross(self.rows, c) for c in self.cols]
        self.square = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

        self.unitlist = self.row + self.col + self.square
        self.units = dict((s, [u for u in self.unitlist if s in u]) for s in self.boxes) #row,column,squares
        self.peers = dict((s, set(sum(self.units[s],[]))-set([s])) for s in self.boxes) #neighbors

    def grid_to_values(self):
        """
            Convert grid into a dict of {square: char} with '123456789' for empties. ex: A1: "1357"
        """
        grid = {}
        for val, key in zip(self.grid, self.boxes):
            if val == '0':
                grid[key] = '123456789' #all values at start if blank cell
            else:
                grid[key] = val
        return grid

    def values_to_grid(self):
        """
            Convert the dictionary board representation to a string.
        """
        str = []
        for r in self.rows:
            for c in self.cols:
                v = self.values[r + c]
                str.append(v if len(v) == 1 else '0')
        return ''.join(str)

    def remove_digit(self, values, box, digit):
        """
            Remove a digit from domain of a box.
        """
        values[box] = values[box].replace(digit, '')
        return values

    def remove(self,values):
        """
            If box has only 1 number, peers may not have this number.
        """
        for box, value in values.items():
            if len(value) == 1:
                for peer in self.peers[box]:
                    values = self.remove_digit(values, peer, value)
        return values

    def forward_check(self, values):
        """
            After a variable gets 1 value, update peers and check. Terminates if a box has no legal states left.
            Either returns modified values or returns false if invalid domain exists
        """
        made_changes = True
        while made_changes:
            pre_solved_vals = len([box for box in values.keys() if len(values[box]) == 1])
            values = self.remove(values)
            # Check how many boxes have a determined value, to compare
            post_solved_vals = len([box for box in values.keys() if len(values[box]) == 1])
            # If no new values were added, stop the loop.
            made_changes = pre_solved_vals != post_solved_vals
            # If any box have an invalid domain, puzzle has no solution.
            if len([box for box in values.keys() if len(values[box]) == 0]):
                return False
        return values

    def MRV_and_degree(self, values):
        """
            Picks next box to assign using:
                MRV - minimum remaining values -> box with smallest domain
                degree - if tied, pick box with highest number of unassigned neighbors
        """
        min_numoptions = min((len(values[s])) for s in self.boxes if len(values[s]) > 1)
        #print(min_numoptions)
        tieslist = [(box,self.degree(box,values)) for box in values if len(values[box]) == min_numoptions]
        #print("min"+ min(tieslist,key = lambda deg: deg[1])[0])
        return min(tieslist,key = lambda deg: deg[1])[0]

    def degree(self,box,values):
        """
            Returns how many unassigned neighbors for a box : ex - A1 has 4 unassigned neighbors, return 4
        """
        #print(len([neighbor for neighbor in self.peers[box] if len(values[neighbor]) > 1]))
        return len([neighbor for neighbor in self.peers[box] if len(values[neighbor]) > 1])

    def backtrack_search(self, values):
        """
            Does the backtrack algorithm to "guess" next unassigned variable
            MRV and degree heuristic
            ORDER-DOMAIN-VALUES already ordered from smallest to largest
            INFERENCE => used forward_check
        """
        values = self.forward_check(values) #forward checking to reduce again
        if values is False:
            return False # Invalid domain through forward checking
        if all(len(values[s]) == 1 for s in self.boxes):
            return values #All boxes have 1 number => solved
        # SELECT-UNASSIGNED-VARIABLE -> used MRV and highest degree
        box = self.MRV_and_degree(values)
        for value in values[box]: #already ordered from smallest to largest, ex:  A1: 1257 -> ORDER-DOMAIN-VALUES
            #print(values[s])
            new_sudoku = values.copy()
            new_sudoku[box] = value
            guess = self.backtrack_search(new_sudoku)
            if guess:
                return guess

    def display(self):
        """
            Display the values as a 2-D grid.
        """
        width = 1 + max(len(self.values[s]) for s in self.boxes)
        line = 'x'.join(['-'*(width*3)]*3)
        for r in self.rows:
            print(''.join(self.values[r+c].center(width)+('|' if c in '36' else '')
                          for c in self.cols))
            if r in 'CF': print(line)
        print

    def check_solved(self, values):
        """
            If all domains only have 1 possible value, puzzle is solved, else false.
        """
        if values == None: #Forward_checking determines that values state is invalid -> set false, check if false here.
            return False

        for box in values.keys():
            if len(values[box]) != 1:
                return False
        return True

    def make_outputfile(self, solved_status, filename):
        """
            Make output file based on what input user specified. Case sensitive on Windows... not sure about other systems.
        """
        filename = filename.split(".")
        filename[0] = filename[0].replace("Input","Output")
        str_filename = "."
        str_filename = str_filename.join(filename)
        # print(str_filename)

        f = open(str_filename,"w+")

        if(solved_status):
            string_rep = self.values_to_grid()
            ptr = 0
            for row in range(0,9):
                for col in range(0,9):
                    f.write(string_rep[ptr]+ " ")
                    ptr += 1
                f.write("\r\n") #windows compatiable formatting...
        else:
            f.write("Unable to solve this puzzle.")

        f.close()

    def solve(self):
        """
            Solve puzzle:
                1) Forward checking
                2) Backtrack Algo using MRV and degree, forward check again
                3) Check if solved
                4) Print and make output files if solved
        """
        #first step: forward check, if invalid state occurs, terminate
        if(self.forward_check(self.values) == False):
            print("Unable to solve this puzzle.")
            return

        #if forward check solved puzzle, we can stop there
        if self.check_solved(self.values):
            #print("I'm done checking!")
            self.display()
            return
        #if not solved, let's backtrack search
        puzzle.values = self.backtrack_search(self.values)
        #after backtrack_searching, puzzle may or may not be solved depending on if there is a solution
        #we check:
        if self.check_solved(self.values):
            self.display()
        else:
            print("Unable to solve this puzzle.")


if __name__ == "__main__":
    """
        Take user input for puzzle to solve
        Solve puzzle
        Display on screen
        Make outputfile
    """
    user_input = raw_input("What is the name of the puzzle file?\n")
    puzzle = Sudoku(format_input(user_input))
    print
    # print("Grid of possible vals: \n")
    # puzzle.display()
    # print("After a forward check: \n")
    # puzzle.forward_check(puzzle.values)
    # puzzle.display()
    # print("After backtrack_search: \n")
    # puzzle.values = puzzle.backtrack_search(puzzle.values)
    # puzzle.display()
    # print(puzzle.check_solved(puzzle.values))

    puzzle.solve()
    if puzzle.check_solved(puzzle.values):
        puzzle.make_outputfile(True, user_input)
    else:
        puzzle.make_outputfile(False, user_input)
