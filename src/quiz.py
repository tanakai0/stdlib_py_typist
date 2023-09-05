import random
import sqlite3
from pathlib import Path
from typing import List, Tuple, Union


class Quiz:
    def __init__(self, question: str, answer: str, explanation: str) -> None:
        self.question = question
        self.answer = answer
        self.explanation = explanation
        self.correct_answers = set(self.answer.split("\t"))

    def check_answer(self, player_answer: str):
        return player_answer in self.correct_answers


class Quizzes:
    """
    This holds overviwe information of set of quiz.
    """

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = self.description

    def quiz_generator():
        pass


class DynamicQuizzes(Quizzes):
    """
    Set of quiz generated dynamically.
    """

    def __init__(self, name: str, description: str) -> None:
        super().__init__(name, description)

    def quiz_generator():
        pass


class StaticQuizzes(Quizzes):
    """
    Set of quiz prepared statistically from database.
    """

    def __init__(self, database_path: Union[str, Path]) -> None:
        name, description = self.load_overview(database_path)
        super().__init__(name, description)
        self.quizzes = self.load_quizzes()

    @staticmethod
    def load_overview(database_path: Union[str, Path]) -> Tuple[str, str]:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute("SELECT name, description FROM overview")
        row = c.fetchone()
        if row is not None:
            name, description = row
        else:
            raise ValueError("No overview")
        conn.close()
        return name, description

    @staticmethod
    def load_quizzes(database_path: Union[str, Path]) -> List[Quiz]:
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute("SELECT question, answer, explanation FROM quizzes")
        data = c.fetchall()
        conn.close()
        return data

    def quiz_generator(self) -> Quiz:
        return random.choice(self.quizzes)
