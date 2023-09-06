from src.quiz import Quiz, Quizzes


class DOWQuizzes(Quizzes):
    """
    Quiz of calculation of the day of the week.
    """

    def __init__(self, is_proleptic_Gregorian_calendar: bool = False) -> None:
        """
        is_proleptic_Gregorian_calendar : bool, default False
            Whether to use proleptic Gregorian calendar.
        """
        name = "今日は何曜日？"
        description = (
            "西暦1年1月1日～西暦9999年12月31日から選ばれた日の曜日を当てよう！"
            + "ただし、西暦1582年10月4日以前はユリウス暦、"
            + "西暦1582年10月15日以降はグレゴリオ暦として答えてね．ちなみに、その間の日付は問題には出さないよ。"
        )
        super().__init__(name, description)

    def generate_quiz(self):
        pass


# Template
# class DynamicQuizzes(Quizzes):
#     """
#     Set of quiz generated dynamically.
#     """

#     def __init__(self, name: str, description: str) -> None:
#         super().__init__(name, description)

#     def generate_quiz():
#         pass
