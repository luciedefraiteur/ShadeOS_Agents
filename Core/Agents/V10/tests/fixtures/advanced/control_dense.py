# control dense

def h(x):
    if x < 0:
        return -1
    elif x == 0:
        y = 0
    else:
        try:
            y = x
        except Exception:
            y = 0
        finally:
            y += 1
    return y
