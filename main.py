# -*- coding: utf-8 -*-
from collections import Counter
import heapq
import math
import graphviz
import tabulate

# Получение текста от пользователя
text = input("Введите текст для кодирования, без переноса строк (enter): ")

def calculate_frequencies(text):
    # Подсчет количества вхождений каждого символа
    char_counts = Counter(text)
    total_chars = len(text)

    # Преобразуем количество в частоту (отношение к общему количеству символов)
    freq = {char: count / total_chars for char, count in char_counts.items()}

    # Добавляем буквы, которых нет в тексте, с очень малой частотой
    russian_alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ "
    for char in russian_alphabet:
        if char not in freq:
            freq[char] = 0.0001

    return freq


class Node:
    def __init__(self, freq, symbol, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right
        self.direction = ''  # 0 или 1, направление от родителя

    def __lt__(self, other):
        return self.freq < other.freq


def get_binary_codes(node, val='', codes=None, suffix=False):
    # Собираем коды вместо вывода на экран
    if codes is None:
        codes = {}

    if suffix:
        # Для суффиксных кодов добавляем направление в начало
        new_val = node.direction + val
    else:
        new_val = val + node.direction

    if node.left:
        get_binary_codes(node.left, new_val, codes, suffix)
    if node.right:
        get_binary_codes(node.right, new_val, codes, suffix)
    if not node.left and not node.right:
        codes[node.symbol] = new_val

    return codes


def build_huffman_tree_binary(frequencies):
    # Создаем начальные узлы из символов
    nodes = []
    for char, freq in frequencies.items():
        heapq.heappush(nodes, Node(freq, char))

    # Строим дерево Хаффмана
    while len(nodes) > 1:
        # Берем два узла с наименьшими частотами
        left = heapq.heappop(nodes)
        right = heapq.heappop(nodes)

        # Назначаем направления
        left.direction = '0'
        right.direction = '1'

        # Создаем новый внутренний узел
        parent = Node(left.freq + right.freq, left.symbol + right.symbol, left, right)

        heapq.heappush(nodes, parent)

    return nodes[0]  # Возвращаем корень дерева


class QuaternaryNode:
    def __init__(self, freq, symbol, children=None):
        self.freq = freq
        self.symbol = symbol
        self.children = children if children else []
        self.directions = []  # '0', '1', '2', '3' - направления от родителя

    def __lt__(self, other):
        return self.freq < other.freq


def get_quaternary_codes(node, val='', codes=None, suffix=False):
    # Собираем коды вместо вывода на экран
    if codes is None:
        codes = {}

    for i, child in enumerate(node.children):
        if child:
            if suffix:
                # Для суффиксных кодов добавляем направление в начало
                new_val = str(i) + val
            else:
            # Для префиксных кодов добавляем направление в конец
                new_val = val + str(i)

            if not child.children:  # Если это лист
                if child.symbol != "empty":  # Не выводим фиктивные узлы
                    codes[child.symbol] = new_val
            else:
                get_quaternary_codes(child, new_val, codes, suffix)

    return codes


def build_huffman_tree_quaternary(frequencies):
    # Создаем начальные узлы из символов
    nodes = []
    for char, freq in frequencies.items():
        heapq.heappush(nodes, QuaternaryNode(freq, char))

    # Если необходимо, добавляем фиктивные узлы, чтобы количество листьев
    # давало хорошее дерево (кратное 3 плюс 1)
    while (len(nodes) - 1) % 3 != 0:
        heapq.heappush(nodes, QuaternaryNode(0, "empty"))

    # Строим дерево Хаффмана для четверичного алфавита
    while len(nodes) > 1:
        # Берем всегда ровно 4 узла с наименьшими частотами
        children = []
        child_symbols = ""
        total_freq = 0

        for _ in range(4):
            if nodes:
                child = heapq.heappop(nodes)
                children.append(child)
                child_symbols += child.symbol
                total_freq += child.freq
            else:
                # Если узлов не хватает, добавляем пустышки
                children.append(None)

        # Создаем новый внутренний узел с 4 детьми (некоторые могут быть None)
        parent = QuaternaryNode(total_freq, child_symbols, children)

        heapq.heappush(nodes, parent)

    return nodes[0]  # Возвращаем корень дерева


def visualize_binary_tree(root, filename="huffman_binary_tree"):
    dot = graphviz.Digraph(comment='Huffman Binary Tree')

    def add_nodes_edges(node, node_id=0):
        if node is None:
            return

        # Добавляем узел
        if not node.left and not node.right:  # Лист
            dot.node(str(node_id), f"{node.symbol}\n{node.freq:.4f}", shape="box")
        else:  # Внутренний узел
            dot.node(str(node_id), f"{node.freq:.4f}")

        # Рекурсивно добавляем левого ребенка
        if node.left:
            left_id = node_id * 2 + 1
            add_nodes_edges(node.left, left_id)
            dot.edge(str(node_id), str(left_id), label="0")

        # Рекурсивно добавляем правого ребенка
        if node.right:
            right_id = node_id * 2 + 2
            add_nodes_edges(node.right, right_id)
            dot.edge(str(node_id), str(right_id), label="1")

    add_nodes_edges(root)
    dot.render(filename, format='png', cleanup=True)
    return filename + ".png"


def visualize_quaternary_tree(root, filename="huffman_quaternary_tree"):
    dot = graphviz.Digraph(comment='Huffman Quaternary Tree')

    def add_nodes_edges(node, node_id=0):
        if node is None:
            return

        # Добавляем узел
        if not node.children:  # Лист
            if "dummy" in node.symbol or node.symbol == "empty":
                dot.node(str(node_id), f"{node.symbol}\n{node.freq:.4f}", shape="box",
                         style="dashed", color="gray", fontcolor="gray")
            else:
                dot.node(str(node_id), f"{node.symbol}\n{node.freq:.4f}", shape="box")
        else:  # Внутренний узел
            dot.node(str(node_id), f"{node.freq:.4f}")

        # Рекурсивно добавляем детей
        for i, child in enumerate(node.children):
            if child:
                child_id = node_id * 4 + i + 1
                add_nodes_edges(child, child_id)
                if "dummy" in child.symbol or child.symbol == "empty":
                    dot.edge(str(node_id), str(child_id), label=str(i),
                            style="dashed", color="gray")
                else:
                    dot.edge(str(node_id), str(child_id), label=str(i))

    add_nodes_edges(root)
    dot.render(filename, format='png', cleanup=True)
    return filename + ".png"

# Подсчет частот символов
frequencies = calculate_frequencies(text)

# Построение бинарного дерева Хаффмана
binary_tree = build_huffman_tree_binary(frequencies)

# Построение четверичного дерева Хаффмана
quaternary_tree = build_huffman_tree_quaternary(frequencies)
# Получение кодов для бинарного дерева (префиксные и суффиксные)
binary_prefix_codes = get_binary_codes(binary_tree)
binary_suffix_codes = get_binary_codes(binary_tree, suffix=True)

# Получение кодов для четверичного дерева (префиксные и суффиксные)
quaternary_prefix_codes = get_quaternary_codes(quaternary_tree)
quaternary_suffix_codes = get_quaternary_codes(quaternary_tree, suffix=True)

# Вывод кодов в виде таблицы для бинарного алфавита
print("Коды Хаффмана для бинарного алфавита {0, 1}:")
print("Символ | Префиксный код | Суффиксный код | Частота")
print("-------|----------------|----------------|--------")
for symbol in sorted(binary_prefix_codes.keys()):
    print(f"{symbol:^7}| {binary_prefix_codes[symbol]:<14}| {binary_suffix_codes[symbol]:<14}| {frequencies[symbol]:.6f}")

# Вывод кодов в виде таблицы для четверичного алфавита
print("\nКоды Хаффмана для четверичного алфавита {0, 1, 2, 3}:")
print("Символ | Префиксный код | Суффиксный код | Частота")
print("-------|----------------|----------------|--------")
for symbol in sorted(quaternary_prefix_codes.keys()):
    print(f"{symbol:^7}| {quaternary_prefix_codes[symbol]:<14}| {quaternary_suffix_codes[symbol]:<14}| {frequencies[symbol]:.6f}")

# Визуализация деревьев (требуется библиотека graphviz)
try:
    binary_tree_image = visualize_binary_tree(binary_tree)
    print(f"\nБинарное дерево Хаффмана сохранено как {binary_tree_image}")

    quaternary_tree_image = visualize_quaternary_tree(quaternary_tree)
    print(f"Четверичное дерево Хаффмана сохранено как {quaternary_tree_image}")
except Exception as e:
    print(f"\nНе удалось создать визуализацию: {e}")
    print("Для визуализации требуется установленная библиотека graphviz.")

# Сохранение таблиц кодов в CSV файлы
import csv

# Сохранение бинарных кодов
with open('binary_huffman_codes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Символ', 'Префиксный код', 'Суффиксный код', 'Частота'])
    for symbol in sorted(binary_prefix_codes.keys()):
        writer.writerow([symbol, binary_prefix_codes[symbol], binary_suffix_codes[symbol], f"{frequencies[symbol]:.6f}"])

