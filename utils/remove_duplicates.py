# data = [(1526, 369), (1805, 486), ...]
def remove_duplicates(data, threshold=10):
    unique = []
    for element in data:
        is_duplicate = False
        for u in unique:
            if abs(element[0] - u[0]) <= threshold and abs(element[1] - u[1]) <= threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique.append(element)
    return unique
