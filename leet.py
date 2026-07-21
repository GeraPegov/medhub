
from typing import List
nums = [3, 2, 4]
target = 6

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        new_list = [0]
        for i in nums:
            new_list.append(new_list[-1]+i)
        new_list = new_list[1:]
        print(new_list)
        if new_list[0] == target:
            return [0]
        for i in range(1, len(new_list)):
            if new_list[i] == target:
                return [i-1, i]
            new_sum = new_list[i] - new_list[i-1]
            print(new_sum)
            if new_sum == target:
                return [i-1, i]

            if new_sum < target:
                l, r = i-1, i
                while new_list[r]-new_list[l] < target:
                    if l - 1 >= 0:
                        l -= 1
                    elif l - 1 < 0:
                        break
                    if new_list[r]-new_list[l] == target:
                        return [l, r]
            
print(Solution().twoSum(nums, target))