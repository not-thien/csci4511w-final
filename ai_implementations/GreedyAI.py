# Importing necessary libraries
from msilib.schema import Error
import nltk
import numpy as np
import pandas as pd
import time
import regex as re
import random

# Implemention requires a priority queue
class PriorityHashQueue:
    def __init__(self):
        self.queue = []

    def returnWordIdx(self, index):
        return self.queue[index].get_word()

    def returnMatchValueIdx(self, index):
        return self.queue[index].get_match_value()

    def returnLength(self):
        return len(self.queue)

    def returnContents(self):
        for i in self.queue:
            print(i.get_word(), i.get_match_value())
        print()

    def returnRandomValue(self):
        return self.queue[random.randint(0, self.returnLength() - 1)]

    def returnTopValue(self):
        return self.queue[0]

    def enqueue(self, word, match_value):
        if (self.returnLength() == 0):
            self.queue.append(HashMap(word, match_value))
        else:
            newEntry = HashMap(word, match_value)
            for i in range(self.returnLength()):
                if (i == self.returnLength() - 1 or match_value == 0):
                    self.queue.append(newEntry)
                    break
                elif (match_value > self.queue[i].get_match_value()):
                    self.queue.insert(i, newEntry)
                    break

    def dequeue(self, index):
        return self.queue.pop(index)



################################################################



# This filter uses list of banned letters to eliminate words from the candidate list (word_list)
def filterWordsBannedLetters(word_list, banned_letters, baseline_answers, misplaced_letters):
    wordHashList = PriorityHashQueue()
    try:
        for i in range(word_list.returnLength()):
            word = word_list.dequeue(0).get_word()
            isBanned = False
            matching_letters = 0  # Contains the number of misplaced letters in the word
            for letter in banned_letters:
                if letter in word:
                    isBanned = True
                    break
            if not isBanned:
                index = 0
                for letter in misplaced_letters:
                    if letter == baseline_answers[index]:
                        matching_letters += 6
                    elif letter in word:
                        matching_letters += 1
                    index += 1
                wordHashList.enqueue(word, matching_letters)
    except Exception as e:
        print(repr(e))
    return wordHashList


# This filter uses regex to eliminate words from the candidate list (word_list)
def filterWordsRegex(word_list, baseline_answers, misplaced_letters):
    wordHashList = PriorityHashQueue()
    try:
        for i in range(word_list.returnLength()):
            word = word_list.dequeue(0).get_word()
            isBanned = False
            matching_letters = 0  # Contains the number of misplaced letters in the word
            if not re.match("".join(baseline_answers), word):
                isBanned = True
            if not isBanned:
                index = 0
                for letter in misplaced_letters:
                    if letter == baseline_answers[index]:
                        matching_letters += 6
                    elif letter in word:
                        matching_letters += 1
                    index += 1
                wordHashList.enqueue(word, matching_letters)
    except Exception as e:
        print(repr(e))
    return wordHashList

# This filter uses regex and list of banned letters to eliminate words from the candidate list (word_list)
def filterWordsBannedLettersRegex(word_list, banned_letters, baseline_answers, misplaced_letters):
    wordHashList = PriorityHashQueue()
    try:
        for i in range(word_list.returnLength()):
            word = word_list.dequeue(0).get_word()
            isBanned = False
            matching_letters = 0  # Contains the number of misplaced letters in the word
            for letter in banned_letters:
                if letter in word:
                    isBanned = True
                    break
            if not isBanned and not re.match("".join(baseline_answers), word):
                isBanned = True
            if not isBanned:
                index = 0
                for letter in misplaced_letters:
                    if letter == baseline_answers[index]:
                        matching_letters += 6
                    elif letter in word:
                        matching_letters += 1
                    index += 1
                wordHashList.enqueue(word, matching_letters)
    except Exception as e:
        print(repr(e))
    return wordHashList

# This function takes a list of words and returns a list of words that contain at least one uppercase letter
def hasUpperCase(word):
    for i in word:
        if i.isupper():
            return True
    return False


# This function takes a word and a dictionary and returns True if the word is in the dictionary
def isWordInDictionary(word, dictionary):
    return word in dictionary


