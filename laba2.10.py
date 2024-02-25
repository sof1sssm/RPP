# Считываем произвольную строку с клавиатуры
sequence = input("Введите произвольную строку: ")

# Преобразуем строку так, чтобы каждое слово начиналось с заглавной буквы
transformed_sequence = ""
count = 0
for char in sequence:
    if char != ' ' and count == 0:
        transformed_sequence += char.upper()
        count = 1
    elif char != ' ' and count == 1:
        transformed_sequence += char
    elif char == ' ':
        transformed_sequence += char
        count = 0

# Выводим полученную строку
print("Преобразованная строка:", transformed_sequence)

# Выводим количество преобразований
print("Количество преобразований:", transformed_sequence.count(' '))