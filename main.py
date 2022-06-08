from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkmacosx import Button
from spellchecker import SpellChecker

spell = SpellChecker()

root = Tk()
root.title('NLP Demonstration: Spelling Correction')
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)


def analyze_text():
    text = user_input_textbox.get('1.0', END)
    print('text: ', text)
    # SAMPLE TEXT: Let us wlak on the groun
    split_text = text.split()
    print('split_text: ', split_text)

    misspelled = spell.unknown(split_text)
    print('type(misspelled): ', type(misspelled))
    print('misspelled: ', misspelled)

    if len(misspelled) > 0:
        print('misspelled: ', misspelled)
        show_recommended_words(list(misspelled)[0])
        mark_red_text()

    # user_input_textbox.delete(1.0, 'end')
    # for original_word in split_text:
    #     if original_word in misspelled:
    #         # TODO: mark the word in the textbox
    #         mark_red_text()
    #         corrected_word = spell.correction(original_word)
    #         print('corrected_word: ', corrected_word)
    #         user_input_textbox.insert(END, corrected_word)
    #         show_recommended_words(original_word)
    #         break

    user_input_textbox.focus_set()


def mark_red_text():
    user_input_textbox.tag_add('red', '1.0', 'end')
    user_input_textbox.tag_config('red', foreground='red')


def clear_tags():
    user_input_textbox.tag_remove('red', '1.0', 'end')


def show_recommended_words(wrong_word):
    misspelled_word_label.config(text='Misspelled word: ' + wrong_word)
    recommended_words = spell.candidates(wrong_word)
    print('recommended_words: ', recommended_words)
    listbox.delete(0, END)
    for word in recommended_words:
        listbox.insert(END, word)


def search_word():
    # TODO: search the word in the dictionary
    print('search_word')
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
listbox.grid(column=0, row=1, sticky='new', padx=10, pady=5)
scrollbar.grid(column=0, row=1, sticky='nse')

# Search bar
search_bar = Frame(right_panel, relief=RAISED)
search_bar.grid(column=0, row=1, sticky='s')
search_bar.rowconfigure(0, weight=1)
search_bar.columnconfigure(0, weight=1)

search_label = Label(search_bar, text='Search:')
search_input = Text(search_bar, height=1)
search_button = Button(search_bar, text='Search', command=search_word)

search_label.grid(column=0, row=0, sticky='se')
search_input.grid(column=1, row=0, sticky='ws', padx=5, pady=5)
search_button.grid(column=2, row=0, sticky='se')

root.mainloop()
