"""
Created on Friday May 5 4:13pm CST

@author: Jerome
"""

from WordleAI import WordleAI, LetterInformation
from WordleJudge import WordleJudge
from TrieNode import Trie

class DfsAI(WordleAI):
    '''
    This AI uses a set of fixed guesses to narrow down the exact letters for the final guess.
    '''
    def __init__(self, words):
        super().__init__(words)
        self.initial_corpus = words
        self.corpus = [words.copy() for _ in range(4)]
        self.judge = WordleJudge()
        self.solved = [False for _ in range(4)]
    
    def guess(self, guess_history):
        if(len(guess_history) == 0):
            self.solved = [False for _ in range(4)]
            return 'aahed'
        word_pools = [pool.copy() for pool in self.corpus]
        word_pools = self.filter_pools(word_pools, guess_history)
        next_guess = self.dfs(word_pools, guess_history)
        return next_guess
    
    def has_guessed(self, guess, guess_history):
        for r in guess_history:
            for c in r:
                if c[1] == guess:
                    return True
        return False

    def dfs(self, word_pools, guess_history):
        tree = Trie()
        for i,word_pool in enumerate(word_pools):
            if not self.solved[i]:
                if len(word_pool) > 1:
                    tree.build(word_pool)
                    return tree.leftmost_word()
                elif len(word_pool) == 1 and not self.has_guessed(word_pool[0], guess_history):
                    self.solved[i] = True
                    return word_pool[0]
                else:
                    self.solved[i] = True
        return "abort"
    
    def get_author(self):
        return "Jerome"
    
    def filter_pools(self, word_pools, guess_history):
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