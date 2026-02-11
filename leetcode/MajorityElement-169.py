def majorityElement(nums) -> int:
    # TODO: Brute Force, loop through store in dictionary if a value exceeds n/2 then return the key
    # dit = {}
    # half = len(nums) // 2
    # for i in nums:
    #     if i not in dit:
    #         dit[i] = 1
    #     else:
    #         dit[i] += 1
    #
    #     if dit[i] > half:
    #         return i
    # return nums[0]
    # TODO: Optimized Solution, loop through check if count is 0 or if result is the present element or else decrement count
    count = 0
    result = 0
    for i in nums:
        if count == 0:
            result = i
            count += 1
        elif result == i:
            count += 1
        else:
            count -= 1
    return result


print("testcase 1: ", majorityElement([3,2,3]))

print("testcase 2: ", majorityElement([2,2,1,1,1,2,2]))
print("testcase 3: ", majorityElement([3, 3 ,2]))
