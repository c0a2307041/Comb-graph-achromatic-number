def remainder(n):
    nC2 = n * (n - 1) // 2
    m = (nC2 + 1) // 2
    if nC2 % 2 == 0:
        m+=1
        remainder = m % n
        print(f"偶数n = {n}, q = {remainder}")
    else:
        remainder = m % n
        print(f"奇数n = {n}, q = {remainder}")

for N_VALUE in range(1, 201):
    remainder(N_VALUE)