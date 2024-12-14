import sieve
from utils.ci import get_function_name, get_function_uri, get_env_passthrough

@sieve.function(name=get_function_name("test-b"), environment_variables=get_env_passthrough(), python_version="3.10")
def test_b(a: int):
    return sieve.function.get(get_function_uri("test-a")).run(a)
