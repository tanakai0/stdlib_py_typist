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
        
        self.start_button = tk.Button(
            self.mainframe, text="Start Game", command=self.typing_screen_grid_manager
        )

        self.set_title_screen()

        self.text_label = tk.Label(self.mainframe, text="", font=("Helvetica", 24))
        self.user_input = tk.StringVar()
        self.user_input_entry = tk.Entry(
            self.mainframe, textvariable=self.user_input, font=("Helvetica", 18)
        )
        self.user_input_entry.bind("<Return>", self.check_text)

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
        List[Tuple[str, str]]:
            List of tuples containing question and explanation texts.
        """
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute("SELECT question, explanation FROM text_typing")
        data = c.fetchall()
        conn.close()

        return data
    
    def select_mode(mode):
        start_game(mode)

    def set_title_screen(self):
        self.mainframe.grid(row=0, column=0, sticky=(self.N, self.S, self.E, self.W))
        self.resizable_mode()
        self.title_label.pack(pady=50)
        self.start_button.pack()
        if self.sound_available:
            winsound.PlaySound(
                self.title_music,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
            )

    def unset_title_screen(self):
        self.title_label.pack_forget()
        self.start_button.pack_forget()
        if self.sound_available:
            winsound.PlaySound(None, winsound.SND_PURGE)

    def typing_screen_grid_manager(self):
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
