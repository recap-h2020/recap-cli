from argparse import ArgumentParser
from typing import List, Dict

from settings.env import get_envs, set_env

recap_module_name = 'env'


def main(argv: List[str]) -> bool:
    arg_parser = ArgumentParser(
        description='List and Persistently Modify Environment Variables'
    )
    arg_parser.add_argument('action', choices=['list', 'get', 'set'])
    arg_parser.add_argument('key', nargs='?')
    arg_parser.add_argument('value', nargs='?')
    args = arg_parser.parse_args(argv)

    if args.action == 'get' and args.key is None:
        arg_parser.error('get requires key')
    elif args.action == 'set' and (args.key is None or args.value is None):
        arg_parser.error('set requires key and value')

    if args.action == 'list':
        _list(get_envs())
        return True
    elif args.action == 'get':
        envs = get_envs()
        if args.key in envs:
            env = {args.key: envs[args.key]}
            _list(env)
            return True
        else:
            return False
    elif args.action == 'set':
        return _set(args.key, args.value)


def _list(envs: Dict[str, str]) -> None:
    for (k, v) in envs.items():
        print(f'{k}={v}')


def _set(key: str, val: str) -> bool:
    return set_env(key, val)
