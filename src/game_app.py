import platform
import textwrap
import tkinter as tk
import winsound
import datetime
from tkinter import ttk

from src.quiz import StaticQuizzes
from src.quiz_database import DATABASE_FOLDER, QUIZ_LOG_FILE, QuizLogger


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
        self.is_saved = True
        self.logger = QuizLogger()

        if self.sound_available:
            self.correct_sound = "./assets/sound/pinpon2.wav"
            self.incorrect_sound = "./assets/sound/bubbu1.wav"
            self.title_music = "./assets/sound/scene3.wav"

        db_paths = [p for p in DATABASE_FOLDER.glob("*.db") if p != QUIZ_LOG_FILE]
        self.quizzes_list = [StaticQuizzes(p) for p in db_paths]
        self.overview2index = {(q.name, q.description): q for q in self.quizzes_list}

        self.root = root
        self.root.title("Typing Game")
        # self.root.geometry('800x400')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))

        # widgets in the title screen
        self.title_label = tk.Label(
            self.mainframe, text="Typing Game", font=("Helvetica", 36)
        )
        self.title_start_button = tk.Button(
            self.mainframe, text="ゲームスタート", command=self.setup_mode_selection_screen
        )
        self.show_quiz_logs_button = tk.Button(
            self.mainframe, text="履歴", command=self.setup_quiz_logs_screen
        )

        # widgets in the mode selection screen
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

        self.quiz_start_button = tk.Button(
            self.mainframe, text="クイズ開始", command=self.push_quiz_start_button
        )
        self.return_to_title_button = tk.Button(
            self.mainframe, text="戻る", command=self.setup_title_screen
        )
        self.seconds_limit = tk.StringVar()
        self.default_seconds_limit = 60 * 2
        self.min_seconds_limit = 1
        self.max_seconds_limit = 60 * 60
        self.seconds_limit.set(self.default_seconds_limit)
        self.seconds_limit_spinbox = tk.Spinbox(
            self.mainframe,
            from_=self.min_seconds_limit,
            to=self.max_seconds_limit,
            increment=30,
            textvariable=self.seconds_limit,
        )
        self.num_limit = tk.StringVar()
        self.default_num_limit = 10
        self.min_num_limit = 1
        self.max_num_limit = 10000
        self.num_limit.set(self.default_num_limit)
        self.num_limit_spinbox = tk.Spinbox(
            self.mainframe,
            from_=self.min_num_limit,
            to=self.max_num_limit,
            increment=1,
            textvariable=self.num_limit,
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
            text=f"時間制限（{self.min_seconds_limit}秒-{self.max_seconds_limit}秒）",
            variable=self.quiz_mode,
            value=self.TIME_LIMIT,
        )
        self.fixed_quiz_radio_button = ttk.Radiobutton(
            self.mainframe,
            text= f"固定問題数（{self.min_num_limit}問-{self.max_num_limit}問）",
            variable=self.quiz_mode,
            value=self.FIXED_QUIZ,
        )

        # widgets in the quiz screen
        self.text_label = tk.Label(self.mainframe, text="", font=("Helvetica", 24))
        self.player_input = tk.StringVar()
        self.player_input_entry = tk.Entry(
            self.mainframe, textvariable=self.player_input, font=("Helvetica", 18)
        )
        self.player_input_entry.bind("<Return>", self.check_text)

        # widgets in the endless quiz screen
        self.accuracy_rate_label = tk.Label(self.mainframe, text="")
        self.elapsed_minutes_label = tk.Label(self.mainframe, text="")
        self.show_result_button = tk.Button(
            self.mainframe, text="終了", command=self.setup_endless_quiz_results
        )

        # widgets in the quiz log screen
        _id = "履歴番号"
        date = "日付"
        player_result = "正誤"
        question = "問題文"
        answer = "正答"
        explanation = "説明"
        
        column = (_id, date, player_result, question, answer, explanation)
        # style = ttk.Style()
        # style.configure("Treeview", rowheight=40)
        self.quiz_logs = ttk.Treeview(self.mainframe, columns=column, height=5, selectmode="browse")
        self.quiz_logs.column("#0", width=0, stretch="no")
        self.quiz_logs.column(_id, anchor="w", width=100)
        self.quiz_logs.column(date, anchor="w", width=200)
        self.quiz_logs.column(player_result, anchor="w", width=50)
        self.quiz_logs.column(question, anchor="w", width=300)
        self.quiz_logs.column(answer, anchor="w", width=300)
        self.quiz_logs.column(explanation, anchor="w", width=300)
        self.quiz_logs.heading("#0", text="")
        self.quiz_logs.heading(_id, text=_id, anchor="center")
        self.quiz_logs.heading(date, text=date, anchor="center")
        self.quiz_logs.heading(player_result, text=player_result, anchor="center")
        self.quiz_logs.heading(question, text=question, anchor="center")
        self.quiz_logs.heading(answer, text=answer, anchor="center")
        self.quiz_logs.heading(explanation, text=explanation, anchor="center")
        for i, log in enumerate(self.logger.load_log()):
            player_result = ""
            if log[2] is None:
                player_result = "None"
            elif log[2]:
                player_result = "O"
            else:
                player_result = "X"
            values = (i, log[1], player_result, log[3], log[4], log[5])
            self.quiz_logs.insert(parent="", index="end", values=values)

        self.setup_title_screen()

    def setup_title_screen(self) -> None:
        self.unset_screen()
        self.mainframe.grid(row=0, column=0, sticky=(self.N, self.S, self.E, self.W))
        # self.resizable_mode()
        if self.sound_available:
            winsound.PlaySound(
                self.title_music,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
            )
        self.title_label.grid(column=0, row=0, columnspan=5, pady=20)
        self.title_start_button.grid(column=0, row=5, columnspan=4, pady=5)
        self.show_quiz_logs_button.grid(column=4, row=5, pady=5)
        self.widgets += [self.title_label, self.title_start_button, self.show_quiz_logs_button]

    def unset_screen(self) -> None:
        for widget in self.widgets:
            widget.grid_forget()
        self.widgets = []

        if self.sound_available:
            winsound.PlaySound(None, winsound.SND_PURGE)

    def push_quiz_start_button(self) -> None:
        self.new_quiz()
        quiz_mode = self.quiz_mode.get()
        # print(
        #     self.str2positive_int(
        #         self.seconds_limit.get(), self.default_seconds_limit, self.min_seconds_limit, self.max_seconds_limit
        #     )
        # )
        # print(
        #     self.str2positive_int(
        #         self.num_limit.get(), self.default_num_limit, self.min_num_limit, self.max_num_limit
        #     )
        # )
        match quiz_mode:
            case self.ENDLESS_QUIZ:
                self.setup_endless_quiz_screen()
            case self.TIME_LIMIT:
                self.setup_endless_quiz_screen()  # temp
            case self.FIXED_QUIZ:
                self.setup_endless_quiz_screen()  # temp
            case _:
                raise ValueError(f"{quiz_mode} is invalid quiz mode.")

    def setup_mode_selection_screen(self) -> None:
        self.unset_screen()
        self.quizzes_table.grid(column=0, row=0, columnspan=5)
        self.quiz_mode_label.grid(column=0, row=1, rowspan=3)
        self.endless_quiz_radio_button.grid(column=1, row=1, sticky=self.W)
        self.time_limit_radio_button.grid(column=1, row=2, sticky=self.W)
        self.fixed_quiz_radio_button.grid(column=1, row=3, sticky=self.W)
        self.seconds_limit_spinbox.grid(column=2, row=2, sticky=self.W)
        self.num_limit_spinbox.grid(column=2, row=3, sticky=self.W)
        self.quiz_start_button.grid(column=4, row=1, rowspan=3)
        self.return_to_title_button.grid(column=3, row=1, rowspan=3)
        self.widgets += [
            self.quizzes_table,
            self.quiz_mode_label,
            self.endless_quiz_radio_button,
            self.time_limit_radio_button,
            self.fixed_quiz_radio_button,
            self.seconds_limit_spinbox,
            self.num_limit_spinbox,
            self.return_to_title_button,
            self.quiz_start_button,
        ]

    def select_quizzes(self, event):
        selected_id = self.quizzes_table.selection()
        if not(selected_id):
            return
        _id = selected_id[0]
        overview = self.quizzes_table.item(_id, "values")
        self.quizzes = self.overview2index[overview]

    def setup_endless_quiz_screen(self) -> None:
        self.unset_screen()
        self.correct = 0
        self.answered_num = 0
        self.text_label.grid(column=0, row=0, rowspan=2)
        self.player_input_entry.grid(column=0, row=2)
        self.accuracy_rate_label.grid(column=1, row=0)
        self.elapsed_minutes_label.grid(column=1, row=1)
        self.show_result_button.grid(column=1, row=2)
        self.player_input_entry.focus_set()
        self.accuracy_rate_label.config(text=f"正答率: {self.correct} [問] {self.answered_num} [問]")
        self.elapsed_minutes_label.config(text=f"経過時間: 0 [分]")
        self.widgets += [
            self.text_label,
            self.player_input_entry,
            self.accuracy_rate_label,
            self.elapsed_minutes_label,
            self.show_result_button
        ]

    def setup_endless_quiz_results(self) -> None:
        self.unset_screen()

    def setup_quiz_logs_screen(self) -> None:
        self.unset_screen()
        self.quiz_logs.grid(column=0, row=0)
        self.return_to_title_button.grid(column=0, row=1)
        self.widgets += [
            self.quiz_logs,
            self.return_to_title_button
        ]

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
        self.is_saved = False

    def check_text(self, event) -> None:
        self.answered_num += 1
        player_answer = self.player_input.get()
        is_correct = self.quiz.check_answer(player_answer)
        if is_correct:
            self.correct += 1
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
        self.accuracy_rate_label.config(text=f"正答率: {self.correct} [問] / {self.answered_num} [問]")

        date = datetime.datetime.now().isoformat()
        self.logger.save_log(date, is_correct, self.quiz.question, self.quiz.answer, self.quiz.explanation)
        self.is_saved = True

        self.root.after(500, self.new_quiz)

    @staticmethod
    def str2positive_int(s: str, default: int, min_limit: int, max_limit: int) -> int:
        try:
            num = float(s)
            if isinstance(num, float):
                num = int(num)
            if num < min_limit:
                return min_limit 
            elif max_limit < num:
                return max_limit
            else:
                return num
        except ValueError:
            return default
        
    def on_closing(self):
        if not self.is_saved:
            date = datetime.datetime.now().isoformat()
            self.logger.save_log(date, None, self.quiz.question, self.quiz.answer, self.quiz.explanation)
        self.logger.close_log_connection()
        self.root.destroy()