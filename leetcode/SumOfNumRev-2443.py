def sumOfNumberAndReverse(num) -> bool:
    r = num // 2
    for i in range(r, num):
        s = int(str(i)[::-1])
        if i + s == num:
            print("i", i)
            return True

    return False


print(sumOfNumberAndReverse(443))
print(sumOfNumberAndReverse(63))
print(sumOfNumberAndReverse(181))