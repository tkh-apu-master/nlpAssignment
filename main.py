from tkinter import *
from tkinter.scrolledtext import ScrolledText
import re
import pkg_resources
from tkmacosx import Button
from urllib.request import urlopen

from spellchecker import SpellChecker
from symspellpy import SymSpell
from textblob import TextBlob, Word
from textblob.en import Spelling
from nltk.corpus import wordnet

# Strategy: Use Norvig with SymSpell approach, which improves speed, memory consumption and accuracy
# Reference: https://towardsdatascience.com/spelling-correction-how-to-make-an-accurate-and-fast-corrector-dc6d0bcbba5f

# TODO: Corpora of misspellings for download
# https://www.dcs.bbk.ac.uk/~ROGER/corpora.html

# TODO: Efficient Text Data Cleaning
# https://www.geeksforgeeks.org/python-efficient-text-data-cleaning/

# TODO: TextBlob with custom training
# https://stackabuse.com/spelling-correction-in-python-with-textblob/

# TODO: Grammar Checker
# https://www.geeksforgeeks.org/grammar-checker-in-python-using-language-check/

spell = SpellChecker()

sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

dictionary_path = pkg_resources.resource_filename('symspellpy', 'frequency_dictionary_en_82_765.txt')
bigram_path = pkg_resources.resource_filename('symspellpy', 'frequency_bigramdictionary_en_243_342.txt')

sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)

# current_sentence = ''

# Sample wrong sentences
# current_sentence = 'let us wlak on the groun. it\'s weird that...'
current_sentence = 'It is a truth unіversally acknowledged, that a single man in possesssion of a good fortune must be' \
                   ' in want of a wife. However little known the feelings or views of such a man may be on his first' \
                   ' entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families,' \
                   ' that he is considered as the rightful property of some one or other of their daugters.'
# current_sentence = 'I enjoyd the event which took place yesteday &amp; I luvd it ! The link to the show is '
# current_sentence = 'I took a message yesterday' # Testing sample real word misspellings
# current_sentence = 'thequickbrownfoxjumpsoverthelazydog'
# current_sentence = 'http://t.co/4ftYom0i It\'s awesome you\'ll luv it #HadFun #Enjoyed BFN GN'
current_wrong_word = ''
recommended_sentence_fixes = []
recommended_fixes = []
recommended_fixes_search_result = []

root = Tk()
root.title('NLP Demonstration: Spelling Correction')
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)


def submit():
    global current_sentence
    current_sentence = user_input_textbox.get('1.0', END)
    clear_recommended_fixes()

    require_check = check_sentence()

    if require_check:
        # Suggest correct sentence spacing
        print('Suggest correct sentence spacing')

    analyze_text()

    user_input_textbox.focus_set()


# Analyze the sentence and suggest correct word segmentation & grammar
def check_sentence():
    print('check_sentence()')
    global current_sentence
    global recommended_sentence_fixes
    print('current_sentence: ', current_sentence)

    # Check word segmentation with symspell
    sentence_suggestions = sym_spell.word_segmentation(current_sentence)
    for sentence_suggestion in sentence_suggestions:
        print('sentence_suggestion type: ', type(sentence_suggestion))
        print('sentence_suggestion: ', sentence_suggestion)
        if type(sentence_suggestion) == str and \
                sentence_suggestion != current_sentence and \
                sentence_suggestion not in recommended_sentence_fixes:
            recommended_sentence_fixes.append(sentence_suggestion)

    # Check if the sentence is correct with TextBlob
    textblob_sentence = TextBlob(current_sentence)

    if textblob_sentence != current_sentence and \
            textblob_sentence not in recommended_sentence_fixes:
        recommended_sentence_fixes.append(textblob_sentence)

    if len(recommended_sentence_fixes) > 0:
        show_recommended_sentence()
        return True
    else:
        return False


def analyze_text():
    global current_sentence
    global current_wrong_word
    global recommended_fixes
    # Split sentence into words precisely using regex: https://stackoverflow.com/a/26209841
    split_text = re.findall(r"(?<![@#])\b\w+(?:'\w+)?", current_sentence)
    misspelled = spell.unknown(split_text)

    if len(misspelled) > 0:
        current_wrong_word = list(misspelled)[0]
        recommended_fixes = show_recommended_fixes(current_wrong_word)
        display_recommended_fixes()


