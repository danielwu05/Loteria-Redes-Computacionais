import lottery


loteria = lottery.Lottery()

print("Quer configurar o escopo e a quantidade de números a serem sorteados? (s/n)")
response = input().lower()

if response == "s":
    print("Digite o número inicial do escopo: ")
    ini = int(input())

    print("Digite o número final do escopo: ")
    fi = int(input())

    print("Digite a quantidade de números a serem sorteados: ")
    co = int(input())

    loteria.setting_config(ini, fi, co)


numbers = []

print("Digite os números que deseja apostar: ")

for i in range(loteria.count):
    num = int(input())
    numbers.append(num)


# Realiza o sorteio
sorted_numbers = loteria.sorting_numbers()

# Verifica quais números da aposta foram sorteados
correct_numbers = loteria.checking_numbers(numbers, sorted_numbers)


print("\nNúmeros apostados:")
print(numbers)

print("\nNúmeros sorteados:")
print(sorted_numbers)

print("\nNúmeros acertados:")
print(correct_numbers)