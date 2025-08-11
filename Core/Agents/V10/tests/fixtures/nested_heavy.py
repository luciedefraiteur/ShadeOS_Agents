# Nested heavy fixture

def outer(a, b):
    total = 0
    def inner(x):
        res = []
        for i in range(x):
            if i % 2 == 0:
                res.append(i)
            else:
                res.append(-i)
        return sum(res)
    total += inner(a)
    total += inner(b)
    return total
