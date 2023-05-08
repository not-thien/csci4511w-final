import math

from WordleAI import WordleAI, LetterInformation
from WordleJudge import WordleJudge

class EntropyAI(WordleAI):
    def __init__(self, words):
        super().__init__(words)
        self.judge = WordleJudge(words)
        self.solved = [False for _ in range(4)]

    def guess(self, guess_history):
        if(len(guess_history) == 0):
            self.solved = [False for _ in range(4)]
            return "rates" # Hard coded first guess to save computation time
        candidates = [self.words.copy() for _ in range(4)]
        for round in guess_history:
            for boardnum, board in enumerate(round):
                guess = board[1]
                outcome = board[2]
                countWin = 0
                for i, x in enumerate(outcome):
                    if x == LetterInformation.CORRECT:
                        countWin += 1
                        candidates[boardnum] = [x for x in candidates[boardnum] if x[i] == guess[i]]
                    elif x == LetterInformation.PRESENT:
                        candidates[boardnum] = [x for x in candidates[boardnum] if x[i] != guess[i] and guess[i] in x]
                    else:
                        candidates[boardnum] = [x for x in candidates[boardnum] if guess[i] not in x]
                if countWin == 5:
                    self.solved[boardnum] = True
        return self.get_candidate(candidates, self.words)

    def get_author(self):
        return "Vwang"

    """
    This function provides three probability values:
    p[ch][i] -> probability of finding character at i out of all words
    q[ch][i] -> probability of finding character at a location other than i out of all words
    r[ch] -> probability of a character not being in any location out of all words
    """
    def get_probability_distributions(self, words):
        p = {}
        q = {}
        r = {}

        for k in range(26):
            k = chr(k + 97)
            p[k] = [0.0] * 5
            q[k] = [0.0] * 5
            r[k] = 0

        for word in words:
            for i, ch in enumerate(word):
                p[ch][i] += 1

        for word in words:
            for i, ch in enumerate(word):
                for j in range(5):
                    if word[j] != ch:
                        q[ch][j] += 1

        for word in words:
            for ch in set(word):
                r[ch] += 1

        for k in range(26):
            k = chr(k + 97)
            p[k] = [x / len(words) for x in p[k]]
            q[k] = [x / len(words) for x in q[k]]
            r[k] = 1 - r[k] / len(words)

        return p, q, r

    def safe_entropy(self, p):
        return p * math.log(p) if p != 0 else 0

    def get_score(self, word, p, q, r):
        entropy = 0
        frequency = {}
        for ch in word:
            frequency[ch] = frequency.get(ch, 0) + 1
        for i, ch in enumerate(word):
            entropy -= self.safe_entropy(p[ch][i])
            entropy -= self.safe_entropy(q[ch][i]) / frequency[ch] # special assumption when a character is repeated more than once
            entropy -= self.safe_entropy(r[ch])
        return entropy

    def get_candidate(self, words, all_words):
        m = 0
        # Set default case
        for i,x in enumerate(self.solved):
            if not x:
                best = words[i][0]

        p = []
        q = []
        r = []
        for i,solved in enumerate(self.solved):
            if not solved:
                tempP, tempQ, tempR = self.get_probability_distributions(words[i])
                p.append(tempP)
                q.append(tempQ)
                r.append(tempR)
            else:
                p.append([])
                q.append([])
                r.append([])

        # Once the number of words become small enough, restrict search to that. FIX???
        for i, boardWords in enumerate(words):
            if len(boardWords) == 1 and not self.solved[i]:
                self.solved[i] = True
                return boardWords[0]

        for word in all_words:
            s = 0
            for i,solved in enumerate(self.solved):
                if not solved:
                    s += self.get_score(word, p[i], q[i], r[i]) + self.judge.is_wordle_probability(word)
            if s > m:
                m = s
                best = word
        return best
