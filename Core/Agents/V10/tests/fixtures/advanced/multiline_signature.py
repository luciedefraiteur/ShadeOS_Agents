# multiline signature

def f(
    a: int,
    b: str = "x",
    *args,
    **kwargs,
) -> int:
    # comment
    if a:
        return 1
    return 0
