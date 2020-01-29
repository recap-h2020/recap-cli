#!/usr/bin/env python3

import argparse
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from sys import argv, exit

from logger import get_logger
from recap_modules import get_recap_modules
from settings.env import load_env


def print_help(module) -> None:
    module.main(['--help'])


def main():
    load_env()
    log = get_logger(name=__name__)

    recap_modules = get_recap_modules()
    commands = list(recap_modules.keys())
    log.debug(f'Subcommands found: {", ".join(commands)}')

    arg_parser = ArgumentParser(
        prog='recap',
        description='Command Line Interface to RECAP',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    arg_parser.add_argument('command',
                            choices=commands + ['help'])
    arg_parser.add_argument('extra',
                            help=argparse.SUPPRESS,
                            nargs=argparse.REMAINDER)

    args = arg_parser.parse_args(argv[1:])

    if args.command == 'help':
        cmd = args.extra[0] if args.extra else None
        if cmd is None:
            arg_parser.print_help()
            exit(0)
        elif cmd in commands:
            print_help(recap_modules[cmd])
            exit(0)
        else:
            print(f'Available Commands: {", ".join(commands)}')
            exit(1)

    log.debug('Importing module ' + args.command)
    command_args = argv[2:]

    log.debug('Invoking command ' + args.command +
              '.main with args ' + ', '.join(command_args))
    module_main = getattr(recap_modules[args.command], 'main')
    success = module_main(command_args)

    if success:
        exit(0)
    else:
        exit(255)


if __name__ == '__main__':
    main()
