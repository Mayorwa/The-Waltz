def convertToTitle(columnNumber):
    # approach 1:
    # alpha* 26^n + beta * 26^n-1 + gamma + 26^n-2
    # while(n > 0) n modulo 26 get remainder and set n to be equals to n//26

    # testcase 1, 28: 28%26 -> 2:B -> 1

    dit = {i: chr(i + 64) for i in range(1, 27)}
    result = ""
    while (columnNumber > 26):
        r = columnNumber % 26
        result += dit[r]
        columnNumber = columnNumber // 26
    result += dit[columnNumber]

    return result[::-1]

print("Testcase 1", convertToTitle(1)) #A
print("Testcase 2", convertToTitle(28)) #AB
print("Testcase 3", convertToTitle(701)) # ZY
print("Testcase 3", convertToTitle(809)) # AEC