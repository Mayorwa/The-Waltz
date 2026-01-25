def merge(nums1, m, nums2, n) -> None:
    idx, i, p = 0
    while idx < len(nums1):
        if nums1[i] == 0:
            nums1[i] = nums2[p]
            i += 1
            p += 1
        elif nums1[i] < nums2[p]:
            i += 1

        elif nums2[p] <= nums1[i]:
            x = nums2[p]
            nums2[p] = nums1[i]
            nums1[i] = x
            i += 1
            
        idx += 1
print(merge([4, 5, 6, 0, 0, 0, 0], 3, [1,2,3, 4], 4))

print(merge([1,2,3,0,0,0], 3, [2,5,6], 3))

