def linear_search(nums, target, reverse=False):
    if not reverse:
        for i in range(len(nums)):
            if nums[i] == target:
                return i
            else:
                continue
        return -1
    else:
        count = None
        for i in range(len(nums)):
            if nums[i] == target:
                count = i
                print('hello')
        print('hello')
        if count == None:
            return -1
        return count

print(linear_search([2, 3], -1, reverse=True))
