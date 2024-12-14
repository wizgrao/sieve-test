import sieve
import time
from utils.ci import get_function_name, get_function_uri
import os

@sieve.function(name=get_function_name("test-b"), environment_variables=[sieve.Env(name="SIEVE_TEST_ENV", description="test environment", default=os.getenv("SIEVE_TEST_ENV") or "")])
def test_b(a: int):
    return sieve.function.get(get_function_uri("test-a")).run(a)
