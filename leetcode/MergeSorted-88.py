def merge(nums1, m, nums2, n):
    idx = len(nums1) - 1
    i = m - 1
    j = n - 1


    while idx >= 0:
        if i < 0:
            nums1[idx] = nums2[j]
            j -= 1
        elif j < 0:
            nums1[idx] = nums1[i]
            i -= 1
        elif nums1[i] > nums2[j]:
            nums1[idx] = nums1[i]
            i -= 1
        elif nums1[i] <= nums2[j]:
            nums1[idx] = nums2[j]
            j -= 1
        idx -= 1
    return nums1
print(merge([4, 5, 6, 0, 0, 0, 0], 3, [1,2,3, 4], 4))

print(merge([1,2,3,0,0,0], 3, [2,5,6], 3))

