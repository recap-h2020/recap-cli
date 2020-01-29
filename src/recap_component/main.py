import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import List

from logger import get_logger
from rancher_api import RancherCompose

recap_module_name = 'component'

log = get_logger(recap_module_name)


def set_unique_site_mapping(site: str) -> None:
    if site == '0_Cloud':  # TODO: make me configurable
        unique_site_mapping = 12727
    else:
        shift = 64 if len(site) == 1 else 6464
        unique_site_mapping = ord(site[:1]) - shift + 10000
    os.environ['UNIQUE_SITE_MAPPING'] = str(unique_site_mapping)


def main(argv: List[str]) -> bool:
    arg_parser = ArgumentParser(
        prog=recap_module_name,
        description='Atomically Manage RECAP Components via Rancher',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    arg_parser.add_argument(
        'action', choices=['up', 'down', 'delete', 'restart'])
    arg_parser.add_argument('--site', required=True)
    arg_parser.add_argument('--infrastructure', required=True)
    arg_parser.add_argument('--stack', required=True)
    arg_parser.add_argument('--docker-compose-file', required=True)
    arg_parser.add_argument('--rancher-compose-file', required=True)
    arg_parser.add_argument('--services', nargs='+', required=True)
    args = arg_parser.parse_args(argv)

    rancher_access_key = os.getenv('RANCHER_ACCESS_KEY_'+args.site)
    rancher_secret_key = os.getenv('RANCHER_SECRET_KEY_'+args.site)

    rancher = RancherCompose(rancher_url=os.getenv('RANCHER_URL'),
                             rancher_access_key=rancher_access_key,
                             rancher_secret_key=rancher_secret_key,
                             site=args.site,
                             infrastructure=args.infrastructure)
    # set env variable for influx' port mapping
    # used by its' docker-compose.yml file
    if 'influxdb' in args.services:
        set_unique_site_mapping(args.site)

    if args.action == 'up':
        return rancher.up(stack=args.stack,
                          services=args.services,
                          docker_compose_file=args.docker_compose_file,
                          rancher_compose_file=args.rancher_compose_file)
    elif args.action == 'down':
        return rancher.down(stack=args.stack,
                            services=args.services,
                            docker_compose_file=args.docker_compose_file,
                            rancher_compose_file=args.rancher_compose_file)
    elif args.action == 'delete':
        return rancher.delete(stack=args.stack,
                              services=args.services,
                              docker_compose_file=args.docker_compose_file,
                              rancher_compose_file=args.rancher_compose_file)
    elif args.action == 'restart':
        return rancher.restart(stack=args.stack,
                               services=args.services,
                               docker_compose_file=args.docker_compose_file,
                               rancher_compose_file=args.rancher_compose_file)
