import platform
import textwrap
import tkinter as tk
import winsound
from tkinter import ttk

from src.quiz import StaticQuizzes
from src.quiz_database import DATABASE_FOLDER


class TypingGameApp:
    N, W, E, S = tk.N, tk.W, tk.E, tk.S
    ENDLESS_QUIZ = "Endless Quiz"
    TIME_LIMIT = "Time Limit"
    FIXED_QUIZ = "Fixed Quiz"

    def __init__(self, root, database_path) -> None:
        self.database_path = database_path
        self.on_windows_os = platform.system() == "Windows"
        self.sound_available = self.on_windows_os
        self.widgets = []
        self.quizzes = None
        self.question = ""

        if self.sound_available:
            self.correct_sound = "./assets/sound/pinpon2.wav"
            self.incorrect_sound = "./assets/sound/bubbu1.wav"
            self.title_music = "./assets/sound/scene3.wav"

        self.root = root
        self.root.title("Typing Game")
        # self.root.geometry('800x400')
        self.mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))

        # widgets in the title screen
        db_paths = [p for p in DATABASE_FOLDER.glob("*.db")]
        self.quizzes_list = [StaticQuizzes(p) for p in db_paths]
        self.overview2index = {(q.name, q.description): q for q in self.quizzes_list}

        name = "名前"
        description = "説明"
        column = (name, description)
        # style = ttk.Style()
        # style.configure("Treeview", rowheight=40)
        self.quizzes_table = ttk.Treeview(self.mainframe, columns=column, height=5, selectmode="browse")
        self.quizzes_table.bind("<<TreeviewSelect>>", self.select_quizzes)
        self.quizzes_table.column("#0", width=0, stretch="no")
        self.quizzes_table.column(name, anchor="w", width=200)
        self.quizzes_table.column(description, anchor="w", width=300)
        self.quizzes_table.heading("#0", text="")
        self.quizzes_table.heading(name, text=name, anchor="center")
        self.quizzes_table.heading(description, text=description, anchor="center")
        for i, (n, d) in enumerate(self.overview2index.keys()):
            wrapped_n = "\n".join(textwrap.wrap(n, width=20))
            wrapped_d = "\n".join(textwrap.wrap(d, width=20))
            self.quizzes_table.insert(parent="", index="end", iid = i, values=(wrapped_n, wrapped_d))
        if db_paths:
            self.quizzes_table.selection_set(0)
            self.quizzes_table.focus(0)
            self.quizzes = self.quizzes_list[0]
        self.title_label = tk.Label(
            self.mainframe, text="Typing Game", font=("Helvetica", 36)
        )
        self.title_start_button = tk.Button(
            self.mainframe, text="ゲームスタート", command=self.set_mode_selection_screen
        )

        # widgets in the mode selection screen
        self.quiz_start_button = tk.Button(
            self.mainframe, text="クイズ開始", command=self.push_quiz_start_button
        )
        self.quiz_mode_label = tk.Label(
            self.mainframe, text="クイズ\nモード", font=("Helvetica", 12)
        )
        self.quiz_mode = tk.StringVar(None, self.ENDLESS_QUIZ)
        self.endless_quiz_radio_button = ttk.Radiobutton(
            self.mainframe,
            text="エンドレス",
            variable=self.quiz_mode,
            value=self.ENDLESS_QUIZ,
        )
        self.time_limit_radio_button = ttk.Radiobutton(
            self.mainframe,
            text="時間制限",
            variable=self.quiz_mode,
            value=self.TIME_LIMIT,
        )
        self.fixed_quiz_radio_button = ttk.Radiobutton(
            self.mainframe,
            text="固定問題数",
            variable=self.quiz_mode,
            value=self.FIXED_QUIZ,
        )

        self.max_seconds = tk.StringVar()
        self.max_seconds_default = 60 * 2
        self.max_seconds_limit = 60 * 60
        self.max_seconds.set(self.max_seconds_default)
        self.max_seconds_spinbox = tk.Spinbox(
            self.mainframe,
            from_=1,
            to=self.max_seconds_limit,
            increment=30,
            textvariable=self.max_seconds,
        )
        self.max_num = tk.StringVar()
        self.max_num_default = 10
        self.max_num_limit = 10000
        self.max_num.set(self.max_num_default)
        self.max_num_spinbox = tk.Spinbox(
            self.mainframe,
            from_=1,
            to=self.max_num_limit,
            increment=1,
            textvariable=self.max_num,
        )
        self.title_back_button = tk.Button(
            self.mainframe, text="戻る", command=self.set_title_screen
        )

        # widgets in the quiz screen
        self.text_label = tk.Label(self.mainframe, text="", font=("Helvetica", 24))
        self.player_input = tk.StringVar()
        self.player_input_entry = tk.Entry(
            self.mainframe, textvariable=self.player_input, font=("Helvetica", 18)
        )
        self.player_input_entry.bind("<Return>", self.check_text)

        self.set_title_screen()

    def set_title_screen(self) -> None:
        self.unset_screen()
        self.mainframe.grid(row=0, column=0, sticky=(self.N, self.S, self.E, self.W))
        # self.resizable_mode()
        if self.sound_available:
            winsound.PlaySound(
                self.title_music,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
            )
        self.title_label.grid(column=0, row=0, columnspan=4, pady=20)
        self.title_start_button.grid(column=0, row=5, columnspan=4, pady=5)
        self.widgets += [self.title_label, self.title_start_button]

    def unset_screen(self) -> None:
        for widget in self.widgets:
            widget.grid_forget()
        self.widgets = []

        if self.sound_available:
            winsound.PlaySound(None, winsound.SND_PURGE)

    def push_quiz_start_button(self) -> None:
        self.new_quiz()
        quiz_mode = self.quiz_mode.get()
        print(self.max_seconds.get())
        print(
            self.str2positive_int(
                self.max_seconds.get(), self.max_seconds_default, self.max_seconds_limit
            )
        )
        print(self.max_num.get())
        print(
            self.str2positive_int(
                self.max_num.get(), self.max_num_default, self.max_num_limit
            )
        )
        match quiz_mode:
            case self.ENDLESS_QUIZ:
                self.set_endless_quiz_screen()
            case self.TIME_LIMIT:
                self.set_endless_quiz_screen()  # temp
            case self.FIXED_QUIZ:
                self.set_endless_quiz_screen()  # temp
            case _:
                raise ValueError(f"{quiz_mode} is invalid quiz mode.")

    def set_mode_selection_screen(self) -> None:
        self.unset_screen()
        self.quizzes_table.grid(column=0, row=0, columnspan=5)
        self.quiz_mode_label.grid(column=0, row=1, rowspan=3)
        self.endless_quiz_radio_button.grid(column=1, row=1, sticky=self.W)
        self.time_limit_radio_button.grid(column=1, row=2, sticky=self.W)
        self.fixed_quiz_radio_button.grid(column=1, row=3, sticky=self.W)
        self.max_seconds_spinbox.grid(column=2, row=2, sticky=self.W)
        self.max_num_spinbox.grid(column=2, row=3, sticky=self.W)
        self.quiz_start_button.grid(column=4, row=1, rowspan=3)
        self.title_back_button.grid(column=3, row=1, rowspan=3)
        self.widgets += [
            self.quizzes_table,
            self.quiz_mode_label,
            self.endless_quiz_radio_button,
            self.time_limit_radio_button,
            self.fixed_quiz_radio_button,
            self.max_seconds_spinbox,
            self.max_num_spinbox,
            self.title_back_button,
            self.quiz_start_button,
        ]

    def select_quizzes(self, event):
        selected_id = self.quizzes_table.selection()
        if not(selected_id):
            return
        _id = selected_id[0]
        overview = self.quizzes_table.item(_id, "values")
        self.quizzes = self.overview2index[overview]

    def set_endless_quiz_screen(self) -> None:
        self.unset_screen()
        self.text_label.pack(pady=20)
        self.player_input_entry.pack(pady=10)
        self.player_input_entry.focus_set()

    def resizable_mode(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.columnconfigure(2, weight=1)
        self.mainframe.columnconfigure(3, weight=1)
        self.mainframe.rowconfigure(1, weight=1)

    def new_quiz(self) -> None:
        self.quiz = self.quizzes.generate_quiz()
        self.question = self.quiz.question
        self.text_label.config(text=self.question, fg="black")

    def check_text(self, event) -> None:
        player_answer = self.player_input.get()
        if self.quiz.check_answer(player_answer):
            self.text_label.config(text="正解！", fg="green")
            if self.sound_available:
                winsound.PlaySound(
                    self.correct_sound, winsound.SND_FILENAME | winsound.SND_ASYNC
                )
        else:
            self.text_label.config(text="不正解！", fg="red")
            if self.sound_available:
                winsound.PlaySound(
                    self.incorrect_sound, winsound.SND_FILENAME | winsound.SND_ASYNC
                )
        self.player_input.set("")
        self.root.after(500, self.new_quiz)

    @staticmethod
    def str2positive_int(s: str, default: int, max_limit: int) -> int:
        try:
            num = float(s)
            if "." in s:
                num = int(num)
            if num > 0 and int(num) == num:
                if num <= max_limit:
                    return int(num)
                else:
                    return max_limit
            else:
                return default
        except ValueError:
            return default
