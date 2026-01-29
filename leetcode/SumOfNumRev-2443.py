def sumOfNumberAndReverse(num) -> bool:
    if num == 0:
        return True
    r = num // 2
    for i in range(r, num):
        s = int(str(i)[::-1])
        if i + s == num:
            return True

    return False


print(sumOfNumberAndReverse(443))
print(sumOfNumberAndReverse(63))
print(sumOfNumberAndReverse(181))
# print(sumOfNumberAndReverse(0))