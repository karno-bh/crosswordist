
def naive_lookup(words, mapping: dict):
    result_words = []
    for word in words:
        suitable = True
        for letter_index, letter in mapping.items():
            if word[letter_index] != letter:
                suitable = False
                break
        if suitable:
            result_words.append(word)

    return result_words