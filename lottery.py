import random


class Lottery:
    def __init__(self):
        self.initial = 0
        self.final = 100
        self.count = 5

    def setting_initial(self, ini):

        if ini < 0:
            raise ValueError("O início não pode ter valor menor que zero")
        if self.final <= ini:
            raise ValueError("O início deve ser um valor menor que o final")

        if self.final - ini + 1 < self.count:
            raise ValueError("O intervalo ficará menor que a quantidade atual")

        self.initial = ini

    def setting_final(self, fi):

        if fi < 0:
            raise ValueError("O final não pode ter valor menor que zero")
        if fi <= self.initial:
            raise ValueError("O final deve ser um valor maior que o inicial")

        if fi - self.initial + 1 < self.count:
            raise ValueError("O intervalo ficará menor que a quantidade atual")

        self.final = fi

    def setting_count(self, co):
        if co <= 0:
            raise ValueError("A Quantidade não pode ter valor menor ou igual a zero")
        if self.final - self.initial + 1 < co:
            raise ValueError("A Quantidade não pode ser maior que o intervalo inserido")
        self.count = co

    def sorting_numbers(self):
        numbers = random.sample(range(self.initial, self.final + 1), self.count)

        return numbers

    def validating_numbers(self, numbers):

        if len(numbers) != self.count:
            raise ValueError(
                f"A aposta deve possuir exatamente {self.count} número(s)."
            )

        for number in numbers:
            if number < self.initial or number > self.final:
                raise ValueError(
                    f"O número {number} está fora do intervalo "
                    f"{self.initial} até {self.final}."
                )

    def checking_numbers(self, numbers, sorted_numbers):
        correct_numbers = []

        for number in numbers:
            if number in sorted_numbers:
                correct_numbers.append(number)

        return correct_numbers

    def get_params(self):
        return [self.initial, self.final, self.count]
