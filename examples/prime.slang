# Compute factors and prime factors of numbers.
def factors(n) {
    res = {i in 0..30 : 1 -> 0};
    cnt = 0;
    for (i in 1..n) {
        if (n % i == 0) {
            res[cnt] = i;
            cnt = (cnt + 1);
        } else {
        }
    }
    return {i in res : i -> i};
}

def prime(n) {
    return size(factors(n)) == 2;
}


def primeFactors(n) {
    return { e in factors(n) : prime(e) };
}

primes = { n in 1..100 : prime(n) };
print(primes);

for (i in 1..100) {
    print(primeFactors(i));
}