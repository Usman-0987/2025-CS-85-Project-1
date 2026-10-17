# -*- coding: utf-8 -*-

from searching import linear_search, binary_search, composite_search

data = [
    {"title": "War and Peace", "year": 1869},
    {"title": "The War of the Worlds", "year": 1898},
    {"title": "Peace Talks", "year": 2020},
]
print(len(linear_search(data, ("title", "contains", "war"))))                      # expect 2
print(len(binary_search(data, "year", "1898")))                                    # expect 1
print(len(composite_search(data, ("title", "contains", "war"), "AND",
                           ("year", "equals", "1898"))))                           # expect 1