"""
Created on Friday May 5 9:30pm CST

@author: Thien Nguyen
"""
from WordleAI import WordleAI, LetterInformation
from WordleJudge import WordleJudge
###################### Letter Tree ##########################
class Node:
    #Construction
    def __init__(self, parent=None):
        self.parent = parent
        self.children = {}
        self.value = None
        self.word = None
        self.level = parent.level + 1 if parent is not None else 0
        self.total_successors = 0

    #Add
    #Recursive function which adds new words to the tree, then updates the number of total sucessors
    def add(self, word, final_word = None):
        #Update the Value of the Current Node
        self.value = word[0]

        if final_word is None:
            final_word = word

        #Add the remaining letters in the word to the tree
        #Base Case: If there are no other letters to add return 1 as parents total successors
        if len(word) == 1:
            #If word length is 1, then we are at level 5 and there are no other valid words
            self.word = final_word
            self.total_successors = 1
            return

        #Trim Word at Head and then add remainder recursively
        #Since we are not in the base case, we know that we have at least 1 more successor than us at this node
        self.total_successors += 1
        word = word[1:]
        next_val = word[0]
        if next_val not in self.children:
            self.children[next_val] = Node(self)

        self.children[next_val].add(word, final_word)

class NodeCollection:
    def __init__(self):
        self.Root = Node(None)
        self.LockedLetters = [None, None, None, None, None, None]
    
    # load all words
    def AddDictionary(self, words):
        for word in words:
            self.Root.add('#' + word)

    # Start the recursion
    def MostLikely(self):
        return self._MostLikely(self.Root)

    # searches through each letter and chooses the letter with most successors
    def _MostLikely(self, search):
        maxSuccessors = float('-inf')
        maxNode = None

        # Find which of the children has the highest number of children
        for node in search.children.values():
            if node is not None and node.total_successors > maxSuccessors:
                maxSuccessors = node.total_successors
                maxNode = node

        # Base Case: We are at the bottom of the tree and need to return the most likely word
        if maxNode.level == 5:
            return maxNode.word
        else:
            return self._MostLikely(maxNode)

###################### Letter Tree Done #####################

class GreedyPopularAI(WordleAI):
    '''
    This AI uses greedy best-first search with a heuristic of letter frequency
    '''
    def __init__(self, words):
        super().__init__(words)
        self.initial_corpus = words
        self.corpus = [words.copy() for _ in range(4)]
        self.judge = WordleJudge()
        self.solved = [False, False, False, False]
        self.board_trees = [NodeCollection() for i in range(4)]
        for bt in self.board_trees:
            bt.AddDictionary(words)
    
    def get_author(self):
        """
        Returns the name of the author
        """
        return "Thien Nguyen"

    def guess(self, guess_history):
        """
        Returns a 5 letter word trying to guess the wordle after filtering the word pools

        Parameters
        ----------
        guess_history : list of lists of tuples (board, guess, result)
            A list of lists of tuples (board, word, result) with result consisting of LetterInformation for each letter on their
            position specifically, for example one previous guess with the guess 'steer' for the word 'tiger':
            [(0, 'steer',[LetterInformation.NOT_PRESENT, LetterInformation.PRESENT,
            LetterInformation.PRESENT, LetterInformation.CORRECT, LetterInformation.CORRECT])]
        """

        if(len(guess_history) == 0):
            self.solved = [False for _ in range(4)]
            return 'stond' # greedy BFS with this heuristic always starts with 'stond'
        word_pools = [pool.copy() for pool in self.corpus]
        word_pools = self.filter_pools(word_pools, guess_history)
        next_guess = self.gbfs(word_pools, guess_history)
        if next_guess[0] != '#': # needed by tree implementation, special case
            return next_guess
        return next_guess[1:]

    def gbfs(self, word_pools, guess_history):
        """
        Resets trees per board and generates guess for next board to be solved

        Parameters
        ----------
        guess_history : list of lists of tuples (board, guess, result)
            A list of lists of tuples (board, word, result) with result consisting of LetterInformation for each letter on their
            position specifically, for example one previous guess with the guess 'steer' for the word 'tiger':
            [(0, 'steer',[LetterInformation.NOT_PRESENT, LetterInformation.PRESENT,
            LetterInformation.PRESENT, LetterInformation.CORRECT, LetterInformation.CORRECT])]

        word_pools: list of strings
            Each string is an accepted Wordle guess
        """
        self.board_trees = [NodeCollection() for i in range(4)]
        for i,word_pool in enumerate(word_pools):
            if not self.solved[i]:
                if len(word_pool) > 1: # build tree based on current word pool for the respective board & generate guess
                    self.board_trees[i].AddDictionary(word_pool)
                    return self.board_trees[i].MostLikely()
                elif len(word_pool) == 1 and not self.has_guessed(word_pool[0], guess_history): # special case where only 1 word left in pool
                    self.solved[i] = True
                    return word_pool[0]
                else: # otherwise, already solved the board
                    self.solved[i] = True
        return "XXXXX"

    def has_guessed(self, guess, guess_history):
        # Checks if guess has already been made
        for r in guess_history:
            for c in r:
                if c[1] == guess:
                    return True
        return False

    def filter_pools(self, word_pools, guess_history):
        """
        Updates each board's word pool based on guess_history

        Parameters
        ----------
        guess_history : list of lists of tuples (board, guess, result)
            A list of lists of tuples (board, word, result) with result consisting of LetterInformation for each letter on their
            position specifically, for example one previous guess with the guess 'steer' for the word 'tiger':
            [(0, 'steer',[LetterInformation.NOT_PRESENT, LetterInformation.PRESENT,
            LetterInformation.PRESENT, LetterInformation.CORRECT, LetterInformation.CORRECT])]
            
        word_pools: list of strings
            Each string is an accepted Wordle guess
        """
        for index, word_pool in enumerate(word_pools):
            for round in guess_history:
                board = round[index]
                present_letters = []
                forbidden_positions = []
                forbidden_letters= []
                correct_positions = []
                for i in range(5):
                    if board[2][i] == LetterInformation.PRESENT:
                        present_letters.append(board[1][i])
                        forbidden_positions.append((board[1][i], i))
                    elif board[2][i] == LetterInformation.NOT_PRESENT:
                        forbidden_letters.append(board[1][i])
                    elif board[2][i] == LetterInformation.CORRECT:
                        correct_positions.append((board[1][i], i))
                # The following 4 fxns were pulled from BruugleAI and are purely used for filtering a word pool
                word_pool = include(word_pool, present_letters)
                word_pool = exclude(word_pool, forbidden_letters)
                word_pool = include_positions(word_pool, correct_positions)
                word_pool = exclude_positions(word_pool, forbidden_positions)
            word_pools[index] = word_pool
        return word_pools

def include(word_list, values):
    filtered_word_list = word_list
    for value in values:
        filtered_word_list = [word for word in filtered_word_list if value in word]
    return filtered_word_list

def exclude(word_list, values):
    filtered_word_list = word_list
    for value in values:
        filtered_word_list = [word for word in filtered_word_list if not value in word]
    return filtered_word_list

def include_positions(word_list, values):
    filtered_word_list = word_list
    for value in values:
        filtered_word_list = [word for word in filtered_word_list if value[0] == word[value[1]]]
    return filtered_word_list

def exclude_positions(word_list, values):
    filtered_word_list = word_list
    for value in values:
        filtered_word_list = [word for word in filtered_word_list if not value[0] == word[value[1]]]
    return filtered_word_list