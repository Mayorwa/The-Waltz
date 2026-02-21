def generateParenthesis(n):
    result = []

    def backtrack(current, open_count, close_count):
        # If the string is complete
        if len(current) == 2 * n:
            result.append(current)
            return

        # If we can add '('
        if open_count < n:
            print("current", current + "(", open_count, close_count)
            backtrack(current + "(", open_count + 1, close_count)

        # If we can add ')'
        if close_count < open_count:
            print("current", current + ")", open_count, close_count)
            backtrack(current + ")", open_count, close_count + 1)

    backtrack("", 0, 0)
    return result


print(generateParenthesis(3))