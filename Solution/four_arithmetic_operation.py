import time


def calc(s):
    rank = {
        ')': 0,
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '^': 3,
    }

    def apart(formula):
        tmp = ''
        for i in formula:
            if i == ' ':
                continue
            elif not i.isdigit() and i != '.':
                if tmp != '':
                    yield float(tmp)
                    tmp = ''
                yield i
            else:
                if not tmp:
                    tmp = i
                elif tmp[0].isdigit():
                    tmp += i
                else:
                    yield tmp
                    tmp = i
        if tmp:
            if tmp.isdigit():
                yield float(tmp)
            else:
                yield tmp

    def sustained_operation(operator=''):
        level = rank[operator] if operator else -1
        while operators and operators[-1] not in '()' and rank[operators[-1]] >= level:
            operator = operators.pop(-1)
            sec = numbers.pop(-1)
            fir = numbers.pop(-1)
            if sec == 0 and operator == "/":
                raise ZeroDivisionError('ZeroDivisionError')
            if operator == '+':
                numbers.append(fir + sec)
            elif operator == '-':
                numbers.append(fir - sec)
            elif operator == '*':
                numbers.append(fir * sec)
            elif operator == '/':
                numbers.append(fir / sec)
            elif operator == '^':
                ret = 1
                for i in range(int(sec)):
                    ret *= fir
                numbers.append(ret)

    numbers = []
    operators = []
    s = '0' + s if s.startswith('-') else s
    s = s[:(len(s))-1] if s.endswith('=') else s
    s = s.replace('÷', '/')

    for part in apart(s):
        if isinstance(part, float):
            numbers.append(part)
        elif not operators or part == '(':
            operators.append(part)
        elif part == ')':
            sustained_operation(part)
            operators.pop(-1)
        else:
            sustained_operation(part)
            operators.append(part)
    sustained_operation()
    if len(numbers) != 1:
        print(numbers)
        return ''
    result = numbers[0]
    result = int(result) if int(result) == result else result
    return result


a = "123.33+32*2+123÷32*2+5^(1+2*1)-32*2+5*0"
b = "-123 +32+2*(5*2+3+5*(2+66))"


start = time.time()
for x in (a, b):
    print(f'{x} = {calc(x)}')
# for i in range(1000):
#     for x in (a, b, c, d):
#         calc(x)
print(time.time() - start)
