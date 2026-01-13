def removeDuplicates(nums) -> int:
    k = 0
    last_seen = '_'

    for i in nums:
        if i != last_seen:
            nums[k] = i
            k += 1
            last_seen = i

    return k



print(removeDuplicates([1, 1, 2]))
print(removeDuplicates([0, 0, 1, 1, 1, 2, 2, 3, 3, 4]))