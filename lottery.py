import random


class Lottery:

    def __init__(self):
        self.initial = 0
        self.final = 100
        self.count = 5

    def setting_config(self, ini, fi, co):
        self.initial = ini
        self.final = fi
        self.count = co

    def sorting_numbers(self):
        numbers = random.sample(
            range(self.initial, self.final + 1),
            self.count
        )

        return numbers

    def checking_numbers(self, numbers, sorted_numbers):
        correct_numbers = []

        for number in numbers:
            if number in sorted_numbers:
                correct_numbers.append(number)

        return correct_numbers