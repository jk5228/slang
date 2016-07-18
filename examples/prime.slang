def factors(n) {
    res = range(0,30);
    cnt = 0;
    for (i in range(1,n+1)) {
        if (n % i == 0) {
            res[cnt] = i;
            cnt = cnt + 1;
        } else {
        }
    }
    len = 0;
    for (i in res) {
        if (i)
    }
    return res;
}

def prime(n) {
    return size(factors(n)) == 2;
}

primes = { n in range(1,100) : prime(n) };

print(primes);

def primeFactors(n) {
    return { e in factors(n) : prime(e) };
}

for (i in range(0,100)) {
    print(primeFactors(i));
}