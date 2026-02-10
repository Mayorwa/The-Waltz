def majorityElement(nums) -> int:
    # TODO: Brute Force, loop through store in dictionary if a value exceeds n/2 then return the key
    dit = {}
    half = len(nums) // 2
    for i in nums:
        if i not in dit:
            dit[i] = 1
        else:
            dit[i] += 1

        if dit[i] > half:
            return i
    return nums[0]


print("testcase 1: ", majorityElement([3,2,3]))

print("testcase 2: ", majorityElement([2,2,1,1,1,2,2]))
