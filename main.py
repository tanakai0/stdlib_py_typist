import platform
import random
import sqlite3
import tkinter as tk
import winsound
from pathlib import Path
from tkinter import ttk
from typing import List, Tuple


class TypingGameApp:
    N, W, E, S = tk.N, tk.W, tk.E, tk.S
    TYPING = "Typing"
    QUIZ = "Quiz"
    DOW = "DoW"
    TIME_LIMIT = "Time Limit"
    FIXED_QUIZ = "Fixed Quiz"
    ENDLESS_QUIZ = "Endless Quiz"

    def __init__(self, root, database_path):
        self.database_path = database_path
        self.root = root
        self.root.title("Typing Game")
        self.mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
        self.on_windows_os = platform.system() == "Windows"
        self.sound_available = self.on_windows_os
        if self.sound_available:
            self.correct_sound = "./assets/sound/pinpon2.wav"
            self.incorrect_sound = "./assets/sound/bubbu1.wav"
            self.title_music = "./assets/sound/scene3.wav"

        self.texts = self.load_texts(self.database_path)
        self.current_text = ""

        self.title_label = tk.Label(
            self.mainframe, text="Typing Game", font=("Helvetica", 36)
        )

        self.game_mode_label = tk.Label(
            self.mainframe, text="Game\n Mode", font=("Helvetica", 12)
        )
        self.game_mode = tk.StringVar(None, self.TYPING)
        self.typing_radio_button = ttk.Radiobutton(
            self.mainframe, text=self.TYPING, variable=self.game_mode, value=self.TYPING
        )
        self.quiz_radio_button = ttk.Radiobutton(
            self.mainframe, text=self.QUIZ, variable=self.game_mode, value=self.QUIZ
        )
        self.DoW_radio_button = ttk.Radiobutton(
            self.mainframe, text=self.DOW, variable=self.game_mode, value=self.DOW
        )

        self.challenge_mode_label = tk.Label(
            self.mainframe, text="Challenge\n Mode", font=("Helvetica", 12)
        )
        self.challenge_mode = tk.StringVar(None, self.ENDLESS_QUIZ)
        self.time_limit_radio_button = ttk.Radiobutton(
            self.mainframe,
            text=self.TIME_LIMIT,
            variable=self.challenge_mode,
            value=self.TIME_LIMIT,
        )
        self.FIXED_QUIZ_radio_button = ttk.Radiobutton(
            self.mainframe,
            text=self.FIXED_QUIZ,
            variable=self.challenge_mode,
            value=self.FIXED_QUIZ,
        )
        self.ENDLESS_QUIZ_radio_button = ttk.Radiobutton(
            self.mainframe,
            text=self.ENDLESS_QUIZ,
            variable=self.challenge_mode,
            value=self.ENDLESS_QUIZ,
        )

        self.start_button = tk.Button(
            self.mainframe, text="Start Game", command=self.push_start_button
        )

        self.text_label = tk.Label(self.mainframe, text="", font=("Helvetica", 24))
        self.user_input = tk.StringVar()
        self.user_input_entry = tk.Entry(
            self.mainframe, textvariable=self.user_input, font=("Helvetica", 18)
        )
        self.user_input_entry.bind("<Return>", self.check_text)

        self.set_title_screen()
        self.new_text()

    def load_texts(self, database_path: str) -> List[Tuple[str, str]]:
        """
        Load question and explanation texts from an SQLite database.

        Parameters
        ----------
        database_path : str
            Path to the SQLite database file.

        Returns
        -------
         _ : List[Tuple[str, str]]
            List of tuples containing question and explanation texts.
        """
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute("SELECT question, explanation FROM text_typing")
        data = c.fetchall()
        conn.close()

        return data

    def set_title_screen(self):
        self.mainframe.grid(row=0, column=0, sticky=(self.N, self.S, self.E, self.W))
        # self.resizable_mode()
        if self.sound_available:
            winsound.PlaySound(
                self.title_music,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
            )
        self.title_label.grid(column=0, row=0, columnspan=4, pady=20)
        self.game_mode_label.grid(column=0, row=1, rowspan=3, padx=5)
        self.typing_radio_button.grid(column=1, row=2, sticky=self.W)
        self.quiz_radio_button.grid(column=1, row=3, sticky=self.W)
        self.DoW_radio_button.grid(column=1, row=4, sticky=self.W)
        self.challenge_mode_label.grid(column=2, row=1, rowspan=3, padx=5)
        self.time_limit_radio_button.grid(column=3, row=2, sticky=self.W)
        self.FIXED_QUIZ_radio_button.grid(column=3, row=3, sticky=self.W)
        self.ENDLESS_QUIZ_radio_button.grid(column=3, row=4, sticky=self.W)
        self.start_button.grid(column=0, row=5, columnspan=4, pady=5)

    def unset_title_screen(self):
        self.title_label.grid_forget()
        self.game_mode_label.grid_forget()
        self.typing_radio_button.grid_forget()
        self.quiz_radio_button.grid_forget()
        self.DoW_radio_button.grid_forget()
        self.challenge_mode_label.grid_forget()
        self.time_limit_radio_button.grid_forget()
        self.FIXED_QUIZ_radio_button.grid_forget()
        self.ENDLESS_QUIZ_radio_button.grid_forget()
        self.start_button.grid_forget()

        if self.sound_available:
            winsound.PlaySound(None, winsound.SND_PURGE)

    def push_start_button(self):
        challenge_mode = self.challenge_mode.get()
        match challenge_mode:
            case self.TIME_LIMIT:
                self.set_ENDLESS_QUIZ_screen()  # temp
            case self.FIXED_QUIZ:
                self.set_ENDLESS_QUIZ_screen()  # temp
            case self.ENDLESS_QUIZ:
                self.set_ENDLESS_QUIZ_screen()
            case _:
                raise ValueError(f"{challenge_mode} is invalid challenge mode.")

    def set_ENDLESS_QUIZ_screen(self):
        self.unset_title_screen()
        self.text_label.pack(pady=20)
        self.user_input_entry.pack(pady=10)
        self.user_input_entry.focus_set()

    def resizable_mode(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.columnconfigure(2, weight=1)
        self.mainframe.columnconfigure(3, weight=1)
        self.mainframe.rowconfigure(1, weight=1)

    def new_text(self):
        self.current_text = random.choice(self.texts)[0]
        self.text_label.config(text=self.current_text, fg="black")

    def check_text(self, event):
        user_text = self.user_input.get()
        if user_text == self.current_text:
            self.text_label.config(text="Correct!", fg="green")
            if self.sound_available:
                winsound.PlaySound(
                    self.correct_sound, winsound.SND_FILENAME | winsound.SND_ASYNC
                )
        else:
            self.text_label.config(text="Incorrect!", fg="red")
            if self.sound_available:
                winsound.PlaySound(
                    self.incorrect_sound, winsound.SND_FILENAME | winsound.SND_ASYNC
                )
        self.user_input.set("")
        self.root.after(500, self.new_text)


def main():
    root = tk.Tk()
    database_path = Path("./assets/database/typing_game.db")
    _ = TypingGameApp(root, database_path)
    root.mainloop()


if __name__ == "__main__":
    main()
