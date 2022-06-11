from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkmacosx import Button
from spellchecker import SpellChecker

spell = SpellChecker(language='en')

current_text = 'let us wlak on the groun'
current_wrong_word = ''
recommended_words = []
recommended_words_search_result = []

root = Tk()
root.title('NLP Demonstration: Spelling Correction')
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)


def analyze_text():
    global current_text
    global current_wrong_word
    current_text = user_input_textbox.get('1.0', END)
    split_text = current_text.split()

    misspelled = spell.unknown(split_text)

    clear_recommended_words()
    if len(misspelled) > 0:
        current_wrong_word = list(misspelled)[0]
        show_recommended_words(current_wrong_word)
    user_input_textbox.focus_set()


def on_select(event):
    print('on_select')
    selected_item = listbox.get(ANCHOR)
    print('selected_item: ', selected_item)
    correct_misspelled_word(selected_item)


def clear_recommended_words():
    misspelled_word_label.config(text='Misspelled word: None')
    listbox.delete(0, END)
    listbox.unbind('<Double-1>')


def show_recommended_words(wrong_word):
    global recommended_words
    misspelled_word_label.config(text='Misspelled word: ' + wrong_word)
    recommended_words = spell.candidates(wrong_word)
    print('recommended_words: ', recommended_words)
    for word in recommended_words:
        listbox.insert(END, word)
    listbox.bind('<Double-1>', on_select)


def correct_misspelled_word(corrected_word):
    global current_text
    global current_wrong_word
    user_input_textbox.delete(1.0, 'end')
    split_text = current_text.split()

    for i in range(len(split_text)):
        if split_text[i] in current_wrong_word:
            split_text[i] = corrected_word
            break

    new_sentence = ' '.join(split_text)
    user_input_textbox.insert(END, new_sentence)
    analyze_text()  # Analyze again


def search_word(event):
    # TODO:

    return


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

btn_submit = Button(frm_buttons, text='Submit', command=analyze_text, background='#00CA4E', foreground='white')
btn_exit = Button(frm_buttons, text='Exit', command=close, background='#FF605C', foreground='white')
btn_submit.grid(column=0, row=1, sticky='nsew')
btn_exit.grid(column=0, row=2, sticky='nsew')

# User input
user_input = Frame(left_panel, relief=RAISED)
user_input.rowconfigure(0, weight=1)
user_input.columnconfigure(0, weight=1)

user_input_label = Label(user_input, text='Input:')
user_input_label.grid(column=0, row=0, sticky='nw')
user_input_textbox = ScrolledText(user_input)
user_input_textbox.grid(column=0, row=1, sticky='s')
user_input_textbox.insert(END, current_text)
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
search_button = Button(search_bar, text='Search', command=search_word)
search_input.bind("<Key>", search_word)

search_label.grid(column=0, row=0, sticky='se')
search_input.grid(column=1, row=0, sticky='ws', padx=5, pady=5)
search_button.grid(column=2, row=0, sticky='se')

root.mainloop()
