import inspect
import os
import random
import importlib
import time
import sys

import pytablewriter
import numpy as np
from pytablewriter.style import Style

from WordList import *
from WordleAI import *


class Competition:

    def __init__(self, competitor_directory, wordlist_filename="data/official/combined_wordlist.txt"):
        self.competitor_directory = competitor_directory
        self.wordlist = WordList(wordlist_filename)
        self.words = self.wordlist.get_list_copy()
        self.competitors = self.load_competitors()

    def load_competitors(self):
        competitors = []
        for file in os.listdir(self.competitor_directory):
            if file.endswith(".py"):
                module = importlib.import_module(self.competitor_directory + "." + file[:-3])
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, WordleAI) and not inspect.isabstract(obj):
                        competitors.append(obj(self.wordlist.get_list_copy()))

        return competitors

    def guess_is_legal(self, guess):
        print("\nGUESS:" + str(guess))
        return len(guess) == 5 and guess.lower() == guess and guess in self.words

    def play(self, competitor, words):
        guesses = []                             # will become a list of up to 9 words
        successes = np.array([False, False, False, False]) # will be 4 Trues if Quordle completed
        guess_history = []                       # will become a list of up to 9 lists of up to 4 3-tuples, each 3-tuple is (whichBoard, guess, guessResultForThatBoard)
                                                 #                                                                          (integer,    str,   list of 5 LetterInformation objects)

        for i in range(9):  # Up to 9 guesses in Quordle 
            # The AI makes a guess, and we check if it's legal
            guess = competitor.guess(guess_history)
            if not self.guess_is_legal(guess):
                print("Competitor ", competitor.__class__.__name__, " is a dirty cheater!")
                print("guess: ", guess, "guess_history", guess_history)
                print("Competition aborted.")
                quit()

            # Update the AI's progress (guess_history) through all 4 boards in the Quordle game for the guess it just made 
            guess_result_all = []
            for board in range(4): # get the result for each board
                # if not successes[board]: # but only if the board hasn't been solved yet
                guess_result_per_board = [] # a list of 5 LetterInformation objects
                for c in range(5): # check each character in the 5-letter guess
                    if guess[c] not in words[board]:
                        guess_result_per_board.append(LetterInformation.NOT_PRESENT)
                    elif words[board][c] == guess[c]:
                        guess_result_per_board.append(LetterInformation.CORRECT)
                    else:
                        guess_result_per_board.append(LetterInformation.PRESENT)
                guess_result_all.append((board, guess, guess_result_per_board))

                if guess == words[board]:
                    successes[board] = True
                    
            # Update guess_history for the AI's guess
            guess_history.append(guess_result_all)
            guesses.append(guess)
            if all(successes):
                break
        return successes, guesses

    def fight(self, rounds, print_details=False, solution_wordlist_filename='data/official/combined_wordlist.txt'):
        print("Start tournament")
        result = {}
        success_total = {}
        partial_solves = {}
        guesses = {}
        points = {}
        times = {}
        round_words = []
        minScore = {}
        minSuccesses = {}
        hardestWords = {}
        easiestWords = {}
        startingWord = ["rates","stond","aahed","random"]

        for i, competitor in enumerate(self.competitors):
            result[competitor] = 0
            success_total[competitor] = 0
            partial_solves[competitor] = 0            
            guesses[competitor] = []
            points[competitor] = []
            times[competitor] = 0.0
            minScore[competitor] = 15
            minSuccesses[competitor] = 4
            hardestWords[competitor] = ["" for x in range(4)]
            easiestWords[competitor] = ["" for x in range(4)]

        fight_words = WordList(solution_wordlist_filename).get_list_copy()
        for r in range(rounds):
            words = []
            for i in range(4):
            # setup the quordle words the bots are trying to guess
                words.append(random.choice(fight_words))
            round_words.append(words)
            for c, competitor in enumerate(self.competitors):
                print("\rRound", r + 1, "/", rounds, "word =", words, "competitior", c + 1, "/", len(self.competitors))

                # Play and Time Game
                competitor_start = time.time()
                successes, round_guesses = self.play(competitor, words)
                times[competitor] += time.time() - competitor_start

                # Track round score
                round_points = len(round_guesses) if all(successes) else 15

                # Track best round score and words
                if all(successes) and len(round_guesses) < minScore[competitor]:
                    minScore[competitor] = len(round_guesses)
                    easiestWords[competitor] = words

                # Track worst successes and words
                if not all(successes) and successes.sum() < minSuccesses[competitor]:
                    minSuccesses[competitor] = successes.sum()
                    hardestWords[competitor] = words.copy()
                    for i, success in enumerate(successes):
                        if not success:
                            hardestWords[competitor][i] = hardestWords[competitor][i].upper()
                
                # Track partial wins
                for solve in successes:
                    if solve: partial_solves[competitor] += 1

                # Track other stats
                result[competitor] += round_points
                guesses[competitor].append(round_guesses)
                points[competitor].append(round_points)
                if all(successes):
                    success_total[competitor] += 1

        print("")
        if print_details:
            print("Words: ", round_words)
            print("Guesses: ", guesses)
            print("Points per round: ", points)
            print("")

        print("Competition finished with ", rounds, " rounds, ", len(self.competitors), " competitors\n")
        result = dict(sorted(result.items(), key=lambda item: item[1]))

        writer = pytablewriter.MarkdownTableWriter()
        writer.table_name = "Leaderboard"
        writer.headers = ["Rank", "AI", "Success Rate", "Starting Word", "Avg # of Guesses", "Best # of Guesses", "<-- Easiest Words", "Fewest Words Found", "<-- Hardest Words (Caps not found)", "Total Boards Solved", "Avg Boards Solved", "Time Per Round", "Author"]
        for i in range(len(writer.headers)):
            writer.set_style(column=i, style=Style(align="left"))
        writer.value_matrix = []

        for i, competitor in enumerate(result):
            writer.value_matrix.append(
                [i + 1, competitor.__class__.__name__, str(100 * success_total[competitor] / rounds) + "%", startingWord[i], 
                 result[competitor] / rounds, minScore[competitor], easiestWords[competitor], minSuccesses[competitor], hardestWords[competitor], 
                 str(partial_solves[competitor]), str(partial_solves[competitor] / rounds), "{:.3f}".format(times[competitor] / rounds) + "seconds", competitor.get_author()])
        writer.write_table()

def main():
    np.set_printoptions(threshold=np.inf)
    np.set_printoptions(suppress=True)

    competition = Competition("ai_implementations_quordle", wordlist_filename="data/official/combined_wordlist.txt")
    competition.fight(rounds=int(sys.argv[1]), solution_wordlist_filename="data/official/shuffled_real_wordles.txt", print_details=True)

if __name__ == "__main__":
    main()
