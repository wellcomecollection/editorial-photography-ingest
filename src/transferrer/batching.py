import itertools


def batch_by_total(entries, maximum, key):
    """
    Given an iterable of entries, return them in groups where their total value does not exceed a `maximum`
    The value of each is derived using `key`, in this case, the identity function:
    >>> list(batch_by_total(range(11), 10, lambda o: o))
    [[0, 1, 2, 3, 4], [5], [6], [7], [8], [9], [10]]

    But you may derive the value however you wish.

    >>> list(batch_by_total([('a',1),('b',2),('c',3),('d',4),('e',5), ('f',4), ('g',3)], 10, lambda o: o[1]))
    [[('a', 1), ('b', 2), ('c', 3), ('d', 4)], [('e', 5), ('f', 4)], [('g', 3)]]

    This function iterates over the provided entries in order.  It does not attempt to create an optimal packing
    In this case, the values are the same as the first example in reverse.  The resulting groups are different.

    >>> list(batch_by_total(range(10, 0, -1), 10, lambda o: o))
    [[10], [9], [8], [7], [6], [5, 4], [3, 2, 1]]

    If any entry is, on its own, larger than maximum, then it will be returned in its own group,
    it is the caller's responisbility to work out how to deal with that.
    >>> list(batch_by_total(range(11), 6, lambda o: o))
    [[0, 1, 2, 3], [4], [5], [6], [7], [8], [9], [10]]
    """

    def accumulator_max(previous, entry):
        value = key(entry)
        running_total = previous[1]
        group = previous[2]
        if running_total + value > maximum:
            return entry, value, group + 1
        else:
            return entry, running_total + value, group

    # just in case entries is a list, create a new iterator for it.
    iter_entries = iter(entries)
    # Because we are using key to derive the value, we need to initialise the accumulator with the first value
    # otherwise it will just use the first entry on its own.
    first = next(iter_entries)
    accumulated = itertools.accumulate(iter_entries, accumulator_max, initial=(first, key(first), 0))

    return ([entry[0] for entry in g] for _, g in itertools.groupby(accumulated, lambda entry: entry[2]))
