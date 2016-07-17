def map(fn, lst) {
    res = range(0, size(lst));
    for (i in res) {
        res[i] = fn(lst[i]);
    }
    return res;
}

def square(n) {
    return (n) * n;
}

lst = range(0,100);
print(map(square, lst));