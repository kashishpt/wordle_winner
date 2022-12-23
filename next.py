import pandas as pd
def get_next(words, gen_weights=False):
    freqs = {
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

    # gather the frequencies of each letter throughout our entire
    # word list
    for word in words:
        for char in word:
            freqs[char] += 1

    if not gen_weights:
        # start the process of finding the optimal word
        # loop through each of the words, and choose the word that 
        # has letters that appear in other words the most
        best_word = None
        max_weight = 0
        for word in words:
            total = 0
            seen = set()
            for letter in word:
                total += freqs[letter] if letter not in seen else 0
                seen.add(letter)

            if total > max_weight:
                max_weight = total
                best_word = word


        words.pop(words.index(best_word))
        return best_word, words

    else:
        weights = {'word':[], 'weight':[]}
        for word in words:
            total = 0
            seen = set()
            for letter in word:
                total += freqs[letter] if letter not in seen else 0
                seen.add(letter)
            weights['word'].append(word)
            weights['weight'].append(total)

        df = pd.DataFrame(weights).sort_values('weight', ascending=False).set_index('word')

        df.to_csv('./weights.csv')


words = []
with open('./words.txt', 'r') as file:
    line = file.readline()

    # all the words are stored in one line, without any explicit delimiters
    # to save space, since we know each word is 5 characters long
    words = [line[i:i+5] for i in range(0, len(line), 5)]

get_next(words, gen_weights=True)
