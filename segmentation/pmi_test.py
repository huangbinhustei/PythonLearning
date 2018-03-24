candidtions = ["黛玉", "宝玉", "和林", "林黛玉"]


def get_pmi(s):
    def spelling(sentence, ret, flag):
        for start in range(len(sentence)):
            for lth in range(len(sentence) - start + 1):
                word = sentence[start:len(sentence) - lth]
                word = word if flag else word[::-1]
                if len(word) == 1 or word in candidtions:
                    ret.append(word)
                    return spelling(sentence[len(sentence) - lth:], ret, flag)
    nor = [[], []]
    for ind, f in enumerate([True, False]):
        spelling(s if f else s[::-1], nor[ind], f)
    return nor

    # todo: 切词可能有多个最短版本，这时候需要挑选一个内聚值最高（低）的


print(get_pmi("贾宝玉和林黛玉"))
print(get_pmi("这会子"))
