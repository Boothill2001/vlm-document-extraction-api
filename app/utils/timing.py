import time
from contextlib import contextmanager


@contextmanager
def timer():
    result = {"ms": 0.0}
    start = time.perf_counter()
    yield result
    result["ms"] = round((time.perf_counter() - start) * 1000, 2)
