import sieve
import time
from utils.ci import get_function_name, get_function_uri

@sieve.function(name=get_function_name("test-a"), python_version="3.10")
def test_a(a: int):
    time.sleep(a)
    return a


