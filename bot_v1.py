import numpy as np
import pandas as pd
from os import path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Eliminates all words that have a certain character at a specified location
# @param pos - the position that the function should search for the character
# @param let - the character that should be eliminated
# @param dct - the DataFrame that will be searched
# @return dct - returns the modified DataFrame
def indexElimination(pos, let, dct):
    reg = "." * pos + "[^" + let + "]" + "." * (4-pos)
    dct = dct[ dct['word'].str.match( reg) ]
    return dct

# Eliminates all words that do not have a specified number of appearances of a certain letter.
# @param list1 - list of letters that will be compared to the DataFrame. The amount of appearances of the certain
# letter is found by the number of appearances in list1 and list2
# @param list2 - list of letters that will be compared to the DataFrame. Same purpose as list1
# @param let - the letter that should be removed from the words
# @param dct the DataFrame that will be analyzed
# @return - the modified DataFrame
def breadthElimination(list1, list2, let, dct):
    num = list1.count(let) + list2.count(let)
    reg = "\D*"
    for i in range(num):
        reg += let + "\D*"
    return dct[dct['word'].str.match(reg)]

# Displays the message after each guess that shows the remaining possible words and the amount of words left
# @param df - the DataFrame whose details will be printed
def message(df, guesses, results):
    print("--------------------------------------")
    print(df)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("There are %d possible words" % len(df))
    print(f"Suggested word(s): {weights(df, guesses, results)}")

def weights(df, guesses, results):
    words_left = df['word'].to_numpy()
    np_guesses = np.array(list(np.array(guesses).flatten()[0]))
    np_results = np.array(list(np.array(results).flatten()[0]))


    letters = {
        'q' : 0,
        'w' : 0,
        'e' : 0,
        'r' : 0,
        't' : 0,
        'y' : 0,
        'u' : 0,
        'i' : 0,
        'o' : 0,
        'p' : 0,
        'a' : 0,
        's' : 0,
        'd' : 0,
        'f' : 0,
        'g' : 0,
        'h' : 0,
        'j' : 0,
        'k' : 0,
        'l' : 0,
        'z' : 0,
        'x' : 0,
        'c' : 0,
        'v' : 0,
        'b' : 0,
        'n' : 0,
        'm' : 0
    }

    filter_arr = []
    for letter in np_results:
        filter_arr.append(letter == 'y' or letter == 'g')

    for word in words_left:
        used = []
        for letter in word:
            if letter not in np_guesses[filter_arr] and letter not in used:
                letters[letter] = letters[letter] + 1
                used.append(letter)
    

    weights = np.array([])
    word_list = pd.read_csv('valid_solutions.csv')['word'].to_numpy()

    for word in word_list:
        weight = 0
        used = []
        for letter in word:
            if letter not in used:
                weight += letters[letter]
                used.append(letter)
        weights = np.append(weights, weight)

    return word_list[np.where(weights == max(weights))]

    


# Filters out the DataFrame
# @param guess - the word that was guessed
# @param result - the sequence of letters that represent the colors that resulted from the guess
# @param words - the DataFrame that will be filtered
# @return - the modified DataFrame
def filter(guess, result, words):
    g_letters = []
    y_letters = []

    for j in range(len(result)):
            if result[j] == 'g':
                g_letters.append(guess[j])
                reg_exp = "." * j + guess[j] + "." * (4 - j)
                words = words[ words['word'].str.match( reg_exp ) ]
        
    for j in range(len(result)):
        if result[j] == 'y':
            y_letters.append(guess[j])
            words = words[ words.word.str.contains( guess[j] ) ]
            words = indexElimination(j, guess[j], words)
            
    for j in range(len(result)):
        if result[j] == 'r' or result[j] == 'b':
            if guess[j] not in g_letters and guess[j] not in y_letters:
                reg = ("[^" + guess[j] + "]") * 5
                words = words[words['word'].str.match(reg)]
            else:
                words = breadthElimination(g_letters, y_letters, guess[j], words)
    
    return words


# Runs the game
def guess():
    words = pd.read_csv('valid_solutions.csv')
    i = 1
    guesses = []
    results = []
    end_game = False
    while i < 9 and not end_game:
        guess = ""
        result = ""
        continue_this_guess = True
        while continue_this_guess:
            continue_this_guess = False
            guess = input("Enter guess %d (or \'stop\' to end the program): " % (i))
            if guess.upper() == 'STOP':
                end_game = True
                continue_this_guess = False
            
            elif len(guess) != 5:
                print("\"%s\" is invalid, try again." % guess)
                end_game = False
                continue_this_guess = True

            else:
                result = input("Enter result for \'%s\': " % (guess))
                if result.upper() == 'STOP':
                    end_game = True
                    continue_this_guess = False
                elif len(result) != 5:
                    print("\"%s\" is invalid, try again." % result)
                    continue_this_guess = True
                elif result == 'ggggg':
                    end_game = True
                    continue_this_guess = False
                    print("Congratulations!")

        guesses.append(guess)
        results.append(result)
        words = filter(guess, result, words)

        message(words, guesses, results)

        if len(words) < 2:
            return i

        i+=1

# guess()

# words = pd.read_csv('valid_solutions.csv')
# s=Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=s)
driver = webdriver.Chrome('/Users/kashishpatel/Downloads/chromedriver')
driver.maximize_window()
driver.get("https://www.nytimes.com/games/wordle/index.html")

time.sleep(1)

word = "alert"
page = driver.find_element(By.TAG_NAME, 'body')

guesses = []
results = []
board =  driver.find_elements(By.CLASS_NAME, 'Row-module_row__dEHfN')

for guess in range(6):
    # type in the guess to the site
    page.send_keys(word)
    page.send_keys(Keys.ENTER)
    time.sleep(3)

    # get the current row from the site
    row = board[guess].find_elements(By.CLASS_NAME, 'Tile-module_tile__3ayIZ')
    # row = driver.execute_script('''return document.querySelector("game-app").shadowRoot.querySelectorAll("game-row")[%d].shadowRoot.querySelectorAll("game-tile")''' % guess)
    cur_result = ""

    # create the result string based off of the website's html
    for letter in row:
        evaluation = letter.get_attribute("data-state")
        if evaluation == "present":
            cur_result += "y"
        elif evaluation == "correct":
            cur_result += "g"
        else:
            cur_result += "b"

    guesses.append(word)
    results.append(cur_result)

    words = filter(list(word), list(cur_result), words)
    if len(words) == 1:
        page.send_keys(words['word'].tolist()[0])
        page.send_keys(Keys.ENTER)
        break
    word = weights(words, guesses, results)[0]