def show_recommended_sentence():
    mistake_sentence_label.config(text='Possible sentence mistake. Please click one of the following suggestions:')
    display_recommended_sentence_fixes()


def clear_input():
    user_input_textbox.delete(1.0, 'end')
    user_input_textbox.focus_set()


def on_sentence_select(event):
    selected_item = listbox.get(ANCHOR)
    correct_misspelled_sentence(selected_item)
    submit()  # Analyze again


def on_correct_word_select(event):
    selected_item = listbox2.get(ANCHOR)
    correct_misspelled_word(selected_item)
    submit()  # Analyze again


def clear():
    clear_input()
    clear_recommended_fixes()


def clear_recommended_fixes():
    global recommended_fixes_search_result
    global recommended_sentence_fixes
    recommended_fixes_search_result.clear()
    recommended_sentence_fixes.clear()
    misspelled_word_label.config(text='Misspelled sentence: None')
    misspelled_word_label.config(text='Misspelled word: None')
    listbox.delete(0, END)
    listbox.unbind('<Double-1>')
    listbox2.delete(0, END)
    listbox2.unbind('<Double-1>')


def show_recommended_fixes(wrong_word):
    misspelled_word_label.config(text='Misspelled word: ' + wrong_word)

    # Get suggestions from SymSpell
    recommended_fixes2 = list(spell.candidates(wrong_word))

    # Additionally, use SymSpell to find similar words
    suggestions = sym_spell.lookup_compound(wrong_word, max_edit_distance=2)
    for suggestion in suggestions:
        if suggestion.term not in recommended_fixes2:
            recommended_fixes2.append(suggestion.term)

    # Use TextBlob to find similar words
    w = Word(wrong_word)
    suggestions2 = w.spellcheck()
    for similar_word in suggestions2:
        if similar_word not in recommended_fixes2:
            recommended_fixes2.append(similar_word[0])

    return recommended_fixes2


def display_recommended_sentence_fixes():
    global recommended_sentence_fixes
    for sentence in recommended_sentence_fixes:
        listbox.insert(END, sentence)
    listbox.bind('<Double-1>', on_sentence_select)


def display_recommended_fixes():
    global recommended_fixes
    for word in recommended_fixes:
        listbox2.insert(END, word)
    listbox2.bind('<Double-1>', on_correct_word_select)


def correct_misspelled_word(corrected_word):
    global current_sentence
    global current_wrong_word
    user_input_textbox.delete(1.0, 'end')

    current_sentence = current_sentence.replace(current_wrong_word, corrected_word)
    user_input_textbox.insert(END, current_sentence)


def correct_misspelled_sentence(corrected_sentence):
    global current_sentence
    user_input_textbox.delete(1.0, 'end')

    current_sentence = corrected_sentence
    user_input_textbox.insert(END, current_sentence)


def search_word(event):
    global recommended_fixes_search_result
    listbox2.delete(0, END)
    listbox2.unbind('<Double-1>')
    recommended_fixes_search_result.clear()
    search_keyword = search_input.get(1.0, 'end')

    for i in range(len(recommended_fixes)):
        if search_keyword in recommended_fixes[i]:
            recommended_fixes_search_result.append(recommended_fixes[i])

    # If search_keyword is empty, show all recommended words as default
    if len(search_keyword) == 1:
        recommended_fixes_search_result.extend(recommended_fixes)

    for word in recommended_fixes_search_result:
        listbox2.insert(END, word)
    listbox2.bind('<Double-1>', on_correct_word_select)


