# -*- coding: utf-8 -*-

from sorting import quick_sort, ALGOS

data = [{"year": 5}, {"year": 2}, {"year": 9}, {"year": 1}]
for name, (func, cx, stable) in ALGOS.items():
    result, comps, swaps = func(data, lambda r: r["year"])
    print(name, [r["year"] for r in result], comps, swaps)