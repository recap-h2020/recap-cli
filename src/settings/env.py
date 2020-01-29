from os import environ
from typing import Dict

from dotenv import load_dotenv, find_dotenv, set_key, dotenv_values

env_file = find_dotenv()


def load_env() -> bool:
    return load_dotenv(env_file)


def set_env(key: str, val: str) -> bool:
    (result, key, val) = set_key(env_file, key, val)
    environ[key] = val
    return result


def get_env(key) -> str:
    return get_envs().get(key)


def get_envs() -> Dict[str, str]:
    return dotenv_values(env_file)
