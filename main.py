from tkinter import *
from tkinter.scrolledtext import ScrolledText

import nltk
import pkg_resources
from spellchecker import SpellChecker
from symspellpy import SymSpell
from textblob import TextBlob, Word
from tkmacosx import Button

from real_word_custom_spell_check import *

nltk.download('punkt')

# Strategy: Use Norvig with SymSpell approach, which improves speed, memory consumption and accuracy
# Reference: https://towardsdatascience.com/spelling-correction-how-to-make-an-accurate-and-fast-corrector-dc6d0bcbba5f

spell = SpellChecker(case_sensitive=True)
spell.word_frequency.load_text_file('datasets/correct_words.txt')

sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

dictionary_path = pkg_resources.resource_filename('symspellpy', 'frequency_dictionary_en_82_765.txt')
bigram_path = pkg_resources.resource_filename('symspellpy', 'frequency_bigramdictionary_en_243_342.txt')

sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)

# current_sentence = ''

# SAMPLE WRONG SENTENCES (COVERS MOST CASES)
current_sentence = 'let us wlak on the groun.'
# current_sentence = 'It is a truth unіversally acknowledged, that a single man in possesssion of a good fortune must be' \
#                    ' in want of a wife. However little known the feelings or views of such a man may be on his first' \
#                    ' entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families,' \
#                    ' that he is considered as the rightful property of some one or other of their daugters.'
# current_sentence = 'I enjoyd the event which took place yesteday &amp; I luvd it ! The link to the show is '
# current_sentence = 'I took a message yesterday' # Testing sample real word misspellings
# current_sentence = 'Uber app is   very bad  to use. What a mess!'
# current_sentence = 'GFG is a good compny and alays value ttheir employes.'
# current_sentence = 'I amm goodd at spelling mstake.'
# current_sentence = 'acress'
# current_sentence = 'two of thew'
# current_sentence = 'i have an apply'
# current_sentence = 'thequickbrownfoxjumpsoverthelazydog'
# current_sentence = 'thequickbrownfoxjumpsoverthelaszydog'

current_wrong_word = ''
recommended_sentence_fixes = []
recommended_word_fixes = []
recommended_fixes_search_result = []

root = Tk()
root.title('NLP Demonstration: Spelling Correction')
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)


def analyze(word=None):
    if word:
        split_text = [word]
        clear_recommended_fixes()
        need_fix = analyze_text(split_text)
    else:
        global current_sentence
        clear_recommended_fixes()
        current_sentence = user_input_textbox.get('1.0', END)
        # Split sentence into words precisely using regex: https://stackoverflow.com/a/26209841
        split_text = re.findall(r"(?<![@#])\b\w+(?:'\w+)?", current_sentence)
        need_fix = check_sentence_segmentation(split_text)
        if need_fix:
            display_recommended_sentence_fixes()
            if split_text == 1:
                need_fix = analyze_text(split_text)
        else:
            need_fix = analyze_text(split_text)

        if need_fix:
            display_recommended_word_fixes()

        user_input_textbox.focus_set()

    return need_fix


# Analyze the sentence and suggest correct word segmentation & grammar
def check_sentence_segmentation(split_text):
    global current_sentence
    global recommended_sentence_fixes
    global recommended_word_fixes
    global current_wrong_word

    # Step 1: Check word segmentation with symspell
    word_segmentation_suggestions = sym_spell.word_segmentation(current_sentence)

    if len(word_segmentation_suggestions) > 0:
        # Only takes the most recommended suggestion
        add_sentence_suggestion(word_segmentation_suggestions[0])

    # If you got a sentence that has issue with word segmentation, and there's recommended fix. stop here
    # Return True to prevent further unnecessary checks
    if len(split_text) == 1 and len(recommended_sentence_fixes) == 1:
        return True

    if len(recommended_sentence_fixes) > 0:
        mistake_sentence_label.config(text='Sentence suggestions:')
        return True

    return False


# Helper function to add a sentence suggestion to the list of recommended fixes
# with standardized formatting and validations.
def add_sentence_suggestion(corrected_sentence):
    global recommended_sentence_fixes

    if str(corrected_sentence).strip() != current_sentence.strip() and \
            corrected_sentence not in recommended_sentence_fixes:
        recommended_sentence_fixes.append(str(corrected_sentence).strip())


