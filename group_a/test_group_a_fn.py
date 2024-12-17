import sieve
from utils.ci import get_function_uri

def test_group_a():
    assert sieve.function.get(get_function_uri("test-group-a")).run(3) == 3
