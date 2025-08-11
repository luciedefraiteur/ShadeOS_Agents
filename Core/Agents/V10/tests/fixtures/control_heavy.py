# Control heavy fixture

def compute(x):
    if x < 0:
        return -1
    elif x == 0:
        y = 1
    else:
        try:
            y = x * 2
        except Exception:
            y = 0
        finally:
            y += 1
    return y
