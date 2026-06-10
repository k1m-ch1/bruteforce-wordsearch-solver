import argparse
from functools import reduce
import pprint
import numpy as np
import copy


parser = argparse.ArgumentParser(description="A brute force wordsearch solver")

parser.add_argument("wordsearch", type=str, help="The wordsearch as a text file")
parser.add_argument("-w", "--wordlist", type=str, help="The worldlist")
parser.add_argument("-m", "--min", type=int, default=1, help="The minimum acceptable word length")

def match_words_in_wordline(wordline, wordset):
    # we'll define a wordline to be a line that may contain words in the wordlist in it
    # returns the matched word, the start index (inclusive), the end index (exclusive), non_reverse_match, reverse match
    matched_words = []
    for i in range(len(wordline)):
        for j in range(i, len(wordline)):
            word_to_check = wordline[i:j+1]
            non_reversed_matched = list_of_char_to_string(word_to_check) in wordset
            reversed_matched = list_of_char_to_string(list(reversed(word_to_check))) in wordset
            if non_reversed_matched or reversed_matched:
                matched_words.append((word_to_check, i, j, non_reversed_matched, reversed_matched))

    return matched_words

def is_square(array_of_array):
    return all([len(array_of_array) == len(row) for row in array_of_array])

def is_rect(array_of_array):
    # check whether an array of array is rectangular
    if len(array_of_array) <= 1:
        return True
    else:
        first_element_length = len(array_of_array[0])
        return all([len(row) == first_element_length for row in array_of_array])

def transpose(array_of_array):
    # assume that it's a square array
    if not is_rect(array_of_array):
        raise ValueError("Please enter a rectangular array of array")

    n = len(array_of_array)
    m = len(array_of_array[0])
    array_transposed = [[None]*n for _ in range(m)]
    for i in range(n):
        for j in range(m):
            array_transposed[j][i] = array_of_array[i][j]
    return array_transposed

def list_of_char_to_string(list_of_char):
    if len(list_of_char) == 0:
        return ""
    elif len(list_of_char) == 1:
        return list_of_char[0]
    return reduce(lambda a, b: a + b, list_of_char)

def apply_highlight_mask(wordsearch, highlight_mask, modify_character):
    # modify_character is a function that takes in a character and spits out what we want to replace it with

    if not is_rect(wordsearch):
        raise ValueError("The wordsearch isn't rectuangular")

    n = len(wordsearch)
    m = len(wordsearch[0])
    highlighted_wordsearch = copy.deepcopy(wordsearch)
    for i in range(n):
        for j in range(m):
            if highlight_mask[i][j]:
                highlighted_wordsearch[i][j] = modify_character(wordsearch[i][j])

    return highlighted_wordsearch

def wordsearch_to_string(wordsearch):
    result = ""
    for row in wordsearch:
        for c in row:
            result += c
        result += "\n"
    result.strip('\n')
    return result


