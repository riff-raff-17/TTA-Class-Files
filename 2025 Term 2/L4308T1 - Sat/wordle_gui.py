import tkinter as tk
from tkinter import messagebox, ttk
from wordlebot import WordleSolver, load_word_list

class WordleGUI:
    def __init__(self, master):
        self.master = master
        master.title("Wordle Solver")
        master.geometry("400x550")
        master.resizable(False, False)

        # Apply a clean theme and colors
        style = ttk.Style(master)
        style.theme_use('clam')
        style.configure('TFrame', background = '#c4ba6a')
        style.configure('Guess.TLabel', background='#fafafa', 
                        font=('Helvetica', 20, 'bold'))
        style.configure('TLabel', background='#fafafa', font=('Helvetica', 12))
        style.configure('TButton', font=('Helvetica', 12), padding=6)

        master.configure(bg='#fafafa')

        # Main container
        container = ttk.Frame(master, padding=20, style='TFrame')
        