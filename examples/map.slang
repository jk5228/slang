def map(fn, lst) {
    res = {};
    for (i in range(0, size(lst))) {
        res[i] = fn(lst[i]);
    }
    return res;
}

def square(n) {
    return (n) * n;
}

lst = {1, 2, 3};
print(map(fn, lst));