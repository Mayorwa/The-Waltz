def removeElement( nums, val):
    i = 0
    for idx in nums:
        if idx != val:
            nums[i] = idx
            i += 1
    return i

print(removeElement([3,2,2,3], 3)) # [2,2]
print(removeElement([0,1,2,2,3,0,4,2], 2))  # [0,1,4,0,3]