import sieve
from utils.ci import get_function_uri

def test_a():
    assert sieve.function.get(get_function_uri("test-a")).run(3) == 3
