from sys import setrecursionlimit, exit
from decimal import Decimal as Dc, getcontext
from functools import lru_cache


getcontext().prec = 150
setrecursionlimit(3000)


class EngineeringCalculator:
    def __init__(self):
        self.operators = {
            '+': (1, lambda x, y: x + y),
            '-': (1, lambda x, y: x - y),
            '*': (2, lambda x, y: x * y),
            '/': (2, lambda x, y: MathOperators.division(x, y)),
            '^': (3, lambda x, y: x ** y),
            'p': (3, lambda x, y: MathOperators.percentage(x, y)),
            'div': (3, lambda x, y: MathOperators.division(x, y, div_type='div')),
            'mod': (3, lambda x, y: MathOperators.division(x, y, div_type='mod')),
            'gcd': (3, lambda x, y: MathOperators.gcd(x, y)),
            'sqrt': (3, lambda x, y: MathOperators.sqrt(x, y)),
            '!': (4, lambda x: MathOperators.factorial(x)),
            'sin': (4, lambda x: MathOperators.get_sin(x)),
            'cos': (4, lambda x: MathOperators.get_cos(x)),
            'tg': (4, lambda x: MathOperators.get_tg(x)),
            'ln': (4, lambda x: MathOperators.ln(x)),
            'e': (4, lambda x: MathOperators.exponentiation(x)),
            'exp': (4, lambda x: MathOperators.exponentiation(x))
        }

    def __split_into_tokens(self, expression):
        tokens = []
        current_token = ''
        for index, char in enumerate(expression):
            if char.isdigit() or char == '.':
                current_token += char
            elif char.isalpha():
                current_token += char
            elif char == '-' and (
                    index == 0 or expression[index - 1] == '(' or expression[index - 1] in self.operators):
                current_token += char
            else:
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
                if char in self.operators or char in ['(', ')']:
                    if (char == '!' and (not expression[index-1].isdigit() and expression[index-1] != ')'))\
                            or index == 0:
                        exit("Неверное местоположение факториала!")
                    tokens.append(char)
        if current_token:
            tokens.append(current_token)
        return tokens

    def __remove_brackets(self, tokens):
        output = []
        operator_stack = []
        for token in tokens:
            if token.isdigit() or '.' in token or ('-' in token and len(token) > 1):
                output.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack:
                    operator_stack.pop()
                else:
                    exit("Несогласованные скобки")
            elif token in self.operators:
                while operator_stack and self.operators.get(token)[0] <= \
                        self.operators.get(operator_stack[-1], (0,))[0]:
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            else:
                exit("Недопустимый оператор")
        while operator_stack:
            if operator_stack[-1] == '(':
                exit("Несогласованные скобки")
            output.append(operator_stack.pop())
        return output

    def __summarize(self, expression):
        stack = []
        for token in expression:
            if token.isdigit() or '.' in token or ('-' in token and len(token) > 1):
                stack.append(float(token))
            elif token in self.operators:
                if self.operators[token][0] == 4:
                    if len(stack) == 1:
                        stack.append(self.operators[token][1](stack.pop()))
                    else:
                        b = stack.pop()
                        stack.append(self.operators[token][1](b))
                else:
                    b = stack.pop()
                    a = stack.pop()
                    stack.append(self.operators[token][1](a, b))

        return stack[0]

    def calculate(self, expression):
        tokens = self.__split_into_tokens(expression)
        clear_order = self.__remove_brackets(tokens)
        result = self.__summarize(clear_order)
        return result


