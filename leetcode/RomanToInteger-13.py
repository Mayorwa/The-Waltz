def romanToInt(s: str) -> int:
    last_value = 0
    hm = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

    result = 0

    for i in reversed(s):
        if last_value != 0 and hm[i] < last_value:
            result += last_value - hm[i]
            last_value = 0
        elif hm[i] >= last_value:
            result += last_value
            last_value = hm[i]

    if last_value != 0:
        result += last_value

    return result

print("testcase 1: ", romanToInt("IV"))
print("testcase 2: ", romanToInt("III"))
print("testcase 3: ", romanToInt("LVIII"))
print("testcase 4: ", romanToInt("MCMXCIV"))