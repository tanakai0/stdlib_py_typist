import random
from datetime import date, timedelta
from typing import Optional, Tuple

from src.quiz import Quiz, Quizzes

# In this module, Quizzes classes are dynamically generated.
# Such dynamically quizzes are only allow to be written in this module.


class JulianGregorianDOWQuizzes(Quizzes):
    """
    Quiz of the day of the week in the Gregorian calendar.
    """

    def __init__(
        self,
        name="今日は何曜日？（ユリウス暦 + グレゴリオ暦）",
        description=(
            "西暦1年1月1日～西暦1582年10月4日と西暦1582年10月15日～西暦9999年12月31日から選ばれた日の曜日を当てよう！"
            + "ただし、西暦1582年10月4日以前はユリウス暦、"
            + "西暦1582年10月15日以降はグレゴリオ暦として答えてね．"
        ),
        is_proleptic_Gregorian_calendar: bool = False,
    ) -> None:
        """
        is_proleptic_Gregorian_calendar : bool, default False
            Whether to use proleptic Gregorian calendar.
        """
        super().__init__(name, description)
        self.start_date = date(1, 1, 1)
        self.end_date = date(9999, 12, 31)
        self.is_proleptic_Gregorian_calendar = is_proleptic_Gregorian_calendar
        self.dow2answer = {
            1: "月曜日\tげつようび\t月\tMonday",
            2: "火曜日\tかようび\t火\tTuesday",
            3: "水曜日\tすいようび\t水\tWednesday",
            4: "木曜日\tもくようび\t木\tThursday",
            5: "金曜日\tきんようび\t金\tFriday",
            6: "土曜日\tどようび\t土\tSaturday",
            7: "日曜日\tにちようび\t日\tSunday",
        }
        self.julian_end_date = date(1582, 10, 4)
        self.gregorian_start_date = date(1582, 10, 15)

    def generate_quiz(self):
        random_date = self.generate_random_date()
        dow = self.calculate_dow(random_date)
        question = random_date.strftime("%Y年%m月%d日")
        answer = self.dow2answer[dow]
        explanation = ""
        if self.check_leap_year(random_date):
            explanation = "うるう年であることに注意！"
        return Quiz(question, answer, explanation)

    def generate_random_date(self) -> date:
        """
        Generate a random date between the given start and end dates, avoiding the dates during the Julian to Gregorian transition.

        Parameters
        ----------
        start : date
            The starting date for the random date generation. Default is January 1, Year 1.
        end : date
            The ending date for the random date generation. Default is December 31, Year 9999.

        Returns
        -------
        random_date : date
            A random date between start and end, avoiding the Julian to Gregorian transition period.
        """
        is_valid = False
        while not is_valid:
            years = self.end_date.year - self.start_date.year + 1
            effective_end = self.start_date + timedelta(days=365 * years)
            random_time_delta = (effective_end - self.start_date) * random.random()
            random_date = self.start_date + random_time_delta

            if self.is_proleptic_Gregorian_calendar:
                if self.start_date <= random_date <= self.end_date:
                    is_valid = True
            else:
                if (self.start_date <= random_date <= self.end_date) and not (
                    self.julian_end_date < random_date < self.gregorian_start_date
                ):
                    is_valid = True

        return random_date

    def calculate_dow(self, d: date) -> Optional[int]:
        """
        Calculate the day of the week from the date.

        Parameter
        ---------
        d : date
            Target data.

        Returns
        -------
        _ : int or None
            ISO week date Day-of-Week (1 = Monday to 7 = Sunday).
        """
        if (not self.is_proleptic_Gregorian_calendar) and (
            self.julian_end_date < d < self.gregorian_start_date
        ):
            return None

        y, m, q = d.year, d.month, d.day
        if m < 3:
            m += 12
            y -= 1
        J, K = divmod(y, 100)
        h = q + 13 * (m + 1) // 5 + K + K // 4
        if self.is_proleptic_Gregorian_calendar:
            # proleptic Gregorian calendar
            h += J // 4 - 2 * J
        else:
            if d >= date(1582, 10, 15):
                # Gregorian calendar
                h += J // 4 - 2 * J
            else:
                # Julian calendar
                h += 5 - J
        dow = (h + 5) % 7 + 1

        return dow

    def check_leap_year(self, d: date) -> bool:
        """
        Check whether the date is a leap year.

        Parameter
        ---------
        d : date
            Target date.

        Returns
        -------
        _ : bool
            Whether the date is a leap year.

        Notes
        -----
        The introduction of the Julian calendar may have experienced some initial irregularities [Alexander Jones, 2000].
        However, for the purposes of this discussion, we assume that the Julian calendar was implemented correctly.
        Specifically, we assume that leap years were accurately inserted every four years.
        """

        def check_Gregorian_leap_year(year):
            if year % 4 != 0:
                return False
            elif year % 100 != 0:
                return True
            elif year % 400 != 0:
                return False
            else:
                return True

        def check_Julian_leap_year(year):
            if year % 4 == 0:
                return True
            else:
                return False

        year = d.year
        if self.is_proleptic_Gregorian_calendar:
            return check_Gregorian_leap_year(year)
        else:
            if year < self.julian_end_date.year:
                return check_Julian_leap_year(year)
            else:
                return check_Gregorian_leap_year(year)


class ProlepticGregorianDOWQuizzes(JulianGregorianDOWQuizzes):
    """
    Quiz of the day of the week in the proleptic Gregorian calendar.
    """

    def __init__(self) -> None:
        name = "今日は何曜日？（先発グレゴリオ暦）"
        description = "先発グレゴリオ暦で西暦1年1月1日～西暦9999年12月31日から選ばれた日の曜日を当てよう！"
        super().__init__(name, description, is_proleptic_Gregorian_calendar=True)


class MultiplicationNDigitsQuizzes(Quizzes):
    """
    Set of quiz generated dynamically.
    """

    def __init__(self, d: int = 2) -> None:
        """
        Parameters
        ----------
        d : int
            Maximum number of digits for the numbers in the quiz.
            d > 0.
        """
        self.d = d
        name = f"{self.d}桁×{self.d}桁"
        description = f"最大{self.d}桁の2つの自然数の掛け算をランダムで出題"
        super().__init__(name, description)

    def generate_quiz(self) -> Tuple[str, str]:
        """
        Generate a multiplication quiz with numbers up to d digits.

        Examples
        --------
        >>> generate_quiz(2)
        ("23 x 41 = ?", "943")
        """

        min_value = 2
        max_value = 10**self.d - 1

        num1 = random.randint(min_value, max_value)
        num2 = random.randint(min_value, max_value)

        question = f"{num1} × {num2} = ?"
        answer = str(num1 * num2)
        explanation = ""

        return Quiz(question, answer, explanation)


class MultiplicationThreeDigitsQuizzes(MultiplicationNDigitsQuizzes):
    def __init__(self) -> None:
        super().__init__(d=3)


# Template
# class DynamicQuizzes(Quizzes):
#     """
#     Set of quiz generated dynamically.
#     """

#     def __init__(self, name: str, description: str) -> None:
#         super().__init__(name, description)

#     def generate_quiz():
#         pass
