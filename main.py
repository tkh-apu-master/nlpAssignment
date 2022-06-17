from tkinter import *
from tkinter.scrolledtext import ScrolledText
import re
import pkg_resources

from tkmacosx import Button
from spellchecker import SpellChecker
from symspellpy import SymSpell

spell = SpellChecker()

sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
bigram_path = pkg_resources.resource_filename("symspellpy", "frequency_bigramdictionary_en_243_342.txt")

sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)

current_sentence = ''

# Sample wrong sentences
# current_sentence = 'let us wlak on the groun. it\'s weird that...'
# current_sentence = 'It is a truth unіversally acknowledged, that a single man in possesssion of a good fortune must be' \
#                    ' in want of a wife. However little known the feelings or views of such a man may be on his first' \
#                    ' entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families,' \
#                    ' that he is considered as the rightful property of some one or other of their daugters.'
current_wrong_word = ''
recommended_words = []
recommended_words_search_result = []

root = Tk()
root.title('NLP Demonstration: Spelling Correction')
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)


def submit():
    global current_sentence
    current_sentence = user_input_textbox.get('1.0', END)

    require_check = check_sentence()

    if require_check:
        return
        # TODO: Suggest correct sentence spacing
    else:
        analyze_text()

    user_input_textbox.focus_set()


# TODO: Analyze sentence and suggest correct spacing
def check_sentence():
    # print('Check using SymSpell: ')
    # print('When checking as a sentence: ')
    # suggestions = sym_spell.lookup_compound(current_sentence, max_edit_distance=2)
    # print('suggestions: ', suggestions)
    # for suggestion in suggestions:
    #     print('Sentence suggestion: ', suggestion)
    # print('When checking word by word: ')
    # for word in split_text:
    #     suggestions = sym_spell.lookup_compound(word, max_edit_distance=2)
    #     print('suggestions: ', suggestions)
    #     for suggestion in suggestions:
    #         print(word, ' suggestion: ', suggestion)
    return False


def analyze_text():
    global current_sentence
    global current_wrong_word
    # Split sentence into words precisely using regex: https://stackoverflow.com/a/26209841
    split_text = re.findall(r"(?<![@#])\b\w+(?:'\w+)?", current_sentence)
    misspelled = spell.unknown(split_text)

    clear_recommended_words()
    if len(misspelled) > 0:
        current_wrong_word = list(misspelled)[0]
        show_recommended_words(current_wrong_word)


def clear_input():
    user_input_textbox.delete(1.0, 'end')
    user_input_textbox.focus_set()


def on_select(event):
    selected_item = listbox.get(ANCHOR)
    correct_misspelled_word(selected_item)
    submit()  # Analyze again


def clear():
    clear_input()
    clear_recommended_words()


def clear_recommended_words():
    global recommended_words_search_result
    recommended_words_search_result.clear()
    misspelled_word_label.config(text='Misspelled word: None')
    listbox.delete(0, END)
    listbox.unbind('<Double-1>')


def show_recommended_words(wrong_word):
    global recommended_words
    misspelled_word_label.config(text='Misspelled word: ' + wrong_word)
    recommended_words = list(spell.candidates(wrong_word))
    for word in recommended_words:
        listbox.insert(END, word)
    listbox.bind('<Double-1>', on_select)


def correct_misspelled_word(corrected_word):
    global current_sentence
    global current_wrong_word
    user_input_textbox.delete(1.0, 'end')
    split_text = current_sentence.split()

    for i in range(len(split_text)):
        if split_text[i] in current_wrong_word:
            split_text[i] = corrected_word
            break

    current_sentence = current_sentence.replace(current_wrong_word, corrected_word)
    user_input_textbox.insert(END, current_sentence)


def search_word(event):
    global recommended_words_search_result
    listbox.delete(0, END)
    listbox.unbind('<Double-1>')
    recommended_words_search_result.clear()
    search_keyword = search_input.get(1.0, 'end')

    for i in range(len(recommended_words)):
        if search_keyword in recommended_words[i]:
            recommended_words_search_result.append(recommended_words[i])

    # If search_keyword is empty, show all recommended words as default
    if len(search_keyword) == 1:
        recommended_words_search_result.extend(recommended_words)

    for word in recommended_words_search_result:
        listbox.insert(END, word)
    listbox.bind('<Double-1>', on_select)


def close():
    root.destroy()


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

btn_submit = Button(frm_buttons, text='Submit', command=submit, background='#00CA4E', foreground='black')
btn_clear = Button(frm_buttons, text='Clear', command=clear, background='#FFBD44', foreground='black')
btn_exit = Button(frm_buttons, text='Exit', command=close, background='#FF605C', foreground='black')
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
misspelled_word_label = Label(right_panel, text='Misspelled word:')
scrollbar = Scrollbar(right_panel, orient="vertical")
listbox = Listbox(right_panel, activestyle='dotbox', yscrollcommand=scrollbar.set)

misspelled_word_label.grid(column=0, row=0, sticky='n')
listbox.grid(column=0, row=1, sticky='news', padx=10)
scrollbar.grid(column=0, row=1, sticky='nse')

# Search bar
search_bar = Frame(right_panel, relief=RAISED)
search_bar.grid(column=0, row=1, sticky='s')
search_bar.rowconfigure(0, weight=1)
search_bar.columnconfigure(0, weight=1)

search_label = Label(search_bar, text='Search:')
search_input = Text(search_bar, height=1)
search_input.bind("<KeyRelease>", search_word)

search_label.grid(column=0, row=0, sticky='se')
search_input.grid(column=1, row=0, sticky='ws', padx=10, pady=5)

root.mainloop()
