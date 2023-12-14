import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Delete all the variables don't have the unary the same as var
        for domain in self.domains:
            # create a set of variables to delete
            deletedVariables = set()
            for x in self.domains[domain]:
                if len(x) != domain.length:
                    deletedVariables.add(x)

            for x in deletedVariables:
                self.domains[domain].remove(x)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = False

        if self.crossword.overlaps[x, y] is not None:
            x_val, y_val = self.crossword.overlaps[x, y]
            # Create a set of variables to delete
            deletedVariables = set()

            for x_var in self.domains[x]:
                consistent = False

                for y_var in self.domains[y]:
                    # If they have the same overlaped word then don't delete
                    if x_var != y_var and x_var[x_val] == y_var[y_val]: 
                        consistent = True

                if consistent == False:
                    deletedVariables.add(x_var)

            # Notify if need to make revision
            if len(deletedVariables) > 0:
                revision = True

            for x_var in deletedVariables:
                self.domains[x].remove(x_var)

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        ac3 = True

        # If `arcs` is None, begin with initial list of all arcs in the problem.
        if arcs == None:
            arcs = []
            for x in self.domains:
                for y in self.domains:
                    if x != y:
                        arcs.append((x, y))


        while arcs != None and len(arcs) != 0:
            x, y = arcs.pop()
            
            if self.revise(x, y) == True:
                # If there's no more variables in domain x, it’s impossible to solve the problem
                if (len(self.domains[x]) == 0):
                    ac3 = False
                    break
                
                for z in self.crossword.neighbors(x):
                    if z != y:
                        arcs.append((z, x))

        return ac3

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        complete = True

        for domain in self.domains.keys():
            if domain not in assignment.keys():
                complete = False
                break

        return complete

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        consistency = True
        values = []

        for key, val in assignment.items():
            # Check all values are distinct
            if (val in values):
                consistency = False
                break
            else:
                values.append(val)
            
            # Check every value is the correct length,
            if (key.length != len(val)):
                consistency = False
                break

            neighbours = self.crossword.neighbors(key)

            # Check there are no conflicts between neighboring variables.
            for neighbor in neighbours:
                x_val, y_val = self.crossword.overlaps[key, neighbor]

                if neighbor in assignment:
                    if assignment[neighbor][y_val] != val[x_val]:
                        consistency = False
                        break

            if consistency == False:
                break

        return consistency

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        values = {}

        for variable in self.domains[var]:
            # If the variable is present in assignment, don't asign the value again
            if variable in assignment:
                continue
            else:
                count = 0

                for neighbor in self.crossword.neighbors(var):
                    if variable in self.domains[neighbor]:
                        count = count + 1

                values[variable] = count      

        return sorted(values, key=lambda key: values[key])
        

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        result = []

        for var in self.domains.keys():
            if var in assignment:
                continue
            else:
                result.append(var)

        # Sort the result list based on MRV and highest degree
        result.sort(key=lambda x: (len(self.domains[x]), -len(self.crossword.neighbors(x))))

        selected = result[0]

        return selected

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If finding the solution, then return it
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value

            if self.consistent(assignment):
                # Start backtracking
                result = self.backtrack(assignment)
                
                if result is not None:
                    return result
            
            assignment.pop(var)
            
        return None      


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
