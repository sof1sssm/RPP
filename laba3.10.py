import sys

# Считывание одномерного массива из параметров командной строки
import sys

# Считывание одномерного массива из параметров командной строки
array = list(map(int, sys.argv[1:]))

# Вывод повторяющихся элементов в консоль
repeated_elements = set([x for x in array if array.count(x) > 1])
if repeated_elements:
    print("Повторяющиеся элементы:", repeated_elements)
else:
    print("Нет повторяющихся элементов")

# Присвоение нулевых значений элементам массива, которые меньше 10, и значений 1 элементам, которые больше 20
transformed_array = [0 if x < 10 else 1 if x > 20 else x for x in array]

# Вывод исходного и преобразованного массивов в виде строки
print("Исходный массив:", ' '.join(map(str, array)))
print("Преобразованный массив:", ' '.join(map(str, transformed_array)))