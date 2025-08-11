# Decorated + docstring fixture

class Service:
    @staticmethod
    def ping(x: int) -> int:
        """Ping method
        Returns the same value.
        """
        if x < 0:
            return 0
        return x
