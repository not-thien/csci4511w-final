# CSCI4511W Spring 2023 Final Project

## Contributors

- Jerome Schreiber
- Vuong DoVu
- Thien Nguyen

## Goal:

Create a Quordle AI bot using different model search methodology taught in class, in addition with incorporation of information entropy techniques. Then we test and compare the performance of the Quordle bots, using metrics of computation speed, success rates, and number of guesses used.

## Setup:

big poggers!

## Libraries and Open Source Software Used

1. [Wordle Competition](https://github.com/Kinkelin/WordleCompetition)
2. Python numpy
3. Ur mom

## Experiment

Using the same word bank that Wordle has, we ran each of our bots through a modified version of the Wordle competition. The competition was modified to play numerous quordle games

## Results

| Nr  | AI                 | Avg. Computing Speed | Points per round | Success rate |
| --- | ------------------ | -------------------- | ---------------- | ------------ |
| 1   | OutcomeBasedAI     | 10s                  | 3.816            | 100.0%       |
| 2   | EntropyAI          | 5s                   | 4.091            | 100.0%       |
| 3   | RubzipAI           | 5s                   | 4.569            | 97.2%        |
| 4   | LetterPopularityAI | 5s                   | 4.653            | 93.6%        |
| 5   | BruugleAI          | 5s                   | 6.120            | 97.0%        |
| 6   | MonkeyAI           | 5s                   | 10.000           | 0.0%         |