class MathOperators:
    EXP_FLAG = False

    MAX_RADIAN_VALUE = 330
    MIN_RADIAN_VALUE = -330

    MAX_EXP_POWER = 709
    MAX_EXP_LEN_OF_ROW = 1000
    MAX_LN_LEN_OF_ROW = 15000

    MAX_FACTORIAL_NUMBER = 1490

    @classmethod
    def get_sin(cls, value):
        if value > cls.MAX_RADIAN_VALUE:
            exit("Слишком большое значение в аргументе Синуса!")
        elif value < cls.MIN_RADIAN_VALUE:
            exit("Слишком маленькое значение в аргументе Синуса!")

        sin = Dc(0)
        len_of_row = cls.MAX_FACTORIAL_NUMBER // 2
        sign = Dc(1)

        for x in range(1, len_of_row * 2 + 1, 2):
            sin += sign * Dc(value) ** x / cls.factorial(x)
            sign = -sign

        return float(round(sin, 11))

    @classmethod
    def get_cos(cls, value):
        if value > cls.MAX_RADIAN_VALUE:
            exit("Слишком большое значение в аргументе Косинуса!")
        elif value < cls.MIN_RADIAN_VALUE:
            exit("Слишком маленькое значение в аргументе Косинуса!")
        elif value == 0:
            return 1

        cos = Dc(0)
        len_of_row = cls.MAX_FACTORIAL_NUMBER // 2
        sign = Dc(1)

        for x in range(0, len_of_row * 2 + 1, 2):
            cos += sign * Dc(value) ** x / cls.factorial(x)
            sign = -sign

        return float(round(cos, 11))

    @classmethod
    def get_tg(cls, value):
        if value > cls.MAX_RADIAN_VALUE:
            exit("Слишком большое значение в аргументе Тангенса!")
        elif value < cls.MIN_RADIAN_VALUE:
            exit("Слишком маленькое значение в аргументе Тангенса!")

        return float(round(cls.get_sin(value) / cls.get_cos(value), 11))

    @classmethod
    def ln(cls, value):
        if value == 0:
            exit("Аргумент логарифма должен быть > 0!")

        if cls.EXP_FLAG:
            return cls.EXP_FLAG

        natural_log = 0
        len_of_row = cls.MAX_LN_LEN_OF_ROW

        y = (value - 1) / (value + 1)

        for x in range(1, len_of_row + 2, 2):
            natural_log += y ** x / x

        natural_log += y ** (len_of_row + 1) / (len_of_row + 1)

        return 2 * natural_log

    @staticmethod
    def sqrt(value, power):
        return pow(value, 1./power)

    @classmethod
    def exponentiation(cls, power):
        if power > cls.MAX_EXP_POWER:
            exit("Слишком большая степень экспоненты(стремится к inf)")

        cls.EXP_FLAG = power

        len_of_row = cls.MAX_EXP_LEN_OF_ROW
        exp = 0

        for x in range(len_of_row):
            exp += int(power) ** x / (cls.factorial(x))

        return exp

    @staticmethod
    def gcd(x, y):
        while y != 0:
            x, y = y, x % y

        return x

    @staticmethod
    def percentage(value, part):
        return value / 100 * part

    @staticmethod
    def division(divisible, divider, div_type='/'):
        try:
            match div_type:
                case '/':
                    return divisible / divider
                case 'mod':
                    return divisible % divider
                case 'div':
                    return divisible // divider
        except ZeroDivisionError:
            exit("На ноль делить нельзя!")

    @classmethod
    @lru_cache
    def factorial(cls, x):
        if x > cls.MAX_FACTORIAL_NUMBER:
            exit("Слишком большое число!")
        if x < 0:
            exit("Факториал не может быть отрицательным")

        if x == 0:
            return 1
        elif x == 1:
            return 1
        else:
            return x * cls.factorial(x - 1)


def dec_input(func):
    def wrapper():
        print("""Доступные команды, где x, y - введённые числа:
ln(x) - Натуральный логарифм от x,
exp(x) или e(x) - Возведение экспоненты в степень x,
^ - Возведение в степень,
p(целое число, процент) - Берёт процент от заданного целого числа,
gcd(x, y) - Наибольший общий делитель у (x и y),
sqrt(x, степень корня) - Корень заданной степени из x,
sin(x), cos(x), tg(x) - Синус, косинус и тангенс от -330 <= x <= 330 в радианах,
x! - Факториал от введённого числа,
div(делимое, делитель), mod(делимое, делитель) - Целочисленное деление и деление с остатком,
Базовые операторы +, -, *, /
exit - Выход из ввода калькулятора
""")
        func()

    return wrapper()


@dec_input
def input_stream():
    calculator = EngineeringCalculator()

    while True:
        expression = input('Введите выражение или команду exit: ').replace(" ", "")

        if expression.lower().strip() == "exit":
            break

        result = calculator.calculate(expression)
        print("Результат:", result)