print("\nБинарные коды Хаффмана сохранены в binary_huffman_codes.csv")

# Сохранение четверичных кодов
with open('quaternary_huffman_codes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Символ', 'Префиксный код', 'Суффиксный код', 'Частота'])
    for symbol in sorted(quaternary_prefix_codes.keys()):
        writer.writerow([symbol, quaternary_prefix_codes[symbol], quaternary_suffix_codes[symbol], f"{frequencies[symbol]:.6f}"])

print("Четверичные коды Хаффмана сохранены в quaternary_huffman_codes.csv")

# Расчет избыточности кода
def calculate_redundancy(codes, frequencies):
    # Вычисляем среднюю длину кода
    avg_length = sum(len(codes[symbol]) * frequencies[symbol] for symbol in codes)

    # Вычисляем энтропию источника
    total_freq = sum(frequencies.values())
    entropy = -sum((freq/total_freq) * math.log2(freq/total_freq) for freq in frequencies.values() if freq > 0)

    # Избыточность кода = средняя длина - энтропия
    redundancy = avg_length - entropy

    return avg_length, entropy, redundancy

# Расчет избыточности для бинарных кодов
binary_prefix_avg, binary_entropy, binary_prefix_redundancy = calculate_redundancy(binary_prefix_codes, frequencies)
binary_suffix_avg, _, binary_suffix_redundancy = calculate_redundancy(binary_suffix_codes, frequencies)

