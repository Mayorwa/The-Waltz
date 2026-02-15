def convertToTitle(columnNumber):
    # approach 1:
    # alpha* 26^n + beta * 26^n-1 + gamma + 26^n-2
    # while(n > 0) n modulo 26 get remainder and set n to be equals to n//26
    return "AA"

print("Testcase 1", convertToTitle(1)) #A
print("Testcase 2", convertToTitle(28)) #AB
print("Testcase 3", convertToTitle(701)) # ZY
