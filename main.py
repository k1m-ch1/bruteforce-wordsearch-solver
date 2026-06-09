import argparse
from functools import reduce
import pprint

parser = argparse.ArgumentParser(description="A brute force crossword solver")

parser.add_argument("crossword", type=str, help="The crossword as a text file")
parser.add_argument("-w", "--wordlist", type=str, help="The worldlist")
parser.add_argument("-m", "--min", type=int, default=0, help="The minimum acceptable word length")

def match_words_in_wordline(wordline, wordset):
    # we'll define a wordline to be a line that may contain words in the wordlist in it
    # returns the matched word, the start index (inclusive), the end index (exclusive), non_reverse_match, reverse match
    matched_words = []
    for i in range(len(wordline)):
        for j in range(i, len(wordline)):
            word_to_check = wordline[i:j]
            non_reversed_matched = list_of_char_to_string(word_to_check) in wordset
            reversed_matched = list_of_char_to_string(list(reversed(word_to_check))) in wordset
            if non_reversed_matched or reversed_matched:
                matched_words.append((word_to_check, i, j, non_reversed_matched, reversed_matched))

    return matched_words

def is_square(array_of_array):
    return all([len(array_of_array) == len(row) for row in array_of_array])

def transpose(array_of_array):
    # assume that it's a square array
    if not is_square(array_of_array):
        raise ValueError("Please enter a square array")

    n = len(array_of_array)
    array_transposed = [[None]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            array_transposed[i][j] = array_of_array[j][i]
    return array_transposed

def list_of_char_to_string(list_of_char):
    if len(list_of_char) == 0:
        return ""
    elif len(list_of_char) == 1:
        return list_of_char[0]
    return reduce(lambda a, b: a + b, list_of_char)

def main():
    args = parser.parse_args()
    with open(args.crossword, 'r') as file:
        crossword_string = file.read()
        crossword = [list(wordline) for wordline in crossword_string.strip().split('\n')]

    with open(args.wordlist, 'r') as file:
        file_as_string = file.read()
        wordset = set([word.strip().lower() for word in file_as_string.split('\n')])
        wordset = set([word for word in wordset if len(word) >= args.min])
    # first, search through the rows
    rows_of_wordline = crossword
    matched_words = []
    for i, row in enumerate(rows_of_wordline):
        matched_words_row = match_words_in_wordline(row, wordset)
        matched_words += [(matched_word[0],
                           (i, matched_word[1]),
                           (i, matched_word[2]),
                           matched_word[3],
                           matched_word[4]) for matched_word in matched_words_row]

    crossword_transposed = transpose(crossword)
    crossword_string = [list_of_char_to_string(r) for r in crossword]
    crossword_transposed_string = [list_of_char_to_string(c) for c in crossword_transposed]
    columns_of_wordline = crossword_transposed
    for i, column in enumerate(columns_of_wordline):
        matched_words_column = match_words_in_wordline(column, wordset)
        matched_words += [(matched_word[0],
                           (matched_word[1], i),
                           (matched_word[2], i),
                           matched_word[3],
                           matched_word[4]) for matched_word in matched_words_column]

    pprint.pprint(crossword_string)
    # now search left diagonals

    n = len(crossword)
    left_diagonal_wordline = []

    for i in range(n):
        left_diagonal_wordline.append([crossword[i + j][j] for j in range(n - i)])

    for i in range(1, n):
        left_diagonal_wordline.append([crossword[j][i + j] for j in range(n - i)])

    #pprint.pprint(left_diagonal_wordline)
    #pprint.pprint([list_of_char_to_string(i) for i in left_diagonal_wordline])
    #pprint.pprint(matched_words)
   
    right_diagonal_wordline = []

    for i in range(n):
        right_diagonal_wordline.append([crossword[i + j][(n - 1) - j] for j in range(n - i)])

    for i in range(1, n):
        right_diagonal_wordline.append([crossword[j][(n - 1 - i) - j] for j in range(n - i)])

    #pprint.pprint(right_diagonal_wordline)
    pprint.pprint([list_of_char_to_string(i) for i in right_diagonal_wordline])

if __name__ == "__main__":
    main()

