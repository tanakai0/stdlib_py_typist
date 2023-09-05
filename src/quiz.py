import random
import sqlite3
from pathlib import Path
from typing import List, Tuple, Union


class Quiz:
    """
    Notes
    -----
    Be careful that tab character in answer is treated as special meaning.
    Multiple answer is implemented as tab connected strings.
    For example, if answer = 'cat\tdog\t', cat, dog and empty string ('') are answers.
    """

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
        self.description = description

    def generate_quiz():
        pass


class StaticQuizzes(Quizzes):
    """
    Set of quiz prepared statistically from database.
    """

    def __init__(self, database_path: Union[str, Path]) -> None:
        name, description = self.load_overview(database_path)
        super().__init__(name, description)
        self.quizzes = self.load_quizzes(database_path)

    @staticmethod
    def load_overview(database_path: Union[str, Path]) -> Tuple[str, str]:
        with sqlite3.connect(database_path) as conn:
            c = conn.cursor()
            c.execute("SELECT name, description FROM overview")
            row = c.fetchone()
            if row is not None:
                name, description = row
            else:
                raise ValueError("No overview")
        return name, description

    @staticmethod
    def load_quizzes(database_path: Union[str, Path]) -> List[Quiz]:
        with sqlite3.connect(database_path) as conn:
            c = conn.cursor()
            c.execute("SELECT question, answer, explanation FROM quizzes")
            data = c.fetchall()
        quizzes = [Quiz(q, a, e) for (q, a, e) in data]
        return quizzes

    def generate_quiz(self) -> Quiz:
        return random.choice(self.quizzes)


class DynamicQuizzes(Quizzes):
    """
    Set of quiz generated dynamically.
    """

    def __init__(self, name: str, description: str) -> None:
        super().__init__(name, description)

    def generate_quiz():
        pass
