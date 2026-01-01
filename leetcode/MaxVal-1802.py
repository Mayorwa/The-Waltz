def maximumSum(arr):
    result = 0
    for i in arr:
        result += i

    return result

def maxValue(n, index, maxSum):
    arr = [1] * n

    arr[index] = maxSum + 1 - n

    print(arr)

    isLoop = True

    while isLoop:
        if abs(arr[index] - arr[index + 1]) <= 1 or abs(arr[index - 1] - arr[index]) <= 1:
            isLoop = False
            break

        # arr[]





print(maxValue(7, 3, 10))
