import sieve
from utils.ci import get_function_uri

def test_b():
    assert sieve.function.get(get_function_uri("test-b")).run(3) == 3