# Perform word by word analysis
def analyze_text(split_text):
    global current_sentence
    global current_wrong_word
    global recommended_word_fixes

    # Step 1: Check word spelling with symspell
    misspelled = spell.unknown(split_text)
    correct_word_list = spell.known(split_text)
    print('correct_word_list: ' , correct_word_list)
    if len(misspelled) > 0:
        for index in range(len(split_text)):
            full_uppercase = re.findall('[A-Z]', split_text[index])
            is_full_uppercase = len(full_uppercase) == len(split_text[index])

            # A word that is Fully uppercase and recognized as misspelled
            if str(split_text[index]).lower() in list(misspelled) and not is_full_uppercase:
                current_wrong_word = split_text[index]
                print('step 1 current_wrong_word:', current_wrong_word)
                candidates = spell.candidates(current_wrong_word)

                if candidates is not None:
                    candidates = list(candidates)
                    candidates.sort()
                    print('step 1 candidates:', candidates)
                    recommended_word_fixes = candidates
                else:
                    recommended_word_fixes = []
                break
            else:
                recommended_word_fixes = []

    if len(recommended_word_fixes) > 0:
        return True

    # Step 2: use SymSpell to find similar words
    symspell_suggestions = sym_spell.lookup_compound(current_sentence, max_edit_distance=2, transfer_casing=True,
                                                     ignore_non_words=True)

    # symspell_suggestions variable has the following format (suggestion term, edit distance, term frequency)
    split_text2 = re.findall(r"(?<![@#])\b\w+(?:'\w+)?", symspell_suggestions[0].term)

    if len(split_text2) > 0:
        for index in range(len(split_text)):
            current_sentence_word = split_text[index]
            suggested_sentence_word = split_text2[index]

            if suggested_sentence_word != current_sentence_word and str(current_sentence_word).lower() not in list(correct_word_list):
                print('step 2 current_sentence_word:', current_sentence_word)
                print('step 2 suggested_sentence_word:', suggested_sentence_word)

            if current_sentence_word != suggested_sentence_word and suggested_sentence_word not in recommended_word_fixes:
                current_wrong_word = split_text[index]
                recommended_word_fixes.append(split_text2[index])
                break

    if len(recommended_word_fixes) > 0:
        return True

    # Step 3: Use TextBlob to find similar words
    for index in range(len(split_text)):
        current_sentence_word = split_text[index]

        w = Word(split_text[index])
        textblob_word_suggestions = w.spellcheck()
        for similar_word in textblob_word_suggestions:
            print('similar_word: ', similar_word)
            suggested_sentence_word = str(similar_word[0]).rstrip()

            if suggested_sentence_word != current_sentence_word:
                print('step 3 current_sentence_word:', current_sentence_word)
                print('step 3 suggested_sentence_word:', suggested_sentence_word)

            if suggested_sentence_word not in recommended_word_fixes and \
                    suggested_sentence_word != current_sentence_word and \
                    str(current_sentence_word).lower() not in list(correct_word_list):
                current_wrong_word = current_sentence_word
                recommended_word_fixes.append(suggested_sentence_word)
                break

    if len(recommended_word_fixes) > 0:
        return True

    # Step 4: Check if the sentence is correct with TextBlob
    textblob_sentence = TextBlob(current_sentence)
    corrected_sentence = textblob_sentence.correct()
    print('step 4 corrected_sentence:', corrected_sentence)

    # Need to convert TextBlob object to string with filtered out '\n' first
    textblob_fixed_sentence = str(corrected_sentence)[:-1]

    corrected_sentence_split_words = nltk.word_tokenize(textblob_fixed_sentence)

    if len(corrected_sentence_split_words) > 0:
        for index in range(len(split_text)):
            word_suggestion = corrected_sentence_split_words[index]
            if split_text[index] != word_suggestion and \
                    word_suggestion not in recommended_word_fixes and \
                    str(split_text[index]).lower() not in list(correct_word_list):
                current_wrong_word = split_text[index]
                recommended_word_fixes.append(str(corrected_sentence_split_words[index]).rstrip())
                break

    if len(recommended_word_fixes) > 0:
        return True

    return False


# Clear the user input at the left panel
def clear_input():
    user_input_textbox.delete(1.0, 'end')
    user_input_textbox.focus_set()


# Event handler for the sentence recommendation in list box
def on_sentence_select(event):
    selected_item = sentence_listbox.get(ANCHOR)
    correct_misspelled_sentence(selected_item)
    clear_recommended_fixes()
    analyze()  # Analyze again


# Event handler for the word recommendation in list box
def on_correct_word_select(event):
    selected_item = recommended_word_listbox.get(ANCHOR)
    correct_misspelled_word(selected_item)
    analyze()  # Analyze again


# Clear user input and recommended fixes
def clear():
    clear_input()
    clear_recommended_fixes()


# Helper function to clear the recommended fixes in the GUI (labels and list boxes)
def clear_recommended_fixes():
    global recommended_fixes_search_result
    global recommended_sentence_fixes
    global recommended_word_fixes
    global current_wrong_word
    global current_sentence
    current_wrong_word = ''
    current_sentence = ''
    recommended_fixes_search_result.clear()
    recommended_sentence_fixes.clear()
    recommended_word_fixes.clear()
    mistake_sentence_label.config(text='Misspelled sentence: None')
    misspelled_word_label.config(text='Misspelled word: None')
    sentence_listbox.delete(0, END)
    sentence_listbox.unbind('<Double-1>')
    recommended_word_listbox.delete(0, END)
    recommended_word_listbox.unbind('<Double-1>')


def get_recommended_word_fixes(wrong_word):
    global current_wrong_word
    global recommended_word_fixes
    # Step 4: Use custom functions to find similar words
    closest_word_result = closest_word(wrong_word)
    if closest_word_result not in recommended_word_fixes and closest_word_result != wrong_word.lower():
        current_wrong_word = wrong_word
        recommended_word_fixes.append(closest_word_result)

    return recommended_word_fixes


