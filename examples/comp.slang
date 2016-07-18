arr = (0..100);
print({e in arr : e % 2 == 0 });
print({e in arr : e % 5 == 0 });
print({e in arr : e >= 50 });
print({e in arr : e >= 50 && (e <= 60) });
print({e in arr : e % 10 == 0 -> print(e) });