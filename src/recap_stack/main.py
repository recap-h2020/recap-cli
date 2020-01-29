from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os import getenv, environ
from pathlib import Path
from typing import List

from logger import get_logger
from recap_component import main as component_cmd

recap_module_name = 'stack'

log = get_logger(recap_module_name)


def main(argv: List[str]) -> bool:
    services = {
        'admin': getenv('SERVICES_ADMIN').split(','),
        'global': getenv('SERVICES_GLOBAL').split(','),
        'r_infra': getenv('SERVICES_INFRA').split(','),
        'r_user': getenv('SERVICES_USER').split(',')
    }

    stacks = {
        'admin': getenv('STACK_NAME_ADMIN'),
        'global': getenv('STACK_NAME_GLOBAL'),
        'r_infra': getenv('STACK_NAME_INFRA'),
        'r_user': getenv('STACK_NAME_USER')
    }

    docker_compose_files = {
        'admin': getenv('DOCKER_COMPOSE_FILE_ADMIN'),
        'global': getenv('DOCKER_COMPOSE_FILE_GLOBAL'),
        'r_infra': getenv('DOCKER_COMPOSE_FILE_INFRA'),
        'r_user': getenv('DOCKER_COMPOSE_FILE_USER')
    }

    rancher_compose_files = {
        'admin': getenv('RANCHER_COMPOSE_FILE_ADMIN'),
        'global': getenv('RANCHER_COMPOSE_FILE_GLOBAL'),
        'r_infra': getenv('RANCHER_COMPOSE_FILE_INFRA'),
        'r_user': getenv('RANCHER_COMPOSE_FILE_USER')
    }

    arg_parser = ArgumentParser(
        prog=recap_module_name,
        description='Manage Complete RECAP Stacks on Running Sites',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    arg_parser.add_argument('action', choices=['up', 'down', 'delete', 'restart'])
    arg_parser.add_argument('site')
    arg_parser.add_argument('--logstash-config-image',
                            default=getenv('LOGSTASH_CONFIG_IMAGE'),
                            help=('Logstash Config Sidekick Container, '
                                  f'default {getenv("LOGSTASH_CONFIG_IMAGE")}'))
    arg_parser.add_argument('--dashboard-config-image',
                            default=getenv('DASHBOARD_CONFIG_IMAGE'),
                            help=('Dashboard Config Sidekick Container, '
                                  f'default {getenv("DASHBOARD_CONFIG_IMAGE")}'))
    arg_parser.add_argument('--infrastructures',
                            nargs='*',
                            default=['r_infra', 'r_user'],
                            help=('Any set of '
                                  '[r_infra, r_user, global, admin] ')
                            )
    arg_parser.add_argument('--services', nargs='*')

    args = arg_parser.parse_args(argv)

    environ['LOGSTASH_CONFIG_IMAGE'] = args.logstash_config_image
    environ['DASHBOARD_CONFIG_IMAGE'] = args.dashboard_config_image

    success = True
    for infra in args.infrastructures:
        log.info('Spinning up ' + infra + ' at ' + args.site)

        stack = stacks[infra].replace('%site%', args.site)

        file_path = Path(__file__).resolve().parent
        docker_compose_file = f'{file_path}/compose/{docker_compose_files[infra]}'
        rancher_compose_file = f'{file_path}/compose/{rancher_compose_files[infra]}'

        srv = args.services or services[infra]

        component_args = [
                             args.action,
                             '--site', args.site,
                             '--infrastructure', infra,
                             '--stack', stack,
                             '--docker-compose-file', docker_compose_file,
                             '--rancher-compose-file', rancher_compose_file,
                             '--services'
                         ] + srv

        success &= component_cmd(component_args)

    return success


if __name__ == '__main__':
    from settings.env import load_env

    load_env()
    main([
        'up',
        '0_Cloud',
        '--infrastructures', 'r_infra', 'r_user', 'admin', 'global'
    ])
    pass