def display_recommended_sentence_fixes():
    global recommended_sentence_fixes
    for sentence in recommended_sentence_fixes:
        sentence_listbox.insert(END, sentence)
    sentence_listbox.bind('<Double-1>', on_sentence_select)


def display_recommended_word_fixes():
    global recommended_word_fixes
    global current_wrong_word
    misspelled_word_label.config(text='Misspelled word: ' + current_wrong_word)
    for word in recommended_word_fixes:
        recommended_word_listbox.insert(END, word)
    recommended_word_listbox.bind('<Double-1>', on_correct_word_select)


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


def search_recommended_word(event):
    global recommended_word_fixes
    global recommended_fixes_search_result
    recommended_word_listbox.delete(0, END)
    recommended_word_listbox.unbind('<Double-1>')
    recommended_fixes_search_result.clear()
    search_keyword = search_input.get(1.0, 'end')

    for i in range(len(recommended_word_fixes)):
        if search_keyword.strip() in str(recommended_word_fixes[i]):
            recommended_fixes_search_result.append(recommended_word_fixes[i])

    # If search_keyword is empty, show all recommended words as default
    if len(search_keyword) == 1:
        recommended_fixes_search_result.clear()
        recommended_fixes_search_result.extend(recommended_word_fixes)

    for word in recommended_fixes_search_result:
        recommended_word_listbox.insert(END, word)
    recommended_word_listbox.bind('<Double-1>', on_correct_word_select)


# A function that analyze the accuracy of the spell checker, with using misspelling corpora, and display the results.
def spelling_corrector_analysis():
    # Analyze accuracy
    correct_count = 0
    wrong_count = 0
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    counter = 0
    for (word, actual_word_is_correct) in word_set:
        print('counter: ', counter)
        word_is_wrong = analyze(word)
        print('recommended_word_fixes: ', recommended_word_fixes)

        if word_is_wrong:
            if actual_word_is_correct:
                wrong_count += 1
                FP += 1
            else:
                correct_count += 1
                TP += 1
        else:
            if actual_word_is_correct:
                correct_count += 1
                TN += 1
            else:
                wrong_count += 1
                FN += 1
        counter += 1

    print('Summary of spell corrector analysis:')
    print('length of word_set: ', len(word_set))
    print('TP: ', TP)
    print('TN: ', TN)
    print('FP: ', FP)
    print('FN: ', FN)
    print('correct_count: ', correct_count)
    print('wrong_count: ', wrong_count)
    accuracy = correct_count / len(word_set)
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1 = 2 * precision * recall / (precision + recall)
    print('accuracy: ', accuracy * 100, '%')
    print('precision: ', precision * 100, '%')
    print('recall: ', recall * 100, '%')
    print('f1: ', f1)


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

btn_spelling_corrector_analysis = Button(frm_buttons, text='Spelling Corrector Accuracy Analysis',
                                         command=spelling_corrector_analysis, background='grey')
btn_sentence_submit = Button(frm_buttons, text='Submit', command=analyze, background='#00CA4E',
                             foreground='black')
btn_clear = Button(frm_buttons, text='Clear', command=clear, background='#FFBD44', foreground='black')
btn_exit = Button(frm_buttons, text='Exit', command=close, background='#FF605C', foreground='black')
btn_spelling_corrector_analysis.grid(column=0, row=0, sticky='nsew')
btn_sentence_submit.grid(column=0, row=1, sticky='nsew')
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

# Listboxes with scrollbars
mistake_sentence_label = Label(right_panel, text='Misspelled sentence: None')
misspelled_word_label = Label(right_panel, text='Misspelled word: None')
recommended_sentence_listbox_scrollbar = Scrollbar(right_panel, orient='vertical')
sentence_listbox = Listbox(right_panel, activestyle='dotbox', yscrollcommand=recommended_sentence_listbox_scrollbar.set)
recommended_word_listbox_scrollbar = Scrollbar(right_panel, orient='vertical')
recommended_word_listbox = Listbox(right_panel, activestyle='dotbox',
                                   yscrollcommand=recommended_word_listbox_scrollbar.set)

mistake_sentence_label.grid(column=0, row=0, sticky='n')
misspelled_word_label.grid(column=0, row=2, sticky='ns')
sentence_listbox.grid(column=0, row=1, sticky='news', padx=10)
recommended_sentence_listbox_scrollbar.grid(column=0, row=1, sticky='nse')
recommended_word_listbox.grid(column=0, row=3, sticky='news', padx=10)
recommended_word_listbox_scrollbar.grid(column=0, row=3, sticky='nse')

# Search bar
search_bar = Frame(right_panel, relief=RAISED)
search_bar.grid(column=0, row=4, sticky='s')
search_bar.rowconfigure(0, weight=1)
search_bar.columnconfigure(0, weight=1)

search_label = Label(search_bar, text='Search word:')
search_input = Text(search_bar, height=1)
search_input.bind('<KeyRelease>', search_recommended_word)

search_label.grid(column=0, row=0, sticky='se')
search_input.grid(column=1, row=0, sticky='ws', padx=10, pady=5)

root.mainloop()
