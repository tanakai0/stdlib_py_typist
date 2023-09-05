import platform
import tkinter as tk
import winsound
from tkinter import ttk

from src.quiz import StaticQuizzes


class TypingGameApp:
    N, W, E, S = tk.N, tk.W, tk.E, tk.S
    TIME_LIMIT = "Time Limit"
    FIXED_QUIZ = "Fixed Quiz"
    ENDLESS_QUIZ = "Endless Quiz"

    def __init__(self, root, database_path) -> None:
        self.database_path = database_path
        self.root = root
        self.root.title("Typing Game")
        self.mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
        self.on_windows_os = platform.system() == "Windows"
        self.sound_available = self.on_windows_os
        self.widgets = []
        self.quizzes = StaticQuizzes(database_path)
        if self.sound_available:
            self.correct_sound = "./assets/sound/pinpon2.wav"
            self.incorrect_sound = "./assets/sound/bubbu1.wav"
            self.title_music = "./assets/sound/scene3.wav"

        self.question = ""

        self.title_label = tk.Label(
            self.mainframe, text="Typing Game", font=("Helvetica", 36)
        )

        self.quiz_mode_label = tk.Label(
            self.mainframe, text="Challenge\n Mode", font=("Helvetica", 12)
        )
        self.quiz_mode = tk.StringVar(None, self.ENDLESS_QUIZ)
        self.time_limit_radio_button = ttk.Radiobutton(
            self.mainframe,
            text=self.TIME_LIMIT,
            variable=self.quiz_mode,
            value=self.TIME_LIMIT,
        )
        self.FIXED_QUIZ_radio_button = ttk.Radiobutton(
            self.mainframe,
            text=self.FIXED_QUIZ,
            variable=self.quiz_mode,
            value=self.FIXED_QUIZ,
        )
        self.ENDLESS_QUIZ_radio_button = ttk.Radiobutton(
            self.mainframe,
            text=self.ENDLESS_QUIZ,
            variable=self.quiz_mode,
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

    def set_title_screen(self) -> None:
        self.mainframe.grid(row=0, column=0, sticky=(self.N, self.S, self.E, self.W))
        # self.resizable_mode()
        if self.sound_available:
            winsound.PlaySound(
                self.title_music,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
            )
        self.title_label.grid(column=0, row=0, columnspan=4, pady=20)
        self.start_button.grid(column=0, row=5, columnspan=4, pady=5)
        self.widgets += [self.title_label, self.start_button]

    def unset_title_screen(self) -> None:
        for widget in self.widgets:
            widget.grid_forget()
        self.widgets = []

        if self.sound_available:
            winsound.PlaySound(None, winsound.SND_PURGE)

    def push_start_button(self) -> None:
        quiz_mode = self.quiz_mode.get()
        match quiz_mode:
            case self.TIME_LIMIT:
                self.set_ENDLESS_QUIZ_screen()  # temp
            case self.FIXED_QUIZ:
                self.set_ENDLESS_QUIZ_screen()  # temp
            case self.ENDLESS_QUIZ:
                self.set_ENDLESS_QUIZ_screen()
            case _:
                raise ValueError(f"{quiz_mode} is invalid quiz mode.")

    def set_ENDLESS_QUIZ_screen(self) -> None:
        self.unset_title_screen()
        self.text_label.pack(pady=20)
        self.user_input_entry.pack(pady=10)
        self.user_input_entry.focus_set()

    def resizable_mode(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.columnconfigure(2, weight=1)
        self.mainframe.columnconfigure(3, weight=1)
        self.mainframe.rowconfigure(1, weight=1)

    def new_text(self) -> None:
        self.quiz = self.quizzes.generate_quiz()
        self.question = self.quiz.question
        self.text_label.config(text=self.question, fg="black")

    def check_text(self, event) -> None:
        player_answer = self.user_input.get()
        if self.quiz.check_answer(player_answer):
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
