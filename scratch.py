import time


def run():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    return a + b + c + d + e + f


def bench():
    start = time.time()
    sum = 0
    for i in range(1000):
        sum = sum + run()
    return time.time() - start


bench()

total = 0
for i in range(100):
    total = total + bench()

print(total)
