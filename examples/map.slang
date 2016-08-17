def map(fn, lst) {
    res = 0...size(lst);
    for (i in res) {
        res[i] = fn(lst[i]);
    }
    return res;
}

def square(n) {
    return n*n;
}

print(map(square, 0..100));

# Or equivalently...
print({ n in 0..100 : 1 -> n*n });