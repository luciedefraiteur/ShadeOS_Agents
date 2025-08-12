# Big comprehensive fixture for scope detection
# Covers decorators, multi-line signatures, docstrings, nested classes/functions,
# dense control flow, continuations, f-strings, async+match, and corruption edges.

# Imports and comments
import os
import sys


class Alpha:
    # MARK: DECORATORS_DECOR1
    @d1
    @d2(k=1)
    @staticmethod
    # MARK: DECORATORS_HEADER
    def decorated(a):
        """Doc for decorated method"""
        # MARK: DECORATORS_BODY
        return a

    # MARK: MULTISIG_HEADER
    def multi_sig(
        self,
        a: int,
        b: str = "x",
        *args,
        # MARK: MULTISIG_MID
        **kwargs,
    ) -> int:
        """Multi-line signature with a docstring"""
        # MARK: MULTISIG_BODY
        if a:
            return 1
        return 0

    class Inner:
        # MARK: INNER_HEADER
        def inner_func(self):
            def nested(x):
                return x * 2
            # MARK: INNER_BODY
            return nested(3)


# MARK: BETA_HEADER
def beta(x):
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
    # MARK: BETA_BODY
    return y


# MARK: GAMMA_HEADER
def gamma():
    value = (
        1
        + 2
    )
    s = f"sum={value}"
    # MARK: GAMMA_BODY
    return s


# MARK: DELTA_HEADER
async def delta(x):
    match x:
        case 0:
            return 0
        case _:
            # MARK: DELTA_BODY
            return 1


# MARK: BAD_STRING_HEADER
def bad_string():
    # Unterminated string to test tokenizer/AST notes
    s = "oops
    # MARK: BAD_STRING_BODY
    return 1


# MARK: EOF_FUNC_HEADER
def near_eof():
    # Unterminated scope at EOF (no dedent)
    y = 2
