import random


class Lottery:

    def __init__(self):
        self.initial = 0
        self.final = 100
        self.count = 5

    def setting_initial(self, ini):
        self.initial = ini

    def setting_final(self,fi):
        self.final = fi    

    def setting_count(self,co):
        self.count = co

    def sorting_numbers(self):
        numbers = random.sample(
            range(self.initial, self.final + 1),
            self.count
        )

        return numbers
    
    def validating_numbers(self, numbers):

        # Verifica quantidade
        if len(numbers) != self.count:
            raise ValueError(
                f"A aposta deve possuir exatamente {self.count} número(s)."
            )

        # Verifica se cada número está dentro do intervalo
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