# Расчет избыточности для четверичных кодов
quaternary_prefix_avg, quaternary_entropy, quaternary_prefix_redundancy = calculate_redundancy(quaternary_prefix_codes, frequencies)
quaternary_suffix_avg, _, quaternary_suffix_redundancy = calculate_redundancy(quaternary_suffix_codes, frequencies)

# Вывод результатов
print("\nИзбыточность кодов:")
print("Алфавит | Тип кода    | Средняя длина | Энтропия | Избыточность")
print("--------|-------------|---------------|----------|-------------")
print(f"Бинарный  | {binary_prefix_avg:.6f} | {binary_entropy:.6f} | {binary_prefix_redundancy:.6f}")
print(f"Четверичный | {quaternary_prefix_avg:.6f} | {quaternary_entropy:.6f} | {quaternary_prefix_redundancy:.6f}")
# Текстовое представление бинарного дерева
def print_tree(node, level=0, prefix="Root: "):
    if node is not None:
        print(" " * level + prefix + f"{node.symbol} ({node.freq:.4f})")
        if node.left or node.right:
            if node.left:
                print_tree(node.left, level + 1, "L(0): ")
            else:
                print(" " * (level + 1) + "L(0): None")
            if node.right:
                print_tree(node.right, level + 1, "R(1): ")
            else:
                print(" " * (level + 1) + "R(1): None")


# Текстовое представление четверичного дерева
def print_quaternary_tree(node, level=0, prefix="Root: "):
    if node is not None:
        if "empty" not in node.symbol: 
            print(" " * level + prefix + f"{node.symbol} ({node.freq:.4f})")
            for i, child in enumerate(node.children):
                if child:
                    if "empty" not in child.symbol:  
                        print_quaternary_tree(child, level + 1, f"Child({i}): ")
                    else:
                        print(" " * (level + 1) + f"Child({i}): [empty node]")
                else:
                    print(" " * (level + 1) + f"Child({i}): None")

