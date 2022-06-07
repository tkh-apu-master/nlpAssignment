from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkmacosx import Button

root = Tk()
root.title('NLP Demonstration: Spelling Correction')
root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)


def analyze_text():
    text = user_input_textbox.get('1.0', END)
    print('text: ', text)
    split_text = text.split()
    print('split_text: ', split_text)


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

# Listbox with scrollbar
scrollbar = Scrollbar(right_panel, orient="vertical")
listbox = Listbox(right_panel, activestyle='dotbox', yscrollcommand=scrollbar.set)
right_panel.rowconfigure(0, weight=1)
right_panel.columnconfigure(0, weight=1)

# Sample data
for i in range(1, 50):
    listbox.insert(i, i)

listbox.grid(column=1, row=0, sticky='nsew', padx=10, pady=5)
scrollbar.grid(column=1, row=0, sticky='nse')

# Search bar
search_bar = Frame(right_panel, relief=RAISED)

search_label = Label(search_bar, text='Search:')
search_label.grid(column=0, row=0, sticky='se')
search_input = Text(search_bar, height=1)
search_input.grid(column=1, row=0, sticky='ws', padx=5, pady=5)

search_bar.grid(column=1, row=1, sticky='s')

root.mainloop()
