import inspect
import os
import random
import importlib
import time

import pytablewriter
import numpy as np
from pytablewriter.style import Style

from WordList import *
from WordleAI import *
from ai_implementations import LetterPopularityAI


class Competition:

    def __init__(self, competitor_directory, wordlist_filename="data/official/combined_wordlist.txt", hard_mode=False):
        self.competitor_directory = competitor_directory
        self.wordlist = WordList(wordlist_filename)
        self.words = self.wordlist.get_list_copy()
        self.competitors = self.load_competitors()
        self.hard_mode = hard_mode

    def load_competitors(self):
        competitors = []
        for file in os.listdir(self.competitor_directory):
            if file.endswith(".py"):
                module = importlib.import_module(self.competitor_directory + "." + file[:-3])
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, WordleAI) and not inspect.isabstract(obj):
                        competitors.append(obj(self.wordlist.get_list_copy()))

        return competitors

    def guess_is_legal(self, guess, guess_history):
        return len(guess) == 5 and guess.lower() == guess and guess in self.words and (
                not self.hard_mode or is_hard_mode(guess, guess_history))

    def play(self, competitor, words):
        guesses = []                             # will become a list of up to 9 words
        successes = [False, False, False, False] # will be 4 Trues if Quordle completed
        guess_history = []                       # will become a list of up to 9 lists of up to 4 3-tuples, each 3-tuple is (whichBoard, guess, guessResultForThatBoard)
                                                 #                                                                          (integer,    str,   list of 5 LetterInformation objects)

        for i in range(9):  # Up to 9 guesses in Quordle 
            # The AI makes a guess, and we check if it's legal
            guess = competitor.guess(guess_history)
            if not self.guess_is_legal(guess, guess_history):
                print("Competitor ", competitor.__class__.__name__, " is a dirty cheater!")
                print("hard_mode: ", self.hard_mode, "guess: ", guess, "guess_history", guess_history)
                print("Competition aborted.")
                quit()

            # Update the AI's progress (guess_history) through all 4 boards in the Quordle game for the guess it just made
            guess_result_all = []
            for board in range(4): # get the result for each board
                if not successes[board]: # but only if the board hasn't been solved yet
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

    def fight(self, rounds, print_details=False, solution_wordlist_filename='data/official/combined_wordlist.txt',
              shuffle=False):
        print("Start tournament")
        result = {}
        success_total = {}
        guesses = {}
        points = {}
        round_words = []

        for competitor in self.competitors:
            result[competitor] = 0
            success_total[competitor] = 0
            guesses[competitor] = []
            points[competitor] = []
        fight_words = WordList(solution_wordlist_filename).get_list_copy()
        start = time.time()
        competitor_times = np.zeros(len(self.competitors))
        for r in range(rounds):
            words = []
            for word in range(4):
                words[word] = random.choice(fight_words) if shuffle else fight_words[r]
            current_time = time.time() - start
            round_words.append(words)
            c = 0
            for competitor in self.competitors:
                print("\rRound", r + 1, "/", rounds, "word =", words, "competitior", c + 1, "/", len(self.competitors),
                      "time", current_time, "/", current_time * rounds / (r + 1), end='')
                competitor_start = time.time()
                successes, round_guesses = self.play(competitor, words)
                round_points = len(round_guesses) if success else 15
                result[competitor] += round_points
                guesses[competitor].append(round_guesses)
                points[competitor].append(round_points)
                if all(successes):
                    success_total[competitor] += 1
                competitor_times[c] += time.time() - competitor_start
                c += 1

        print("\n")
        for i in range(len(competitor_times)):
            print(self.competitors[i].__class__.__name__, "calculation took", "{:.3f}".format(competitor_times[i]), "seconds")

        print("")
        if print_details:
            print("Words: ", round_words)
            print("Guesses: ", guesses)
            print("Points per round: ", points)
            print("")

        print("Competition finished with ", rounds, " rounds, ", len(self.competitors), " competitors and hard_mode = ", self.hard_mode,"\n")
        result = dict(sorted(result.items(), key=lambda item: item[1]))

        writer = pytablewriter.MarkdownTableWriter()
        writer.table_name = "Leaderboard"
        writer.headers = ["Nr", "AI", "Author", "Points per round", "Success rate"]
        for i in range(len(writer.headers)):
            writer.set_style(column=i, style=Style(align="left"))
        writer.value_matrix = []

        placement = 1
        for competitor in result:
            writer.value_matrix.append(
                [placement, competitor.__class__.__name__, competitor.get_author(), result[competitor] / rounds,
                 str(100 * success_total[competitor] / rounds) + "%"])
            placement += 1
        writer.write_table()

# TODO: change this for Quordle
def is_hard_mode(word, guess_history):
    """
    Returns True if the word is a legal guess in hard mode.
    """
    return len(LetterPopularityAI.remaining_options([word], guess_history)) == 1


def main():
    np.set_printoptions(threshold=np.inf)
    np.set_printoptions(suppress=True)

    competition = Competition("ai_implementations", wordlist_filename="data/official/combined_wordlist.txt", hard_mode=False)
    # competition.fight(rounds=1000, solution_wordlist_filename="data/official/shuffled_real_wordles.txt", print_details=False)
    competition.fight(rounds=3, solution_wordlist_filename="data/official/shuffled_real_wordles.txt", print_details=True)

if __name__ == "__main__":
    main()
