import sys

# Считывание одномерного массива из параметров командной строки. 
# Модуль sys - предоставляет доступ к некоторым переменным и функциям интерпретатора.
import sys

# Считывание одномерного массива из параметров командной строки
# map(int, ...) - преобразует каждый элемент списка в целое число.
# sys.argv[1:] - список параметров командной строки, за исключением имени программы.
array = list(map(int, sys.argv[1:]))

# Вывод повторяющихся элементов в консоль
# set - создает множество, состоящее из элементов, встречающихся в массиве более одного раза.
# array.count(x) - подсчитывает количество вхождений элемента x в массиве.
# if repeated_elements - Проверяет, пусто ли множество repeated_elements
repeated_elements = set([x for x in array if array.count(x) > 1])
if repeated_elements:
    print("Повторяющиеся элементы:", repeated_elements)
else:
    print("Нет повторяющихся элементов")

# Присвоение нулевых значений элементам массива, которые меньше 10, и значений 1 элементам, которые больше 20
transformed_array = [0 if x < 10 else 1 if x > 20 else x for x in array]

# Вывод исходного и преобразованного массивов в виде строки
# map(str, array) - преобразует каждый элемент массива в строку. ' '.join(...) - 
# - объединяет элементы списка в строку, разделяя их пробелами.
print("Исходный массив:", ' '.join(map(str, array)))
print("Преобразованный массив:", ' '.join(map(str, transformed_array)))
