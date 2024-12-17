import sieve
import time
from utils.ci import get_function_name, get_env_passthrough

@sieve.function(name=get_function_name("test-group-b"), python_version="3.10", environment_variables=get_env_passthrough())
def test_a(a: int):
    time.sleep(a)
    return a