def main():
    # Using heuristics, there are nine words in the English dictionary that has the most vowels
    # "adieu", "audio", "auloi", "aurei", "louie", "miaou", "ouija", "ourie", "uraei"
    first_words = ["adieu", "audio", "auloi", "aurei",
                   "louie", "miaou", "ouija", "ourie", "uraei"]

    # Importing the list of english words and limit the length of the words to five (as in Wordle)
    # All words here is assumed to have a meaning and is a valid answer to a wordle (lowercase).
    raw_english_words = nltk.corpus.words.words()
    print("From NLTK library, there are {} words.".format(
        len(raw_english_words)))  # Returns 236726 words in total
    wordHashList = PriorityHashQueue()
    for word in raw_english_words:
        if len(word) == 5 and not hasUpperCase(word):
            wordHashList.enqueue(word, 0)
    # Returns 8689 five-lettered words in total
    print("From NLTK library, there are {} five-letter words.".format(wordHashList.returnLength()))

    # Giving an option to the user to manually input answer word or let simulation choose one
    answer_word = input(
        "Please enter the answer word (or press enter to let the simulation choose one): ")
    if answer_word == "":
        # Retrieve a random word from the list of english words as the answer
        answer = wordHashList.returnRandomValue().get_word()
        print("The answer is {}".format(answer))
        answer_arr = list(answer)
    else:
        isAnswerValid = False
        while not isAnswerValid:
            if len(answer_word) == 5 and not hasUpperCase(answer_word) and isWordInDictionary(answer_word, raw_english_words):
                isAnswerValid = True
            else:
                answer_word = input("Please enter a valid answer word: ")
        answer = answer_word
        answer_arr = list(answer)

    # Create array for baseline answers as regex and for misplaced but correct letters
    baseline_answers = ['.'] * 5  # This serves as the final answer
    # This serves as a temporary list to store the correct letters that are misplaced
    misplaced_letters = []

    # Create array to safe the letters that are not in the answer
    banned_letters = []

    # Main program
    hasFoundAnswer = False
    num_iterations = 1
    t_start = time.time()
    while not hasFoundAnswer:
        # If the loop starts at zero or baseline_answers are all '.' (wildcards), then the try words from the first_words list
        if num_iterations == 0:
            attempt = first_words.pop(0)
        else:
            # If the loop starts at one or more than baseline_answers are not all '.' (wildcards), then the try words from the wordHashList list
            attempt = wordHashList.dequeue(0).get_word()
        attempt_arr = list(attempt)
        for i in range(5):  # 5 is the length of words in the answer (default)
            if attempt_arr[i] == answer_arr[i]:
                # Replace the '.' with the correct letter
                baseline_answers[i] = attempt_arr[i]
            elif attempt_arr[i] in answer and attempt_arr[i] not in misplaced_letters:
                misplaced_letters.append(attempt_arr[i])
            elif attempt_arr[i] not in banned_letters and attempt_arr[i] not in answer:
                banned_letters.append(attempt_arr[i])
        # If the baseline_answers are all not '.', then the loop is over
        if all(x != '.' for x in baseline_answers):
            hasFoundAnswer = True
            print("\nThe word is {} and the number of iterations are {}".format(
                attempt, num_iterations))
        else:
            # Refresh the wordHashList list. Uncomment necessary lines to use the filterWords function
            # wordHashList = filterWordsBannedLetters(wordHashList, banned_letters, baseline_answers, misplaced_letters)
            # wordHashList = filterWordsRegex(wordHashList, baseline_answers, misplaced_letters)
            wordHashList = filterWordsBannedLettersRegex(wordHashList, banned_letters, baseline_answers, misplaced_letters)
            print("\nCurrent state:")
            print("Attempt word: {}".format(attempt))
            print("Number of iterations: {}".format(num_iterations))
            print("Baseline answer: {}".format(''.join(baseline_answers)))
            print("Misplaced letters: {}".format(''.join(misplaced_letters)))
            print("Banned letters: {}".format(''.join(banned_letters)))
            print("Current length of wordHashList: {}".format(
                wordHashList.returnLength()))
            num_iterations += 1
    t_end = time.time()
    print("\nThe time taken is {:.5f} seconds".format(t_end - t_start))
