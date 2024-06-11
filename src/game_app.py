import datetime
import inspect
import platform
import textwrap
import tkinter as tk
import winsound
from functools import partial
from tkinter import ttk
from typing import List

from src import constants, dynamic_quizzes
from src.quiz import Quiz, StaticQuizzes
from src.quiz_database import DATABASE_FOLDER, QUIZ_LOG_FILE, QuizLogger
from src.timer import CountDownTimer, Timer
from src.utils import throttle


class TypingGameApp:
    ENDLESS_QUIZ = "Endless Quiz"
    TIME_LIMIT = "Time Limit"
    FIXED_QUIZ = "Fixed Quiz"

    def __init__(self, root) -> None:
        self.on_windows_os = platform.system() == "Windows"
        self.sound_available = self.on_windows_os
        self.widgets = []
        self.quizzes = None
        self.question = ""
        self.is_saved = True
        self.logger = QuizLogger()

        if self.sound_available:
            self.correct_sound = constants.CORRECT_SOUND_PATH
            self.incorrect_sound = constants.INCORRECT_SOUND_PATH
            self.title_music = constants.TITLE_MUSIC_PATH

        db_paths = [p for p in DATABASE_FOLDER.glob("*.db") if p != QUIZ_LOG_FILE]
        self.quizzes_list = [StaticQuizzes(p) for p in db_paths]
        # add instances of class defined in the ./src/dynamic_quizzes.py
        self.quizzes_list += [
            cls()
            for name, cls in inspect.getmembers(dynamic_quizzes, inspect.isclass)
            if cls.__module__ == dynamic_quizzes.__name__
        ]
        self.quizzes_list.sort(key=lambda x: x.name)
        self.overview2index = {(q.name, q.description): q for q in self.quizzes_list}

        self.root = root
        self.root.title("Typing Game")
        # self.root.geometry('800x400')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))

        # widgets in the title screen
        # self.title_background_image = tk.PhotoImage(master = self.mainframe, file='./assets/image/ichimatsu_lightblue-300x300.png')
        # self.title_background = tk.Label(self.mainframe, image=self.title_background_image, width=300, height = 200)
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
        style = ttk.Style()
        style.configure("Treeview", rowheight=40)
        self.quizzes_table = ttk.Treeview(
            self.mainframe, columns=column, height=5, selectmode="browse"
        )
        self.quizzes_table.bind("<<TreeviewSelect>>", self.select_quizzes)
        self.quizzes_table.column("#0", width=0, stretch="no")
        self.quizzes_table.column(name, anchor="w", width=200)
        self.quizzes_table.column(description, anchor="w", width=300)
        self.quizzes_table.heading("#0", text="")
        self.quizzes_table.heading(name, text=name, anchor="center")
        self.quizzes_table.heading(description, text=description, anchor="center")
        for i, (n, d) in enumerate(self.overview2index.keys()):
            wrapped_n = "\n".join(textwrap.wrap(n, width=20))
            wrapped_d = "\n".join(textwrap.wrap(d, width=30))
            self.quizzes_table.insert(
                parent="", index="end", iid=i, values=(wrapped_n, wrapped_d)
            )
        if db_paths:
            self.quizzes_table.selection_set(0)
            self.quizzes_table.focus(0)
            self.quizzes = self.quizzes_list[0]

        self.quiz_start_button = tk.Button(
            self.mainframe, text="クイズ開始", command=self.setup_quiz_screen
        )
        self.return_to_title_button = tk.Button(
            self.mainframe, text="タイトルに戻る", command=self.setup_title_screen
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
            text=f"固定問題数（{self.min_num_limit}問-{self.max_num_limit}問）",
            variable=self.quiz_mode,
            value=self.FIXED_QUIZ,
        )

        # widgets in the quiz screen
        self.text_label = tk.Label(
            self.mainframe, text="", font=("Helvetica", 24), justify=tk.LEFT
        )
        self.player_answer = tk.StringVar()
        self.player_answer_entry = tk.Entry(
            self.mainframe, textvariable=self.player_answer, font=("Helvetica", 18)
        )
        self.player_answer_entry.bind("<Return>", self.setup_feedback_screen)

        # for endless quiz mode
        self.quiz_num_text = tk.Label(
            self.mainframe, text="", anchor=tk.W, justify=tk.LEFT
        )
        self.quiz_time_text = tk.Label(
            self.mainframe, text="", anchor=tk.W, justify=tk.LEFT
        )
        self.show_result_button = tk.Button(
            self.mainframe, text="終了", command=self.setup_results_screen
        )
        # self.quit_button = tk.Button(
        #     self.mainframe, text="リタイア", command=self.setup_feedback_screen
        # )
        self.quit_button = tk.Button(self.mainframe, text="リタイア")
        self.quit_button.bind(
            "<Button-1>", partial(self.setup_feedback_screen, no_answer=True)
        )

        # widgets in the feedback screen

        # for endless quiz mode
        self.question_title_label = tk.Label(self.mainframe, text="問題：")
        self.answer_title_label = tk.Label(self.mainframe, text="正答：")
        self.explanation_title_label = tk.Label(self.mainframe, text="解説：")
        self.question_label = tk.Label(
            self.mainframe, text="", anchor=tk.W, justify=tk.LEFT
        )
        self.answer_label = tk.Label(
            self.mainframe, text="", anchor=tk.W, justify=tk.LEFT
        )
        self.explanation_label = tk.Label(
            self.mainframe, text="", anchor=tk.W, justify=tk.LEFT
        )
        self.next_quiz_button = tk.Button(
            self.mainframe, text="次へ (Enter)", command=self.update_quiz_screen
        )
        self.next_quiz_button.bind("<Return>", self.update_quiz_screen)

        # widgets in the results screen
        self.retry_button = tk.Button(
            self.mainframe, text="再挑戦", command=self.setup_quiz_screen
        )
        self.return_to_mode_selection_button = tk.Button(
            self.mainframe, text="モード選択に戻る", command=self.setup_mode_selection_screen
        )

        # widgets in the quiz logs screen

        # initial screen
        self.setup_title_screen()

    def unset_screen(self) -> None:
        for widget in self.widgets:
            widget.grid_forget()
        self.widgets = []

        if self.sound_available:
            winsound.PlaySound(None, winsound.SND_PURGE)

    def resizable_mode(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.columnconfigure(2, weight=1)
        self.mainframe.columnconfigure(3, weight=1)
        self.mainframe.rowconfigure(1, weight=1)

    def setup_title_screen(self) -> None:
        self.unset_screen()
        self.mainframe.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        # self.title_background.grid(row=0, column = 0, rowspan=2, columnspan=2)
        # self.resizable_mode()
        if self.sound_available:
            winsound.PlaySound(
                self.title_music,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
            )
        self.title_label.grid(column=0, row=0, columnspan=2, pady=20)
        self.title_start_button.grid(column=0, row=1, pady=5)
        self.show_quiz_logs_button.grid(column=1, row=1, pady=5)

        self.widgets += [
            self.title_label,
            self.title_start_button,
            self.show_quiz_logs_button,
        ]

    def setup_mode_selection_screen(self) -> None:
        self.unset_screen()
        self.quizzes_table.grid(column=0, row=0, columnspan=5)
        self.quiz_mode_label.grid(column=0, row=1, rowspan=3)
        self.endless_quiz_radio_button.grid(column=1, row=1, sticky=tk.W)
        self.time_limit_radio_button.grid(column=1, row=2, sticky=tk.W)
        self.fixed_quiz_radio_button.grid(column=1, row=3, sticky=tk.W)
        self.seconds_limit_spinbox.grid(column=2, row=2, sticky=tk.W)
        self.num_limit_spinbox.grid(column=2, row=3, sticky=tk.W)
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

    def select_quizzes(self, event) -> List[Quiz]:
        selected_id = self.quizzes_table.selection()
        if not (selected_id):
            return
        _id = int(selected_id[0])
        self.quizzes = self.quizzes_list[_id]

    def setup_quiz_screen(self) -> None:
        seconds_limit = self.str2positive_int(
            self.seconds_limit.get(),
            self.default_seconds_limit,
            self.min_seconds_limit,
            self.max_seconds_limit,
        )
        num_limit = self.str2positive_int(
            self.num_limit.get(),
            self.default_num_limit,
            self.min_num_limit,
            self.max_num_limit,
        )
        self.seconds_limit.set(seconds_limit)
        self.num_limit.set(num_limit)
        self.correct = 0
        self.displayed_quiz_count = 0
        self.unset_screen()
        self.player_answer.set("")
        quiz_mode = self.quiz_mode.get()
        self.new_quiz()

        self.text_label.grid(column=0, row=0, rowspan=2, columnspan=2)
        self.player_answer_entry.grid(column=0, row=2, columnspan=2)
        self.player_answer_entry.focus_set()
        self.quiz_num_text.grid(column=2, row=0)
        self.quiz_time_text.grid(column=2, row=1)
        match quiz_mode:
            case self.ENDLESS_QUIZ:
                self.timer = Timer()
                quiz_num_text = "正答率： 0 問 / 0 問"
                quiz_time_text = "経過時間: 0 秒"
                self.show_result_button.grid(column=2, row=2)
                self.widgets += [self.show_result_button]
            case self.TIME_LIMIT:
                self.timer = CountDownTimer(int(self.seconds_limit.get()))
                self.quiz_completete = False
                quiz_num_text = "正答率： 0 問 / 0 問"
                quiz_time_text = f"残り時間: {self.seconds_limit} 秒"
                self.quit_button.grid(column=2, row=2)
                self.widgets += [self.quit_button]
            case self.FIXED_QUIZ:
                self.timer = Timer()
                self.quiz_completete = False
                quiz_num_text = f"控え問題数：{int(self.num_limit.get()) - self.displayed_quiz_count} 問\n 正答率： 0 問 / 0 問"
                quiz_time_text = "経過時間: 0 秒"
                self.quit_button.grid(column=2, row=2)
                self.widgets += [self.quit_button]
            case _:
                raise ValueError(f"{quiz_mode} is invalid quiz mode.")
        self.quiz_num_text.config(text=quiz_num_text)
        self.quiz_time_text.config(text=quiz_time_text)
        self.widgets += [
            self.text_label,
            self.player_answer_entry,
            self.quiz_num_text,
            self.quiz_time_text,
        ]
        self.timer.start()
        match quiz_mode:
            case self.ENDLESS_QUIZ | self.FIXED_QUIZ:
                self.update_timer()
            case self.TIME_LIMIT:
                self.update_count_down_timer()
            case _:
                raise ValueError(f"{quiz_mode} is invalid quiz mode.")

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

    def update_timer(self):
        if self.timer.is_stopped():
            return
        else:
            quiz_time_text = f"経過時間: {int(self.timer.get_elapsed_time())} 秒"
            self.quiz_time_text.config(text=quiz_time_text)
            self.root.after(1000, self.update_timer)

    def update_count_down_timer(self):
        if self.timer.is_stopped():
            return
        else:
            if self.timer.is_time_over():
                self.quiz_completete = True
                self.mainframe.focus_set()
                self.player_answer_entry.grid_forget()
                quiz_time_text = "タイムアップ！"
                self.quiz_time_text.config(text=quiz_time_text)
                self.setup_feedback_screen(no_answer=True)
            else:
                quiz_time_text = f"経過時間: {int(self.timer.get_remaining_time())} 秒"
                self.quiz_time_text.config(text=quiz_time_text)
            self.root.after(1000, self.update_count_down_timer)

    @throttle(seconds=0.5)
    def setup_feedback_screen(self, event=None, no_answer=False) -> None:
        quiz_mode = self.quiz_mode.get()
        player_answer = self.player_answer.get()
        is_correct = self.quiz.check_answer(player_answer)

        # check the answer
        if no_answer:
            self.text_label.config(text="無回答", fg="black")
        elif is_correct:
            self.correct += 1
            self.text_label.config(text="正解！", fg="green")
            if self.sound_available:
                winsound.PlaySound(
                    self.correct_sound,
                    winsound.SND_FILENAME | winsound.SND_ASYNC,
                )
        else:
            self.text_label.config(text="不正解！", fg="red")
            if self.sound_available:
                winsound.PlaySound(
                    self.incorrect_sound,
                    winsound.SND_FILENAME | winsound.SND_ASYNC,
                )

        # save log
        date = datetime.datetime.now().isoformat()
        if no_answer:
            saved_answer = None
        else:
            saved_answer = is_correct
        self.logger.save_log(
            date,
            saved_answer,
            self.quiz.question,
            self.quiz.answer,
            self.quiz.explanation,
        )
        self.is_saved = True

        if no_answer:
            self.root.after(700, self.setup_results_screen)
            return

        match quiz_mode:
            case self.ENDLESS_QUIZ:
                quiz_num_text = f"正答率： {self.correct} 問 / {self.displayed_quiz_count} 問"
                self.quiz_num_text.config(text=quiz_num_text)
                self.question_title_label.grid(column=0, row=3, pady=8)
                self.answer_title_label.grid(column=0, row=4, pady=8)
                self.explanation_title_label.grid(column=0, row=5)
                self.question_label.grid(column=1, row=3, sticky=tk.W, pady=8)
                self.answer_label.grid(column=1, row=4, sticky=tk.W, pady=8)
                self.explanation_label.grid(column=1, row=5, sticky=tk.W)
                self.next_quiz_button.grid(column=1, row=6)
                self.question_label.config(text=self.question)
                self.answer_label.config(text=self.quiz.answer)
                self.explanation_label.config(text=self.quiz.explanation)
                self.next_quiz_button.focus_set()
                self.widgets += [
                    self.question_title_label,
                    self.answer_title_label,
                    self.explanation_title_label,
                    self.question_label,
                    self.answer_label,
                    self.explanation_label,
                    self.next_quiz_button,
                ]
            case self.TIME_LIMIT:
                if self.quiz_completete:
                    self.root.after(700, self.setup_results_screen)
                else:
                    self.root.after(500, self.update_quiz_screen)
            case self.FIXED_QUIZ:
                if self.displayed_quiz_count >= int(self.num_limit.get()):
                    self.quiz_completete = True
                    self.root.after(700, self.setup_results_screen)
                else:
                    self.root.after(500, self.update_quiz_screen)
            case _:
                raise ValueError(f"{quiz_mode} is invalid quiz mode.")

    def update_quiz_screen(self, event=None) -> None:
        self.player_answer.set("")
        self.player_answer_entry.focus_set()
        self.new_quiz()
        quiz_mode = self.quiz_mode.get()
        match quiz_mode:
            case self.ENDLESS_QUIZ:
                # delete last 7 widgets
                for w in self.widgets[-7:]:
                    w.grid_forget()
                self.widgets = self.widgets[:-7]
            case self.TIME_LIMIT:
                quiz_num_text = (
                    f"正答率： {self.correct} 問 / {self.displayed_quiz_count - 1} 問"
                )
                self.quiz_num_text.config(text=quiz_num_text)
            case self.FIXED_QUIZ:
                quiz_num_text = (
                    f"控え問題数： {int(self.num_limit.get()) - self.displayed_quiz_count} 問\n"
                    + f"正答率： {self.correct} 問 / {self.displayed_quiz_count - 1} 問"
                )
                self.quiz_num_text.config(text=quiz_num_text)
            case _:
                raise ValueError(f"{quiz_mode} is invalid quiz mode.")

    def new_quiz(self) -> None:
        self.is_saved = False
        self.quiz = self.quizzes.generate_quiz()
        self.question = self.quiz.question
        self.text_label.config(text=self.question, fg="black")
        self.displayed_quiz_count += 1

    def setup_results_screen(self) -> None:
        self.mainframe.focus_set()
        self.player_answer_entry.grid_forget()
        if not self.is_saved:
            date = datetime.datetime.now().isoformat()
            self.logger.save_log(
                date, None, self.quiz.question, self.quiz.answer, self.quiz.explanation
            )
        self.is_saved = True
        self.timer.stop()

        self.unset_screen()
        quiz_mode = self.quiz_mode.get()
        result_logs = self.generate_quiz_logs_table(self.displayed_quiz_count)

        self.quiz_num_text.grid(row=0, column=0, columnspan=3, sticky=tk.W)
        self.quiz_time_text.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=10)
        result_logs.grid(row=2, column=0, columnspan=3)
        self.retry_button.grid(row=3, column=0)
        self.return_to_mode_selection_button.grid(row=3, column=1)
        self.return_to_title_button.grid(row=3, column=2)
        quiz_num_text = f"正答率： {self.correct} 問 / {self.displayed_quiz_count} 問"

        minutes, seconds = divmod(self.timer.total_seconds, 60)
        match quiz_mode:
            case self.ENDLESS_QUIZ:
                quiz_time_text = f"経過時間： {int(minutes)} 分 {seconds:.2f} 秒"
            case self.TIME_LIMIT:
                quiz_time_text = f"制限時間： {int(self.seconds_limit.get())} 秒"
                if not self.quiz_completete:
                    quiz_time_text += f" （残り{self.timer.remaining_time_at_stop}秒でリタイア）"
                score = self.correct / int(self.seconds_limit.get())
                quiz_num_text += f"\n1秒あたりの正解数（正解数 / 合計時間）： {score:.2f} ［問 / 秒］"
            case self.FIXED_QUIZ:
                quiz_time_text = f"経過時間： {int(minutes)} 分 {seconds:.2f} 秒"
                score = 0
                if self.correct == 0:
                    score = "Null"
                else:
                    score = f"{self.timer.total_seconds / self.correct :.2f}"
                quiz_num_text += f"\n正答にかかる平均時間（合計時間 / 正解数）： {score} ［秒 / 問］"
                if not self.quiz_completete:
                    quiz_num_text += f" （残り {int(self.num_limit.get()) - self.displayed_quiz_count + 1} 問でリタイア）"
            case _:
                raise ValueError(f"{quiz_mode} is invalid quiz mode.")

        self.quiz_num_text.config(text=quiz_num_text)
        self.quiz_time_text.config(text=quiz_time_text)
        self.widgets += [
            self.quiz_num_text,
            self.quiz_time_text,
            result_logs,
            self.retry_button,
            self.return_to_mode_selection_button,
            self.return_to_title_button,
        ]

    def setup_quiz_logs_screen(self) -> None:
        def select_log(event=None) -> None:
            selected_id = quiz_logs.selection()
            if not (selected_id):
                return
            _id = int(selected_id[0])
            log = quiz_logs.item(_id, "values")
            self.log_quiz = Quiz(log[3], log[4], log[5])
            if self.detail_toggle.get() == self.detail_toggle_ON_text:
                self.log_question_label.config(text=self.log_quiz.question)
                self.log_answer_label.config(text=self.log_quiz.answer)
                self.log_explanation_label.config(text=self.log_quiz.explanation)

        def toggle_details(event=None) -> None:
            if self.detail_toggle.get() == self.detail_toggle_ON_text:
                self.detail_toggle.set(self.detail_toggle_OFF_text)
                for w in self.widgets[-6:]:
                    w.grid_forget()
                self.widgets = self.widgets[:-6]
            else:
                self.detail_toggle.set(self.detail_toggle_ON_text)
                self.question_title_label.grid(column=0, row=2, pady=8)
                self.answer_title_label.grid(column=0, row=3, pady=8)
                self.explanation_title_label.grid(column=0, row=4)
                self.log_question_label.grid(column=1, row=2, sticky=tk.W, pady=8)
                self.log_answer_label.grid(column=1, row=3, sticky=tk.W, pady=8)
                self.log_explanation_label.grid(column=1, row=4, sticky=tk.W)
                if self.log_quiz is not None:
                    self.log_question_label.config(text=self.log_quiz.question)
                    self.log_answer_label.config(text=self.log_quiz.answer)
                    self.log_explanation_label.config(text=self.log_quiz.explanation)
                self.widgets += [
                    self.question_title_label,
                    self.answer_title_label,
                    self.explanation_title_label,
                    self.log_question_label,
                    self.log_answer_label,
                    self.log_explanation_label,
                ]

        self.unset_screen()

        self.log_question_label = tk.Label(
            self.mainframe, text="", anchor=tk.W, justify=tk.LEFT
        )
        self.log_answer_label = tk.Label(
            self.mainframe, text="", anchor=tk.W, justify=tk.LEFT
        )
        self.log_explanation_label = tk.Label(
            self.mainframe, text="", anchor=tk.W, justify=tk.LEFT
        )
        self.detail_toggle_ON_text = "詳細ON"
        self.detail_toggle_OFF_text = "詳細OFF"
        self.detail_toggle = tk.StringVar()
        self.detail_toggle_button = tk.Button(
            self.mainframe, textvariable=self.detail_toggle, command=toggle_details
        )

        self.detail_toggle.set(self.detail_toggle_OFF_text)
        quiz_logs = self.generate_quiz_logs_table()
        quiz_logs.bind("<<TreeviewSelect>>", select_log)

        scrollbar = ttk.Scrollbar(
            self.mainframe, orient="vertical", command=quiz_logs.yview
        )
        quiz_logs.configure(yscrollcommand=scrollbar.set)

        self.log_quiz = None
        if len(quiz_logs.get_children()):
            quiz_logs.selection_set(0)
            quiz_logs.focus(0)
            log = quiz_logs.item(0, "values")
            self.log_quiz = Quiz(log[3], log[4], log[5])

        quiz_logs.grid(row=0, column=0, rowspan=2, columnspan=2)
        scrollbar.grid(row=0, column=2, rowspan=2, sticky=(tk.N, tk.S))
        self.detail_toggle_button.grid(row=0, column=3)
        self.return_to_title_button.grid(row=1, column=3)
        self.widgets += [
            quiz_logs,
            scrollbar,
            self.return_to_title_button,
            self.detail_toggle_button,
        ]

    def generate_quiz_logs_table(self, num_limit=None) -> None:
        _id = "履歴番号"
        date = "回答日時"
        player_result = "正誤"
        question = "問題文"
        answer = "正答"
        explanation = "説明"

        column = (_id, date, player_result, question, answer, explanation)
        style = ttk.Style()
        style.configure("Treeview", rowheight=40)
        quiz_logs_table = ttk.Treeview(
            self.mainframe, columns=column, height=5, selectmode="browse"
        )
        quiz_logs_table.column("#0", width=0, stretch="no")
        quiz_logs_table.column(_id, anchor="w", width=60)
        quiz_logs_table.column(date, anchor="w", width=170)
        quiz_logs_table.column(player_result, anchor="w", width=40)
        quiz_logs_table.column(question, anchor="w", width=300)
        quiz_logs_table.column(answer, anchor="w", width=300)
        quiz_logs_table.column(explanation, anchor="w", width=300)
        quiz_logs_table.heading("#0", text="")
        quiz_logs_table.heading(_id, text=_id, anchor="center")
        quiz_logs_table.heading(date, text=date, anchor="center")
        quiz_logs_table.heading(player_result, text=player_result, anchor="center")
        quiz_logs_table.heading(question, text=question, anchor="center")
        quiz_logs_table.heading(answer, text=answer, anchor="center")
        quiz_logs_table.heading(explanation, text=explanation, anchor="center")
        logs = self.logger.load_log()
        if num_limit is not None:
            logs = logs[:num_limit]
        for i, log in enumerate(logs):
            player_result = ""
            if log[2] is None:
                player_result = "None"
            elif log[2]:
                player_result = "O"
            else:
                player_result = "X"
            values = (i, log[1], player_result, log[3], log[4], log[5])
            quiz_logs_table.insert(parent="", iid=i, index="end", values=values)
        return quiz_logs_table

    def on_closing(self):
        if not self.is_saved:
            date = datetime.datetime.now().isoformat()
            self.logger.save_log(
                date, None, self.quiz.question, self.quiz.answer, self.quiz.explanation
            )
        self.logger.close_log_connection()
        self.root.destroy()
