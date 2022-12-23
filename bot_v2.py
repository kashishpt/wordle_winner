import numpy as np
import pandas as pd
# from os import path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from enum import Enum
import re
from next import get_next

# set up an enum to symbolize which characters are present.
# this will help with readability
class Presence(Enum):
    ABSENT = 1
    PRESENT = 2
    CORRECT = 3


def guess():
    # keep a running set of which letters are in the word
    correct_letters = set()

    # read in all the possible words
    # these were found straight from https://www.nytimes.com/games/wordle/index.html,
    # in the Sources /top/www.nytime.com/games-assets/v2/wordle.31c3cb8f197aa9ad1b27e65327e43a0e621f3eb0.js
    words = []
    with open('./words.txt', 'r') as file:
        line = file.readline()

        # all the words are stored in one line, without any explicit delimiters
        # to save space, since we know each word is 5 characters long
        words = [line[i:i+5] for i in range(0, len(line), 5)]




    # load the page
    s=Service(ChromeDriverManager().install())
    driver = driver = webdriver.Chrome(service=s)
    driver.get("https://www.nytimes.com/games/wordle/index.html")
    time.sleep(1)

    # close the tutorial window
    x_button = driver.find_element(By.CLASS_NAME, 'Modal-module_closeIcon__b4z74')
    x_button.click()
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 1080)") 

    # get the board rows
    page = driver.find_element(By.TAG_NAME, 'body')
    rows = driver.find_elements(By.CLASS_NAME, 'Row-module_row__dEHfN')

    current_guess, words = get_next(words)


    for row in rows:
        # guess the current word
        page.send_keys(current_guess)
        page.send_keys(Keys.ENTER)
        time.sleep(2.5)

        # collect the results
        cur_result = []
        # get each of the letters in one list
        letters = row.find_elements(By.CLASS_NAME, 'Tile-module_tile__3ayIZ')
        # loop throught the letters, determining if that letter is absent, present, or correct
        for feedback in letters:
            result = feedback.get_attribute('data-state')
            if result == 'absent':
                cur_result.append(Presence.ABSENT)
            elif result == 'present':
                cur_result.append(Presence.PRESENT)
            elif result == 'correct':
                cur_result.append(Presence.CORRECT)

        if len(list(filter(lambda x: x == Presence.CORRECT, cur_result))) == 5:
            time.sleep(4)
            print(f'The word was {current_guess.upper()}!')
            return

        for letter, presence, index in zip(current_guess, cur_result, range(5)):

            # if the letter is correct, only keep the words that have that letter
            # in the same spot
            if presence == Presence.CORRECT:
                regex = ("."*index) + letter + ("." * (5 - index - 1))
                dfa = re.compile(regex)
                words = list(filter(lambda word: bool(dfa.match(word)), words))
                correct_letters.add(letter)

            # if the letter is present, only keep the words that have that letter
            # in a different spot
            elif presence == Presence.PRESENT:
                regex = ("."*index) + ('[^' + letter + ']') + ("." * (5 - index - 1))
                dfa = re.compile(regex)
                words = list(filter(lambda word: bool(dfa.match(word) and letter in word), words))
                correct_letters.add(letter)

        for letter, presence, index in zip(current_guess, cur_result, range(5)):
            # if the letter is absent AND it has not been a correct letter in the past,
            # remove all words that have that letter in them
            if presence == Presence.ABSENT and letter not in correct_letters:
                regex = ('[^' + letter + ']')*5
                dfa = re.compile(regex)
                words = list(filter(lambda word: bool(dfa.match(word)), words))

        current_guess, words = get_next(words)

guess()
