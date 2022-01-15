#!/usr/bin/env python
import codecs
import itertools
import os
import time
from difflib import SequenceMatcher

import bs4

start = time.time()
print("loading...")


def main():
    languages = ['en', 'ru']
    cats = ['society', 'economy', 'technology', 'sports', 'entertainment', 'science']
    dictionary = {}
    alphabet = {}
    articles = {}
    category = {}
    entities = {}
    entities['ru'] = setup_dictionary('ru', 'entities')
    path_to_files = "./data/20191102/00/"
    files = os.listdir(path_to_files)
    for lang in languages:
        category[lang] = {}
        articles[lang] = {}
        dictionary[lang] = setup_dictionary(lang)
        alphabet[lang] = setup_alphabet(lang)
        for cat in cats:
            if lang == 'ru' and cat == 'society':
                category[lang][cat] = setup_dictionary(lang, cat)
    i = 0
    en_articles = 0
    ru_articles = 0
    other_articles = 0
    ru_society = 0
    ru_society_articles = {}

    for file in files:
        article = get_txts_from_file(file, path_to_files)
        en = is_required_language('en', article['txt'], alphabet['en'], dictionary['en'])
        ru = is_required_language('ru', article['txt'], alphabet['ru'], dictionary['ru'])
        i += 1
        if ru:
            ru_society_articles[file] = {}
            ru_society_articles[file]['w'] = {}
            is_society = category_check(alphabet['ru'], article['txt'], category['ru']['society'])

            if is_society:
                ru_society_articles[file]['title'] = article['title']
                ru_society_articles[file]['txt'] = article['txt']
                ru_society_articles[file]['w'] = break_article_into_words(article['txt'], alphabet['ru'])
                ru_society += 1
            ru_articles += 1
        elif en:
            en_articles += 1

    for ArticleA in ru_society_articles:
        for ArticleB in ru_society_articles:
            if isset(ArticleA['txt']) and isset(ArticleB['txt']):
                sim = similar(ArticleA['txt'], ArticleB['txt'])
                if sim > 0:
                    print("Similarity: {}:".format(sim))
                    print(ArticleA['title'])
                    print(ArticleB['title'])
                    print('--------------------')

    other_articles = i - en_articles - ru_articles
    print('processed {} articles'.format(i))
    print('Russian articles: {}'.format(ru_articles))
    print(' --- Общество: {}'.format(ru_society))
    print('English articles: {}'.format(en_articles))
    print('Other articles (neither English nor Russian): {}'.format(other_articles))
    end = time.time()
    print('Processing time in seconds:')
    print(end - start)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_txts_from_file(filename, path_to_files):
    article = {}
    url = path_to_files + filename
    url = get_full_pathname(url)
    f = codecs.open(url, 'r', 'utf-8')
    # print(document)
    soup = bs4.BeautifulSoup(f, 'html.parser')
    article['txt'] = soup.find('article').get_text()
    article['title'] = soup.find('h1').get_text()

    return article


def isset(variable):
    return variable in locals() or variable in globals()


def is_required_language(lang, txt, alphabet, dictionary):
    preliminary_test_passed = preliminary_check(lang, txt)
    if preliminary_test_passed:
        full_test_passed = full_check(alphabet, dictionary, txt)
        if full_test_passed:
            return True
        else:
            return False
    else:
        return False


def get_full_pathname(name):
    full_path = os.path.abspath(os.path.join(name))
    return full_path


def preliminary_check(lang, txt):
    if lang == 'en':
        if "the " in txt and ("be " in txt or 'is ' in txt or 'been ' or 'was '):
            return True
        else:
            return False

    if lang == 'ru':
        if 'с ' in txt or 'из ' in txt or 'в ' in txt or 'а ' in txt or 'и ' in txt:
            return True
        else:
            return False


def setup_alphabet(lang):
    if lang == 'en':
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        # print('alphabet EN defined')
    elif lang == 'ru':
        alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        # print('alphabet RU defined')
    else:
        alphabet = None

    letters_and_space = alphabet + alphabet.lower() + ' \t\n'
    # print('letters_and_space defined')
    return letters_and_space


def setup_dictionary(lang, category='dictionary'):
    dictionary_file = open("./src/{0}_{1}.txt".format(category, lang))
    words = {}

    for word in dictionary_file.read().split("\n"):
        word = word.upper()
        words[word] = None

    dictionary_file.close()
    words = set(words)
    return words


def full_check(letters_and_space, words, txt, word_percentage=20, letter_percentage=85):
    words_match = get_words_count(txt, words, letters_and_space) * 100 >= word_percentage
    num_letters = len(remove_non_letters(txt, letters_and_space))
    message_letters_percentage = float(num_letters) / len(txt) * 100
    letters_match = message_letters_percentage >= letter_percentage
    return words_match and letters_match


def category_check(letters_and_space, txt, context_words):
    context_words_match = get_words_count(txt, context_words, letters_and_space) * 100  # >= context_words_percentage
    if context_words_match > 0.5:
        return context_words_match
    else:
        return False


def get_matched_words(message, words, letters_and_space, length=0):
    message = message.upper()
    message = remove_non_letters(message, letters_and_space)
    possible_words = message.split()

    if not possible_words:
        return 0.0  # no words at all, so return 0.0

    matches = 0
    matched_words = {}
    for word in possible_words:
        if word in words:
            if len(word) >= length:
                matches += 1
                matched_words[word] = None
    return matched_words, matches, possible_words


def break_article_into_words(message, letters_and_space, length=0):
    message = message.upper()
    message = remove_non_letters(message, letters_and_space)
    possible_words = message.split()
    matched_words = {}
    for word in possible_words:
        if len(word) >= length:
            matched_words[word] = None
    return matched_words


def get_words_count(message, words, letters_and_space):
    array = get_matched_words(message, words, letters_and_space)
    matched_words = array[0]
    matches = array[1]
    possible_words = array[2]
    return float(matches) / len(possible_words)


def remove_non_letters(message, letters_and_space):
    letters_only = []

    for symbol in message:
        if symbol in letters_and_space:
            letters_only.append(symbol)

    return ''.join(letters_only)


main()
