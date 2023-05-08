# CSCI4511W Spring 2023 Final Project

[Link to our final writeup on Overleaf!](https://blogs.motiondevelopment.top/overleaf)

## Contributors

- Jerome Schreiber
- Vuong DoVu
- Thien Nguyen

## Description:

AI bots solving Quordle games using different search methodologies and techniques including depth-first search, greedy best-first search, predictive information entropy, and random guessing. The four bots' performances were compared against eachother using metrics including computation speed, success rate, and average number of guesses per game.

## Libraries and Dependancies:

1. Python 3
2. Pip (and following libraries)
  - numpy
  - trienode
  - pytablewriter

## Setup

Run: "py .\Competition.py (number of games)"

## Based from the following Wordle Competition

[Wordle Competition](https://github.com/Kinkelin/WordleCompetition)

## Results (1000 Quordle Games)

# Leaderboard
|Rank|      AI       |Success Rate|Starting Word|Avg # of Guesses|Best # of Guesses|         <-- Easiest Words          |Fewest Words Found| <-- Hardest Words (Caps not found) |Total Words Solved|Avg Words Solved|Time Per Round|   Author   |
|----|---------------|------------|-------------|----------------|-----------------|------------------------------------|------------------|------------------------------------|-------------------|-----------------|--------------|------------|
|1   |EntropyAI      |93.0%       |rates        |8.679           |6                |['adept', 'snide', 'mound', 'swamp']|3                 |['abbey', 'place', 'FIZZY', 'rival']|3930               |3.930            |0.774 seconds  |Jerome Schreiber|
|2   |GreedyPopularAI|59.2%       |stond        |11.066          |6                |['solid', 'lease', 'blond', 'humid']|1                 |['woody', 'HATER', 'SOWER', 'HORNY']|3437               |3.437            |0.051 seconds  |Thien Nguyen|
|3   |DfsAI          |36.5%       |aahed        |12.666          |6                |['cloud', 'bused', 'gruel', 'mucus']|0                 |['LAYER', 'TRUST', 'GEEKY', 'JAZZY']|2994               |2.994            |0.063 seconds  |Jerome Schreiber|
|4   |RandomAI       |0.0%        |random       |15.000          |15               |['', '', '', '']                    |0                 |['SIEVE', 'PESKY', 'WRUNG', 'JIFFY']|7                  |0.007            |0.004 seconds  |Example     |
