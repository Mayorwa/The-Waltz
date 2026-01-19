def addBinary(a, b):
    x = max(len(a), len(b))
    result = ""
    num_bin_map = {3: '11', 2: '10', 1: '1', 0: '0'}
    remainder = 0

    a = a[::-1]
    b = b[::-1]
    for i in range(0, x):
        cumm = remainder
        if i < len(a):
            cumm += int(a[i])
        if i < len(b):
            cumm += int(b[i])


        cumm = num_bin_map[cumm]
        if len(cumm) > 1:
            remainder = 1
            result += cumm[-1]
        else:
            remainder = 0
            result += cumm[0]

    if remainder:
        result += str(remainder)
    return result[::-1]

print("tc 1: ", addBinary("11", "1"))
print("tc 2: ", addBinary("1010", "1011"))