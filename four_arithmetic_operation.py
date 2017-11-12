#!/usr/bin/env python3


def str2list(temp):
    out_put = []
    while len(temp) > 0:
        sym = [temp.find("+"), temp.find("-"), temp.find("*"), temp.find("/")]
        if sym[1] == 0:
            sym[1] = temp.find("-", 1)
        for i in range(len(sym)):
            if sym[i] < 0:
                sym[i] = 1000
        fir = min(sym)
        if fir == 1000:
            out_put.append(temp)
            return out_put
        out_put.append(temp[:fir])
        out_put.append(temp[fir:fir + 1])
        temp = temp[fir + 1:]
    out_put.pop(-1)
    return out_put


def calc(first_in, second_in, char):
    first_number = float(first_in)
    second_number = float(second_in)
    if second_number == 0 and char == "/":
        raise ZeroDivisionError('ZeroDivisionError')
    return {"+": first_number + second_number, "-": first_number - second_number, "*": first_number * second_number,
            "/": first_number / second_number}[char]


def is_formula_first(char_formula, char_symbol):
    if char_formula == "+" or char_formula == "-":
        return False
    if char_symbol == "*" or char_symbol == "/":
        return False
    return True


def calc_without_bracket(mini_list):
    symbol = []
    num = []
    formula = mini_list
    if len(mini_list) == 1:
        return float(mini_list[0])
    while formula:
        if not symbol:
            num.append(formula.pop(0))
            symbol.append(formula.pop(0))
            num.append(formula.pop(0))
        elif is_formula_first(formula[0], symbol[-1]):
            temp_num1 = calc(num.pop(-1), formula.pop(1), formula.pop(0))
            num.append(temp_num1)
        else:
            num.append(calc(num.pop(-2), num.pop(-1), symbol.pop(-1)))
            symbol.append(formula.pop(0))
            num.append(formula.pop(0))
    return calc(num.pop(-2), num.pop(-1), symbol.pop(-1))


def remove_bracket(this_str):
    last_left_bracket = this_str.rfind("(")
    first_right_bracket = this_str.find(")", last_left_bracket)
    if last_left_bracket > -1 and first_right_bracket > -1:
        temp_str = this_str[last_left_bracket + 1:first_right_bracket]
        temp_res = calc_without_bracket(str2list(temp_str))
        temp_res_chr = repr(temp_res)
        new_str = this_str[:last_left_bracket] + temp_res_chr + this_str[first_right_bracket + 1:]
        return remove_bracket(new_str)  # 这个return 的意义是什么？
    else:
        final = calc_without_bracket(str2list(this_str))
        return final


def main(str1):
    return remove_bracket(str1)

if __name__ == '__main__':
    s = input()
    print(main(s))
