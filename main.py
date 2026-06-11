import argparse
from functools import reduce
import copy

ANSI_BLACK = "\033[0;30m"
ANSI_RED = "\033[0;31m"
ANSI_GREEN = "\033[0;32m"
ANSI_BROWN = "\033[0;33m"
ANSI_BLUE = "\033[0;34m"
ANSI_PURPLE = "\033[0;35m"
ANSI_CYAN = "\033[0;36m"
ANSI_LIGHT_GRAY = "\033[0;37m"
ANSI_DARK_GRAY = "\033[1;30m"
ANSI_LIGHT_RED = "\033[1;31m"
ANSI_LIGHT_GREEN = "\033[1;32m"
ANSI_YELLOW = "\033[1;33m"
ANSI_LIGHT_BLUE = "\033[1;34m"
ANSI_LIGHT_PURPLE = "\033[1;35m"
ANSI_LIGHT_CYAN = "\033[1;36m"
ANSI_LIGHT_WHITE = "\033[1;37m"
ANSI_BOLD = "\033[1m"
ANSI_FAINT = "\033[2m"
ANSI_ITALIC = "\033[3m"
ANSI_UNDERLINE = "\033[4m"
ANSI_BLINK = "\033[5m"
ANSI_NEGATIVE = "\033[7m"
ANSI_CROSSED = "\033[9m"
ANSI_END = "\033[0m"

SELECTED_COLORS = [
    ANSI_RED,
    ANSI_GREEN,
    ANSI_BROWN,
    ANSI_BLUE,
    ANSI_PURPLE,
    ANSI_CYAN,
    ANSI_YELLOW
]

APPLY_SELECTED_COlORS = [lambda c: SELECTED_COLORS[i] + c + ANSI_END for i in range(len(SELECTED_COLORS))]

DEFAULT_COLOR = ANSI_END

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
    # the index of the color
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
        print(wordset)

    if not is_rect(wordsearch):
        raise ValueError("The wordsearch isn't rectuangular")

    n = len(wordsearch)
    m = len(wordsearch[0])

    highlight_masks = [[[False]*m for _ in range(n)] for _ in range(len(SELECTED_COLORS))]
    highlight_mask = [[DEFAULT_COLOR]*n for _ in range(n)]
    selected_color = 0
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
                highlight_masks[selected_color][i][j] = True
                highlight_mask[i][j] = SELECTED_COLORS[selected_color]
            selected_color += 1
            selected_color = selected_color % len(SELECTED_COLORS)

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
                highlight_masks[selected_color][j][i] = True
                highlight_mask[j][i] = SELECTED_COLORS[selected_color]
            selected_color += 1
            selected_color = selected_color % len(SELECTED_COLORS)


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
                highlight_masks[selected_color][i + j][j] = True
                highlight_mask[i + j][j] = SELECTED_COLORS[selected_color]

            selected_color += 1
            selected_color = selected_color % len(SELECTED_COLORS)



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
                highlight_masks[selected_color][j][i + j] = True
                highlight_mask[j][i + j] = SELECTED_COLORS[selected_color]

            selected_color += 1
            selected_color = selected_color % len(SELECTED_COLORS)

    # and search right diagonal
    for i in range(n):
        #[crossword[i + j][(n - 1) - j] for j in range(n - i)]
        wordline = [wordsearch[i + j][(min(m,n) - 1) - j] for j in range(min(m,n) - i)]
        print(wordline)
        matched_words_right_diagonal = match_words_in_wordline(wordline, wordset)
        for matched_word in matched_words_right_diagonal:
            matched_words.append(
                (matched_word[0],
                 (i + matched_word[1], (min(m, n) - 1) - matched_word[1]),
                 (i + matched_word[2], (min(m, n) - 1) - matched_word[2]),
                 matched_word[3],
                 matched_word[4])
            )

            for j in range(matched_word[1], matched_word[2] + 1):
                highlight_masks[selected_color][i + j][(min(m, n) - 1) - j] = True
                highlight_mask[i + j][(min(m, n) - 1) -  j] = SELECTED_COLORS[selected_color]

            selected_color += 1
            selected_color = selected_color % len(SELECTED_COLORS)


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
                highlight_masks[selected_color][j][(min(m, n) - 1 - i) - j] = True
                highlight_mask[j][(min(m, n) - 1 - i) -  j] = SELECTED_COLORS[selected_color]

            selected_color += 1
            selected_color = selected_color % len(SELECTED_COLORS)

    highlighted_wordsearch = copy.deepcopy(wordsearch)
    better_highlighted_wordsearch = copy.deepcopy(wordsearch)
    for i in range(len(highlight_masks)):
        highlighted_wordsearch = apply_highlight_mask(highlighted_wordsearch, highlight_masks[i], APPLY_SELECTED_COlORS[i])

    for i in range(n):
        for j in range(m):
            better_highlighted_wordsearch[i][j] = highlight_mask[i][j] + better_highlighted_wordsearch[i][j]

    #print(wordsearch_to_string(highlighted_wordsearch))
    print(wordsearch_to_string(better_highlighted_wordsearch))

if __name__ == "__main__":
  main()

