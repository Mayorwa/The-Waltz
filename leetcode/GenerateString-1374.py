def generateTheString(n: int) -> str:
    # check if number is odd or even
    # if odd just return a string n times
    # else: return a + b *n - 1
    if n % 2 == 0:
        return "a" + ("b" * (n - 1))
    return "a" * n

print("testcase 1: ", generateTheString(4))

print("testcase 2: ", generateTheString(2))

print("testcase 3: ", generateTheString(7))
print("testcase 4: ", generateTheString(0))