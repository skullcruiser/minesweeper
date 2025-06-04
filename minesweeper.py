import itertools
import random

class Minesweeper:
    # Minesweeper game representation

    def __init__(self, height=8, width=8, mines=8):
        # Initialize the Minesweeper board.
        self.height = height
        self.width = width
        self.mines = set()

        # Create an empty board with no mines
        self.board = [[False for _ in range(self.width)] for _ in range(self.height)]

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # Keep track of found mines
        self.mines_found = set()

    def is_mine(self, cell):
        # Checks if a cell contains a mine.
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        # Returns the number of mines adjacent to the given cell.
        count = 0
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) != cell and 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1
        return count

    def won(self):
        # Returns True if all mines have been flagged.
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game.
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        # Initialize a sentence with a set of cells and a count.
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        # Check equality of sentences.
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        # Return a string representation of the sentence.
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        # Identify cells that are definitely mines.
        if len(self.cells) == self.count:
            return set(self.cells)
        return set()

    def known_safes(self):
        # Identify cells that are definitely safe.
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        # Mark a cell as a mine and update the sentence.
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        # Mark a cell as safe and update the sentence.
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:

    def __init__(self, height=8, width=8):
        # Initialize the AI's knowledge base and tracking variables.
        self.height = height
        self.width = width
        self.moves_made = set()  # Cells the AI has already chosen
        self.mines = set()  # Cells known to be mines
        self.safes = set()  # Cells known to be safe
        self.knowledge = []  # Knowledge base (list of sentences)

    def mark_mine(self, cell):
        # Mark a cell as a mine and update all sentences.
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        # Mark a cell as safe and update all sentences.
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        # Update the AI's knowledge base when a safe cell is revealed.

        # Step 1: Mark the cell as a move made and safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Step 2: Get the neighbors of the cell
        newSentence = self.neighboursSentence(cell,count)

        # Step 3: Add a new sentence to the knowledge base
        if newSentence:
            self.knowledge.append(newSentence)

        # Step 4: Update the knowledge base with new information
        self.update_knowledge()

        # Step 5: Infer new sentences by combining existing knowledge
        self.infer_new_sentences()

    def neighboursSentence(self,cell,count):
        row, col = cell
        neighbour_set = set()
        for i in range(-1,2):
            for j in range(-1,2):
                nrow = row + i
                ncol = col + j
                ncell = (nrow, ncol)
                if ncell != cell and 0 <= nrow < self.height and 0 <= ncol < self.width:
                    if ncell in self.mines:
                        count -= 1
                    elif ncell != cell and ncell not in self.mines and ncell not in self.safes:
                        neighbour_set.add(ncell)
        if(neighbour_set):
            return Sentence(neighbour_set,count)  
        else:
            return None

    def update_knowledge(self):
        # Update the knowledge base by marking known mines and safes.
        new_safes = set()
        new_mines = set()

        # Identify new safes and mines
        for sentence in self.knowledge:
            new_safes.update(sentence.known_safes())
            new_mines.update(sentence.known_mines())

        # Mark cells as safe or mines
        for cell in new_safes:
            self.mark_safe(cell)
        for cell in new_mines:
            self.mark_mine(cell)

        # Remove empty sentences
        self.knowledge = [sentence for sentence in self.knowledge if sentence.cells]

    def infer_new_sentences(self):
        # Infer new sentences by comparing subsets of existing sentences.
        inferred = []

        # Compare each pair of sentences
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2 and sentence1.cells < sentence2.cells:
                    # Infer a new sentence by subtracting subsets
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count
                    inferred.append(Sentence(new_cells, new_count))

        # Add inferred sentences and update knowledge
        self.knowledge.extend(inferred)
        self.update_knowledge()

    def make_safe_move(self):
        # Return a safe cell to move to, or None if no safe moves are available.
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        # Return a random cell to move to, avoiding known mines and moves already made.
        choices = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines
        ]
        return random.choice(choices) if choices else None