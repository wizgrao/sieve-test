import yaml
import typer
from pydantic import BaseModel, Field
from typing import Annotated, List, Set
import subprocess
import os
import sieve

class SieveFunction(BaseModel):
    path: str
    depends_on: List[str] = Field(alias="depends-on", default=[])

class SieveConfig(BaseModel):
    functions: dict[str, SieveFunction]

class InvertedFunction(BaseModel):
    name: str
    depended_by: List[str]


def invert_config(cfg: SieveConfig) -> dict[str, InvertedFunction]:
    ret: dict[str, InvertedFunction] = {}
    for fn_name in cfg.functions.keys(): 
        ret[fn_name] = InvertedFunction(name=fn_name, depended_by=[])
    for fn_name, fn in cfg.functions.items():
        for dependency in fn.depends_on:
            ret[dependency].depended_by.append(fn_name)
    return ret

def deploy_function(fn: SieveFunction):
    p = subprocess.Popen(["sieve", "deploy"], cwd=fn.path)
    if p.wait() != 0:
        raise Exception("deploy failed")

def test_functions(fns: List[SieveFunction]):
    fn_paths = [fn.path for fn in fns]
    p = subprocess.Popen(["pytest", "-n", "40", "-vv"] + fn_paths)
    if p.wait() != 0:
        raise Exception("tests failed")

def extend_test_list(cfg: SieveConfig, function_list: List[str]) -> List[str]:
    visited: Set[str] = set()
    inverted_config = invert_config(cfg)
    def visit(s: str):
        if s in visited:
            return
        visited.add(s)
        for child in inverted_config[s].depended_by:
            visit(child)
    for fn in function_list:
        visit(fn)

    return list(visited)

def extend_deploy_list(cfg: SieveConfig, function_list: List[str]) -> List[str]:
    visited: Set[str] = set()
    def visit(s: str):
        if s in visited:
            return
        visited.add(s)
        for child in cfg.functions[s].depends_on:
            visit(child)

    for fn in function_list:
        visit(fn)

    return list(visited)

def get_test_env() -> str:
    return os.getenv("SIEVE_TEST_ENV") or ""

def is_test_env() -> bool:
    return len(get_test_env()) > 0

def get_function_name(name: str):
    if not is_test_env():
        return name
    return name + "-" + get_test_env()

def get_function_uri(name: str, org:str= "", version: str=""):
    if org == "" or is_test_env():
        org = os.getenv("ORGANIZATION_NAME") or ""
    fn_name = get_function_name(name)
    if is_test_env() or len(version) == 0:
        return f"{org}/{fn_name}"
    return f"{org}/{fn_name}:{version}"

def get_env_passthrough():
    if not is_test_env():
        return []
    return sieve.Env(name="SIEVE_TEST_ENV", description="test environment", default=os.getenv("SIEVE_TEST_ENV") or ""), sieve.Env(name="ORGANIZATION_NAME", description="test environment", default=os.getenv("ORGANIZATION_NAME") or "")

def main(functions: Annotated[List[str], typer.Argument()], config: str="sieve-config.yml", test_env: bool=False):
    with open(config, 'r') as config_file:
        config_yaml = yaml.safe_load(config_file)
        sieve_config = SieveConfig(**config_yaml)
        print(sieve_config)

        if 'all' in functions or 'utils' in functions:
            functions = list(sieve_config.functions.keys())

        deploy_fns = functions
        functions = extend_test_list(sieve_config, functions)
        if test_env:
            deploy_fns = extend_deploy_list(sieve_config, functions)
        for fn in deploy_fns:
            deploy_function(sieve_config.functions[fn])

        test_functions([sieve_config.functions[fn] for fn in functions])


if __name__ == "__main__":
    typer.run(main)
