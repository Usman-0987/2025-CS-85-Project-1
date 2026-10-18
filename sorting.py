NUMBER_COLUMNS = ["year", "editions", "pages"]


def get_value(row, column):
    """Numbers sort as numbers, text sorts ignoring upper/lower case."""
    if column in NUMBER_COLUMNS:
        return row[column]
    return str(row[column]).lower()


def check_numbers(values):
    """Counting, Radix and Bucket sort need whole numbers."""
    for v in values:
        if not isinstance(v, int):
            raise ValueError("numbers only")


# ---------------- simple sorts ----------------

def bubble_sort(rows, key):
    arr = rows[:]
    comps = swaps = 0
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            comps += 1
            if key(arr[j]) > key(arr[j + 1]):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return arr, comps, swaps


def selection_sort(rows, key):
    arr = rows[:]
    comps = swaps = 0
    n = len(arr)
    for i in range(n):
        smallest = i
        for j in range(i + 1, n):
            comps += 1
            if key(arr[j]) < key(arr[smallest]):
                smallest = j
        if smallest != i:
            arr[i], arr[smallest] = arr[smallest], arr[i]
            swaps += 1
    return arr, comps, swaps


def insertion_sort(rows, key):
    arr = rows[:]
    comps = swaps = 0
    for i in range(1, len(arr)):
        j = i
        while j > 0:
            comps += 1
            if key(arr[j - 1]) > key(arr[j]):
                arr[j - 1], arr[j] = arr[j], arr[j - 1]
                swaps += 1
                j -= 1
            else:
                break
    return arr, comps, swaps


def gnome_sort(rows, key):
    arr = rows[:]
    comps = swaps = 0
    i = 0
    while i < len(arr):
        if i == 0:
            i += 1
        else:
            comps += 1
            if key(arr[i - 1]) <= key(arr[i]):
                i += 1
            else:
                arr[i - 1], arr[i] = arr[i], arr[i - 1]
                swaps += 1
                i -= 1
    return arr, comps, swaps


def shell_sort(rows, key):
    arr = rows[:]
    comps = swaps = 0
    gap = len(arr) // 2
    while gap > 0:
        for i in range(gap, len(arr)):
            temp = arr[i]
            j = i
            while j >= gap:
                comps += 1
                if key(arr[j - gap]) > key(temp):
                    arr[j] = arr[j - gap]
                    swaps += 1
                    j -= gap
                else:
                    break
            arr[j] = temp
        gap //= 2
    return arr, comps, swaps


# ---------------- quick and merge sorts ----------------

def quick_sort(rows, key):
    arr = rows[:]
    comps = swaps = 0
    stack = [(0, len(arr) - 1)]          # a stack instead of recursion (no crash on big data)
    while stack:
        low, high = stack.pop()
        if low >= high:
            continue
        pivot = key(arr[(low + high) // 2])      # middle element is the pivot
        i, j = low, high
        while i <= j:
            while True:                          # move i right while smaller than pivot
                comps += 1
                if key(arr[i]) < pivot:
                    i += 1
                else:
                    break
            while True:                          # move j left while bigger than pivot
                comps += 1
                if key(arr[j]) > pivot:
                    j -= 1
                else:
                    break
            if i <= j:
                arr[i], arr[j] = arr[j], arr[i]
                swaps += 1
                i += 1
                j -= 1
        stack.append((low, j))                   # sort left part
        stack.append((i, high))                  # sort right part
    return arr, comps, swaps


def merge_sort(rows, key):
    comps = 0

    def sort(a):
        nonlocal comps
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left, right = sort(a[:mid]), sort(a[mid:])
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            comps += 1
            if key(left[i]) <= key(right[j]):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        return result + left[i:] + right[j:]

    return sort(rows[:]), comps, 0               # merge sort has no swaps


def hybrid_merge_sort(rows, key):
    """Merge sort, but small pieces (10 or fewer) are sorted with insertion sort."""
    comps = swaps = 0

    def sort(a):
        nonlocal comps, swaps
        if len(a) <= 10:
            a, c, s = insertion_sort(a, key)
            comps += c
            swaps += s
            return a
        mid = len(a) // 2
        left, right = sort(a[:mid]), sort(a[mid:])
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            comps += 1
            if key(left[i]) <= key(right[j]):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        return result + left[i:] + right[j:]

    return sort(rows[:]), comps, swaps


# ---------------- number sorts (no comparing) ----------------

def counting_sort(rows, key):
    values = [key(r) for r in rows]
    check_numbers(values)
    if not rows:
        return [], 0, 0
    low = min(values)
    counts = [0] * (max(values) - low + 1)
    for v in values:                              # count each value
        counts[v - low] += 1
    for i in range(1, len(counts)):               # running total = final position
        counts[i] += counts[i - 1]
    result = [None] * len(rows)
    for k in range(len(rows) - 1, -1, -1):        # go backwards to keep it stable
        v = values[k]
        counts[v - low] -= 1
        result[counts[v - low]] = rows[k]
    return result, 0, 0                           # no comparisons, no swaps


def radix_sort(rows, key):
    check_numbers([key(r) for r in rows])
    arr = rows[:]
    if not arr:
        return arr, 0, 0
    biggest = max(key(r) for r in arr)
    place = 1                                     # 1 = ones, 10 = tens, 100 = hundreds...
    while biggest // place > 0:
        buckets = [[] for _ in range(10)]
        for r in arr:
            buckets[(key(r) // place) % 10].append(r)
        arr = [r for b in buckets for r in b]
        place *= 10
    return arr, 0, 0


def bucket_sort(rows, key):
    values = [key(r) for r in rows]
    check_numbers(values)
    if not rows:
        return [], 0, 0
    low, high = min(values), max(values)
    count = 100                                   # number of buckets
    buckets = [[] for _ in range(count)]
    for r in rows:
        index = (key(r) - low) * (count - 1) // (high - low or 1)
        buckets[index].append(r)
    result = []
    comps = swaps = 0
    for b in buckets:                             # sort each bucket, then join them
        b, c, s = quick_sort(b, key)
        comps += c
        swaps += s
        result += b
    return result, comps, swaps


# name -> (function, time complexity, stable?)
ALGOS = {
    "Bubble Sort":       (bubble_sort,       "O(n²)",                       "Stable"),
    "Selection Sort":    (selection_sort,    "O(n²)",                       "Not stable"),
    "Insertion Sort":    (insertion_sort,    "O(n²)",                       "Stable"),
    "Merge Sort":        (merge_sort,        "O(n log n)",                  "Stable"),
    "Hybrid Merge Sort": (hybrid_merge_sort, "O(n log n)",                  "Stable"),
    "Quick Sort":        (quick_sort,        "O(n log n) avg, O(n²) worst", "Not stable"),
    "Counting Sort":     (counting_sort,     "O(n + k)",                    "Stable"),
    "Radix Sort":        (radix_sort,        "O(d · n)",                    "Stable"),
    "Bucket Sort":       (bucket_sort,       "O(n + k) avg",                "Not stable"),
    "Shell Sort":        (shell_sort,        "O(n²) worst",                 "Not stable"),
    "Gnome Sort":        (gnome_sort,        "O(n²)",                       "Stable"),
}