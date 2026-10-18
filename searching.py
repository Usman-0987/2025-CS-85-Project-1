from sorting import quick_sort, get_value, NUMBER_COLUMNS

MODES = ["contains", "starts with", "ends with", "equals"]


def check(row, condition):
    """condition = (column, mode, value). Returns True or False."""
    column, mode, value = condition
    text = str(row[column]).lower()
    value = value.lower()
    if mode == "contains":
        return value in text
    if mode == "starts with":
        return text.startswith(value)
    if mode == "ends with":
        return text.endswith(value)
    return text == value                      # equals


def linear_search(rows, condition):
    result = []
    for row in rows:
        if check(row, condition):
            result.append(row)
    return result


def binary_search(rows, column, value):
    """Exact match only. Needs sorted data, so sort by that column first."""
    rows = quick_sort(rows, lambda r: get_value(r, column))[0]
    target = int(value) if column in NUMBER_COLUMNS else value.lower()
    low, high = 0, len(rows) - 1
    found = -1
    while low <= high:
        mid = (low + high) // 2
        current = get_value(rows[mid], column)
        if current == target:
            found = mid
            break
        elif current < target:
            low = mid + 1
        else:
            high = mid - 1
    if found == -1:
        return []
    left = right = found                      # collect neighbours with the same value
    while left > 0 and get_value(rows[left - 1], column) == target:
        left -= 1
    while right < len(rows) - 1 and get_value(rows[right + 1], column) == target:
        right += 1
    return rows[left:right + 1]


def composite_search(rows, cond1, op, cond2):
    result = []
    for row in rows:
        a = check(row, cond1)
        b = check(row, cond2)
        if op == "AND":
            ok = a and b
        elif op == "OR":
            ok = a or b
        else:                                 # NOT means cond1 but not cond2
            ok = a and not b
        if ok:
            result.append(row)
    return result# -*- coding: utf-8 -*-

