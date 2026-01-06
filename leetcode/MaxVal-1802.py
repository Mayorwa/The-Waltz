def maxValue(n, index, maxSum):
    hill_height = 0
    total_sum = n
    left_bound = index + 1
    right_bound = index - 1
    hill_width = 1

    while total_sum <= maxSum:
        left_bound -= 1
        right_bound += 1
        if left_bound == index and right_bound == index:
            total_sum += hill_width
        else:
            l_, r_ = max(left_bound, 0), min(right_bound, n - 1)
            if left_bound < l_ and right_bound > r_:
                rm = maxSum - total_sum
                hill_height += int(rm / hill_width) + 1
                break
            else:
                hill_width = r_ - l_ + 1
                total_sum += hill_width
        hill_height += 1
    return hill_height


print(maxValue(4, 2, 6))
print(maxValue(7, 3, 10))