def main():
    args = parser.parse_args()
    with open(args.wordsearch, 'r') as file:
        wordsearch_string = file.read()
        wordsearch = [list(wordline) for wordline in wordsearch_string.strip().split('\n')]

    with open(args.wordlist, 'r') as file:
        file_as_string = file.read()
        wordset = set([word.strip().lower() for word in file_as_string.split('\n')])
        wordset = set([word for word in wordset if len(word) >= args.min])


    if not is_rect(wordsearch):
        raise ValueError("The wordsearch isn't rectuangular")

    n = len(wordsearch)
    m = len(wordsearch[0])

    highlight_mask = [[False]*m for _ in range(n)]
    # first, search through the rows
    rows_of_wordline = wordsearch
    matched_words = []
    for i, row in enumerate(rows_of_wordline):
        matched_words_row = match_words_in_wordline(row, wordset)
        for matched_word in matched_words_row:
            matched_words.append(
                (matched_word[0],
                 (i, matched_word[1]),
                 (i, matched_word[2]),
                 matched_word[3],
                 matched_word[4])
            )
            for j in range(matched_word[1], matched_word[2] + 1):
                highlight_mask[i][j] = True

    wordsearch_transposed = transpose(wordsearch)
    wordsearch_string = [list_of_char_to_string(r) for r in wordsearch]
    #crossword_transposed_string = [list_of_char_to_string(c) for c in crossword_transposed]
    columns_of_wordline = wordsearch_transposed
    for i, column in enumerate(columns_of_wordline):
        matched_words_column = match_words_in_wordline(column, wordset)
        for matched_word in matched_words_column:
            matched_words.append(
                (matched_word[0],
                 (matched_word[1], i),
                 (matched_word[2], i),
                 matched_word[3],
                 matched_word[4])
            )
            for j in range(matched_word[1], matched_word[2] + 1):
                highlight_mask[j][i] = True

    # now search left diagonals

    for i in range(n):
        matched_words_left_diagonal = match_words_in_wordline([wordsearch[i + j][j] for j in range(min(n,m) - i)], wordset)
        for matched_word in matched_words_left_diagonal:
            matched_words.append(
                (matched_word[0],
                 (i + matched_word[1], matched_word[1]),
                 (i + matched_word[2], matched_word[2]),
                 matched_word[3],
                 matched_word[4])
            )
            for j in range(matched_word[1], matched_word[2] + 1):
                highlight_mask[i + j][j] = True

    for i in range(1, m):
        #[crossword[j][i + j] for j in range(n - i)]
        matched_words_left_diagonal = match_words_in_wordline([wordsearch[j][i + j] for j in range(min(n,m) - i)], wordset)
        for matched_word in matched_words_left_diagonal:
            matched_words.append(
                (matched_word[0],
                 (matched_word[1], i + matched_word[1]),
                 (matched_word[2], i + matched_word[2]),
                 matched_word[3],
                 matched_word[4])
            )
            for j in range(matched_word[1], matched_word[2] + 1):
                highlight_mask[j][i + j] = True


    for i in range(n):
        #[crossword[i + j][(n - 1) - j] for j in range(n - i)]
        matched_words_right_diagonal = match_words_in_wordline([wordsearch[i + j][(min(m,n) - 1) - j] for j in range(min(m,n) - i)], wordset)
        for matched_word in matched_words_right_diagonal:
            matched_words.append(
                (matched_word[0],
                 (i + matched_word[1], (min(m, n) - 1) - matched_word[1]),
                 (i + matched_word[2], (min(m, n) - 1) - matched_word[2]),
                 matched_word[3],
                 matched_word[4])
            )

            for j in range(matched_word[1], matched_word[2] + 1):
                highlight_mask[i + j][(min(m, n) - 1) - j] = True

    for i in range(1, m):
        #[crossword[j][(n - 1 - i) - j] for j in range(n - i)]
        matched_words_right_diagonal = match_words_in_wordline([wordsearch[j][(min(m,n) - 1 - i) - j] for j in range(min(m,n) - i)], wordset)
        for matched_word in matched_words_right_diagonal:
            matched_words.append(
                    (matched_word[0],
                    (matched_word[1], (min(m, n) - 1 - i) - matched_word[1]),
                    (matched_word[2], (min(m, n) - 1 - i) - matched_word[2]),
                    matched_word[3],
                    matched_word[4])
            )
            for j in range(matched_word[1], matched_word[2] + 1):
                highlight_mask[j][(min(m, n) - 1 - i) - j] = True

    start_mask = [[False]*m for _ in range(n)]
    end_mask = [[False]*m for _ in range(n)]
    for matched_word in matched_words:
        start_coord = matched_word[1]
        end_coord = matched_word[2]
        start_mask[start_coord[0]][start_coord[1]] = True
        end_mask[end_coord[0]][end_coord[1]] = True

    pprint.pprint(matched_words)
    print(np.array(highlight_mask))
    highlighted_wordsearch = apply_highlight_mask(wordsearch, highlight_mask, lambda c: "\033[1;33m" + c + "\033[0m")
    highlighted_wordsearch = apply_highlight_mask(highlighted_wordsearch, start_mask, lambda c: "\033[44m" + c)
    highlighted_wordsearch = apply_highlight_mask(highlighted_wordsearch, end_mask, lambda c: "\033[45m" + c)
    print(wordsearch_to_string(highlighted_wordsearch))

if __name__ == "__main__":
  main()