# A function that analyze the accuracy of the spell checker, with using misspelling corpora, and display the results.
def spelling_corrector_analysis():
    # Prepare dataset
    r = urlopen('https://www.dcs.bbk.ac.uk/~ROGER/missp.dat')
    correct_words = []
    wrong_words = []

    for line in r:
        string = str(line)
        string = string[2:]  # Remove b'
        string = string[:-3]  # Remove \n'
        if string.startswith(tuple(['$'])):
            correct_words.append(string)
        else:
            wrong_words.append(string)

    # Analyze accuracy
    print('correct_words: ', correct_words)
    print('wrong_words: ', wrong_words)
    print('len(correct_words): ', len(correct_words))
    print('len(wrong_words): ', len(wrong_words))
    test_data = wrong_words[:100]
    print('len(test_data): ', len(test_data))
    correct_count = 0
    wrong_count = 0
    for mispelled_word in test_data:
        print('mispelled_word: ', mispelled_word)
        suggestions = show_recommended_fixes(mispelled_word)
        if suggestions is not None:
            print('suggestions: ', len(suggestions))
        else:
            print('No suggestions for this word')

        # If there is no suggestion, then the word is not in the dictionary
        if suggestions is not None and len(suggestions) > 0:
            for suggestion in list(suggestions):
                # If the suggestion is in the correct_words, then it is correct
                if suggestion in correct_words:
                    correct_count += 1
        else:
            wrong_count += 1
    print('correct_count: ', correct_count)
    print('wrong_count: ', wrong_count)

    # Display results
    accuracy = correct_count / len(test_data)
    print('accuracy: ', accuracy, '%')


# Left panel
left_panel = Frame(root)
left_panel.rowconfigure(0, weight=1)
left_panel.columnconfigure(0, weight=1)
left_panel.grid(column=0, row=0, sticky='nsew')

# Action buttons
frm_buttons = Frame(left_panel, relief=RAISED)
frm_buttons.rowconfigure(0, weight=1)
frm_buttons.columnconfigure(0, weight=1)
frm_buttons.grid(column=0, row=1, sticky='nsew')

btn_spelling_corrector_analysis = Button(frm_buttons, text='Spelling Corrector Accuracy Analysis',
                                         command=spelling_corrector_analysis, background='grey')
btn_submit = Button(frm_buttons, text='Submit', command=submit, background='#00CA4E', foreground='black')
btn_clear = Button(frm_buttons, text='Clear', command=clear, background='#FFBD44', foreground='black')
btn_exit = Button(frm_buttons, text='Exit', command=root.destroy, background='#FF605C', foreground='black')
btn_spelling_corrector_analysis.grid(column=0, row=0, sticky='nsew')
btn_submit.grid(column=0, row=1, sticky='nsew')
btn_clear.grid(column=0, row=2, sticky='nsew')
btn_exit.grid(column=0, row=3, sticky='nsew')

# User input
user_input = Frame(left_panel, relief=RAISED)
user_input.rowconfigure(0, weight=1)
user_input.columnconfigure(0, weight=1)

user_input_label = Label(user_input, text='Input:')
user_input_label.grid(column=0, row=0, sticky='nw')
user_input_textbox = ScrolledText(user_input)
user_input_textbox.grid(column=0, row=1, sticky='s')
user_input_textbox.insert(END, current_sentence)
user_input_textbox.focus_set()

user_input.grid(column=0, row=0, padx=5, pady=5)

# Right panel
right_panel = Frame(root, bd=1)
right_panel.grid(column=1, row=0, sticky='nsew')
right_panel.rowconfigure(0, weight=1)
right_panel.columnconfigure(0, weight=1)

# Listbox with scrollbar
mistake_sentence_label = Label(right_panel, text='Misspelled sentence: None')
misspelled_word_label = Label(right_panel, text='Misspelled word:')
scrollbar = Scrollbar(right_panel, orient='vertical')
listbox = Listbox(right_panel, activestyle='dotbox', yscrollcommand=scrollbar.set)
scrollbar2 = Scrollbar(right_panel, orient='vertical')
listbox2 = Listbox(right_panel, activestyle='dotbox', yscrollcommand=scrollbar2.set)

mistake_sentence_label.grid(column=0, row=0, sticky='n')
misspelled_word_label.grid(column=0, row=2, sticky='ns')
listbox.grid(column=0, row=1, sticky='news', padx=10)
scrollbar.grid(column=0, row=1, sticky='nse')
listbox2.grid(column=0, row=3, sticky='news', padx=10)
scrollbar2.grid(column=0, row=3, sticky='nse')

# Search bar
search_bar = Frame(right_panel, relief=RAISED)
search_bar.grid(column=0, row=4, sticky='s')
search_bar.rowconfigure(0, weight=1)
search_bar.columnconfigure(0, weight=1)

search_label = Label(search_bar, text='Search word:')
search_input = Text(search_bar, height=1)
search_input.bind('<KeyRelease>', search_word)

search_label.grid(column=0, row=0, sticky='se')
search_input.grid(column=1, row=0, sticky='ws', padx=10, pady=5)

root.mainloop()
