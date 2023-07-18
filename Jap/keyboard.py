import json


def read_kana():
    with open("./Jap/katakana.json", 'r') as f:
        al = json.load(f)
        basic = al["basic kana"]
        extended = al["extended kana"]
    return basic, extended


basic, extended = read_kana()
vowels = ['a', 'i', 'u', 'e', 'o']


def parse_one(kana: str, fon: str, dic: dict):
    k = dic.get(fon, None)
    if k is not None:
        return kana+k, ''
    return kana, fon


def parse_twice(kana: str, fon: str):
    kana, fon = parse_one(kana, fon, basic)
    if len(fon) < 2:
        return kana, fon
    if fon != '':
        kana, fon = parse_one(kana, fon, extended)
    if fon != '':
        raise Exception(f"Cant parse: {fon}")
    return kana, fon


def parse(text: str):
    text = text.lower()
    text = ''.join(text.split())
    text = text.replace('l', 'r')
    text = text.replace('c', 'k')
    text = text.replace('kh', 'ch')
    fon = text[0]
    kana = ''
    kana, fon = parse_one(kana, fon, basic)
    for j, letter in enumerate(text[1:-1]):
        i = j+1
        if letter == text[i+1] and letter not in vowels and fon == '':
            if letter == 'n':
                kana += basic['n']
            else:
                kana += extended["tsu"]
            fon = ''
        elif letter == text[i-1] and letter in vowels:
            kana += basic["-"]
            fon = ''
        else:
            fon += letter
            if fon == 'n' and text[i+1] in vowels:
                continue
            try:
                kana, fon = parse_twice(kana, fon)
            except Exception:
                pass
            if len(fon) < 2 or (fon != '' and len(fon) == 2):
                continue
            elif len(fon) == 3:
                kana, fon = connect(kana, fon)
    if text[-1] == text[-2] and fon == '' and text[-2] in vowels:
        kana += basic['-']
        return kana
    fon += text[-1]
    kana, fon = connect(kana, fon)
    return kana


def connect(kana: str, fon: str):
    try:
        kana, fon = parse_twice(kana, fon)
        if fon == '':
            return kana, fon
    except Exception:
        pass
    lenfon = len(fon)
    fon1 = fon[0] + 'u'        
    kana, fon1 = parse_twice(kana, fon1)
    if lenfon == 1:
        return kana, ''
    fon = fon[1:]
    if lenfon == 3 and fon[-1] in vowels:
        kana, fon = parse_twice(kana, fon)
        if fon == '':
            return kana, fon
    fon1 = fon[0] + 'u'
    kana, fon1 = parse_twice(kana, fon1)
    if lenfon == 2:
        return kana, ''
    fon2 = fon[-1] + 'u'
    kana, fon2 = parse_twice(kana, fon2)
    fon = ''
    return kana, fon


def parse_foreach(words):
    words = words.split()
    kana = ''
    for word in words:
        kana += parse(word)
    return kana


import sys

if __name__ == "__main__":
    arg = sys.argv[1:]
    kana = ''
    for word in arg:
        kana += parse(word)
    print(kana)
