import re
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, ArgumentTypeError
from os import getenv
from pathlib import Path
from typing import List, Optional, Dict

from ansible_runner import AnsibleRunner
from logger import get_logger
from recap_host import main as add_agent
from recap_host.main import labels_type, get_labels_string
from recap_init import main as init_rancher
from recap_virtualenv.json_loader import VenvJsonLoader
from recap_virtualenv.landscaper import update as update_landscaper
from settings.env import load_env
from recap_env import main as env


recap_module_name = 'venv'

log = get_logger(name=recap_module_name)


def network_address(s) -> str:
    pat = re.compile(
        r'^([0-9]{1,3}\.){3}[0-9]{1,3}/([0-9]|[1-2][0-9]|3[0-2])$')
    if not pat.match(s):
        raise ArgumentTypeError(
            f'"{s}" is not a valid IPv4 CIDR address. Example: "192.168.0.0/24"'
        )
    return s


def ip_address(s) -> str:
    pat = re.compile(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$')
    if not pat.match(s):
        raise ArgumentTypeError(
            f'"{s}" is not a valid IPv4 address. Example: "192.168.0.1"'
        )
    return s


def main(argv: List[str]) -> bool:
    arg_parser = ArgumentParser(
        prog=recap_module_name,
        description='Manage Virtual RECAP Infrastructure on OpenStack',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    arg_parser.add_argument('action', choices=[
        'add-site',
        'init-master',
        'add-host',
        'connect-sites',
        'from-json'
    ])

    # optionals for 'add-site'
    arg_parser.add_argument('--name', required=False)
    arg_parser.add_argument('--network', required=False, type=network_address)
    arg_parser.add_argument('--router-ip', required=False, type=ip_address)

    # optional for 'connect-sites'
    arg_parser.add_argument(
        '--inter-network', required=False, type=network_address)
    arg_parser.add_argument('--inter-ports', nargs='*', type=ip_address)
    arg_parser.add_argument('--sites', nargs='*')
    arg_parser.add_argument('--site-networks', nargs='*', type=network_address)

    # optionals for 'init-master', 'add-host'
    arg_parser.add_argument('--on-site', required=False)
    arg_parser.add_argument('--type', required=False)
    arg_parser.add_argument('--instance', required=False)
    arg_parser.add_argument('--public-key-file', required=False)
    arg_parser.add_argument('--private-key-file', required=False)
    arg_parser.add_argument('--vm-flavour', required=False, default='medium')
    arg_parser.add_argument('--vm-availability-zone',
                            required=False, default='blade')
    arg_parser.add_argument('--extra-labels', required=False, type=labels_type)
    arg_parser.add_argument('--is-master', action='store_true')
    arg_parser.add_argument('--rancher-sites', nargs='*')

    # optionals for 'from-json'
    arg_parser.add_argument('--file', required=False)

    args = arg_parser.parse_args(argv)

    file_path = Path(__file__).resolve().parent
    playbook_path = f'{file_path}/playbooks'

    if args.action == 'add-site':
        if args.name is None:
            arg_parser.error('--name is required with add-site')
        if args.network is None:
            arg_parser.error('--network is required with add-site')
        if args.router_ip is None:
            arg_parser.error('--router-ip is required with add-site')

        return add_site(playbook_path=playbook_path,
                        name=args.name,
                        network=args.network,
                        router_ip=args.router_ip)

    if args.action == 'init-master':

        if args.on_site is None:
            arg_parser.error('--on-site is required with init-master')
        if args.public_key_file is None:
            arg_parser.error('--public-key-file is required with init-master')
        if args.private_key_file is None:
            arg_parser.error('--private-key-file is required with init-master')

        return init_master(playbook_path=playbook_path,
                           site=args.on_site,
                           public_key=args.public_key_file,
                           private_key=args.private_key_file,
                           rancher_sites=args.rancher_sites)

    if args.action == 'add-host':
        if args.type is None:
            arg_parser.error('--type is required with add-host')
        if args.on_site is None:
            arg_parser.error('--on-site is required with add-host')
        if args.instance is None:
            arg_parser.error('--instance is required with add-host')
        if args.public_key_file is None:
            arg_parser.error('--public-key-file is required with add-host')
        if args.private_key_file is None:
            arg_parser.error('--private-key-file is required with add-host')

        return add_host(playbook_path=playbook_path,
                        site=args.on_site,
                        host_type=args.type,
                        instance=args.instance,
                        public_key=args.public_key_file,
                        private_key=args.private_key_file,
                        vm_flavour=args.vm_flavour,
                        vm_availability_zone=args.vm_availability_zone,
                        extra_labels=args.extra_labels or {},
                        is_master=args.is_master)

    if args.action == 'connect-sites':
        if not args.sites:
            arg_parser.error('--sites are required with connect-sites')
        elif not len(args.sites) == 2:
            arg_parser.error('you must specify exactly 2 --sites')

        if not args.inter_network:
            arg_parser.error('--inter-network is required with connect-sites')

        if not args.inter_ports:
            arg_parser.error('--inter-ports are required with connect-sites')
        elif not len(args.inter_ports) == 2:
            arg_parser.error('you must specify exactly 2 --inter-ports')

        if not args.site_networks:
            arg_parser.error('--site-networks are required with connect-sites')
        elif not len(args.site_networks) == 2:
            arg_parser.error('you must specify exactly 2 --site-networks')

        return connect_sites(
            playbook_path=playbook_path,
            inter_network=args.inter_network,
            inter_ports=args.inter_ports,
            sites=args.sites,
            site_addresses=args.site_networks,
            name=args.sites[1],
            network=args.site_networks[1],
            router_ip=args.router_ip
        )

    if args.action == 'from-json':
        if not args.file:
            arg_parser.error('--file is required with from-json')
        json_loader = VenvJsonLoader(args.file, main)
        return json_loader.setup()

    return False


def add_site(playbook_path: str,
             name: str,
             network: str,
             router_ip: str) -> bool:
    ar = AnsibleRunner()

    network_name = _get_internal_network_name(name)
    subnet_name = _get_internal_subnet_name(name)
    router_name = _get_internal_router_name(name)

    return ar.play(
        playbook=f'{playbook_path}/add_site.yml',
        extra_vars={
            'NETWORK_NAME': network_name,
            'SUBNET_NAME': subnet_name,
            'NETWORK_ADDRESS': network,
            'ROUTER_NAME': router_name,
            'ROUTER_IP': router_ip
        }
    )


def init_master(playbook_path: str,
                site: str,
                public_key: str,
                private_key: str,
                rancher_sites: List[str]) -> bool:
    ar = AnsibleRunner()

    vm_name = _get_rancher_master_vm_name(site)
    network_name = _get_internal_network_name(site)
    router_name = _get_internal_router_name(site)

    host_available = ar.play(
        playbook=f'{playbook_path}/init_master.yml',
        extra_vars={
            'VM_NAME': vm_name,
            'NETWORK_NAME': network_name,
            'ROUTER_NAME': router_name,
            'SITE_NAME': site,
            'PUBLIC_KEY_FILE': public_key,
            'PRIVATE_KEY_FILE': private_key
        }
    )

    if not host_available:
        return False

    host_vars = ar.inventory_manager.get_host(vm_name).get_vars()
    host = host_vars.get('ansible_host')
    python_interpreter = host_vars.get('ansible_python_interpreter')
    username = host_vars.get('ansible_user')

    print(rancher_sites)
    return init_rancher([
        '--host', host,
        '--username', username,
        '--private-key-file', private_key,
        '--python-interpreter', python_interpreter,
        '--pip-executable', '/home/core/bin/pip',
        '--pip-as-non-root',
        '--update-config',
        '--rancher-username', 'recap',
        '--rancher-password', 'recap$123',
        '--rancher-env-name', 'recap',
        '--rancher-registry-url', 'omi-registry.e-technik.uni-ulm.de',
        '--rancher-registry-username', 'recap_pipeline',
        '--rancher-registry-password', '53qThb2ZDUaXc3L49bs8',
        '--rancher-sites', *rancher_sites
    ])


def add_host(playbook_path: str,
             site: str,
             host_type: str,
             instance: int,
             public_key: str,
             private_key: str,
             vm_flavour: str,
             vm_availability_zone: str,
             extra_labels: Dict[str, str],
             is_master: bool = False) -> bool:
    ar = AnsibleRunner()

    vm_name = _get_host_vm_name(site, host_type, instance)
    network_name = _get_internal_network_name(site)
    master_host = _get_master_address()

    if "global" == host_type:
        current_playbook = f'{playbook_path}/add_host_fip.yml'

    else:
        current_playbook = f'{playbook_path}/add_host.yml'

    host_available = ar.play(
        playbook=current_playbook,
        extra_vars={
            'VM_NAME': vm_name,
            'NETWORK_NAME': network_name,
            'SITE_NAME': site,
            'TYPE': host_type,
            'MASTER_HOST': master_host,
            'PUBLIC_KEY_FILE': public_key,
            'PRIVATE_KEY_FILE': private_key,
            'VM_FLAVOUR': vm_flavour,
            'VM_AZ': vm_availability_zone
        }
    )

    if not host_available:
        return False

    host_vars = ar.inventory_manager.get_host(vm_name).get_vars()
    host = host_vars.get('ansible_host')
    python_interpreter = host_vars.get('ansible_python_interpreter')
    username = host_vars.get('ansible_user')

    if is_master:
        extra_labels['master'] = 'true'
    
    if "global" == host_type:
        env(['set', "GLOBAL_ADDRESS", host])

    agent_added = add_agent([
        'add', host,
        '--infrastructure', host_type,
        '--site', site,
        '--username', username,
        '--private-key-file', private_key,
        '--start-stack',
        '--python-interpreter', python_interpreter,
        '--pip-executable', '/home/core/bin/pip',
        '--pip-as-non-root',
        '--proxy-host', master_host,
        '--extra-labels', get_labels_string(extra_labels) or None
    ])

    services = {
        'admin': getenv('SERVICES_ADMIN').split(','),
        'global': getenv('SERVICES_GLOBAL').split(','),
        'r_infra': getenv('SERVICES_INFRA').split(','),
        'r_user': getenv('SERVICES_USER').split(',')
    }

    # if agent_added and host_type == 'r_user':
    #     result = update_landscaper(site=site,
    #                                restart_service=True,
    #                                ssh_user=username,
    #                                private_key=private_key,
    #                                python_interpreter=python_interpreter,
    #                                ssh_common_args='-o StrictHostKeyChecking=no')
    #     if not result:
    #         log.warning('There was an error updating the landscaper')

    return agent_added


def connect_sites(playbook_path: str,
                  inter_network: str,
                  inter_ports: List[str],
                  sites: List[str],
                  site_addresses: List[str],
                  name: str,
                  network: str,
                  router_ip: str) -> bool:
    p2p_network_name = _get_p2p_network_name(sites)
    p2p_subnet_name = _get_p2p_subnet_name(sites)

    network_name = _get_internal_network_name(name)
    subnet_name = _get_internal_subnet_name(name)
    router_name = _get_internal_router_name(name)

    site_routers = [_get_internal_router_name(s) for s in sites]

    ar = AnsibleRunner()

    print("network_name: " + network_name)
    print("subnet_name: " + subnet_name)
    print("network: " + network)
    print("router_name: " + router_name)
    print("router_ip: " + router_ip)
    return ar.play(
        playbook=f'{playbook_path}/connect_sites.yml',
        extra_vars={
            'INTER_NETWORK_NAME': p2p_network_name,
            'INTER_SUBNET_NAME': p2p_subnet_name,
            'INTER_NETWORK_ADDRESS': inter_network,
            'SITES': [
                {
                    'INTER_PORT': inter_ports[0],
                    'ROUTER_NAME': site_routers[0],
                    'OTHER_NETWORK_ADDRESS': site_addresses[1],
                    'OTHER_PORT': inter_ports[1]
                },
                {
                    'INTER_PORT': inter_ports[1],
                    'ROUTER_NAME': site_routers[1],
                    'OTHER_NETWORK_ADDRESS': site_addresses[0],
                    'OTHER_PORT': inter_ports[0]
                }
            ],
            'NETWORK_NAME': network_name,
            'SUBNET_NAME': subnet_name,
            'NETWORK_ADDRESS': network,
            'ROUTER_NAME': router_name,
            'ROUTER_IP': router_ip
        }
    )

def _get_master_address() -> Optional[str]:
    rancher_url = getenv('RANCHER_URL')
    matches = re.findall(r'[0-9]+(?:\.[0-9]+){3}', rancher_url)
    if not matches:
        return None
    else:
        return matches[0]


def _get_rancher_master_vm_name(site_name: str) -> str:
    return f'site-{site_name}_rancher-server'


def _get_host_vm_name(site_name: str, host_type: str, instance: int) -> str:
    return f'site-{site_name}_{host_type}_instance-{instance}'


def _get_internal_network_name(site_name: str) -> str:
    return f'site-{site_name}_internal-network'


def _get_internal_subnet_name(site_name: str) -> str:
    return f'site-{site_name}_internal-subnet'


def _get_internal_router_name(site_name: str) -> str:
    return f'site-{site_name}_internal-router'


def _get_p2p_network_name(sites: List[str]) -> str:
    return f'{"-".join(sites)}_p2p-network'


def _get_p2p_subnet_name(sites: List[str]) -> str:
    return f'{"-".join(sites)}_p2p-subnet'


if __name__ == '__main__':
    load_env()

    main([
        'from-json',
        '--file', '/opt/app/cli/recap_virtualenv/example_env.json'
    ])

    # a = [
    #     'add-site',
    #     '--name', 'test_A',
    #     '--network', '192.168.0.0/24',
    #     '--router-ip', '192.168.0.1'
    # ]
    # main(a)

    # b = [
    #     'add-site',
    #     '--name', 'test_B',
    #     '--network', '192.168.1.0/24',
    #     '--router-ip', '192.168.1.1'
    # ]
    # main(b)

    # c = [
    #     'connect-sites',
    #     '--inter-network', '192.168.10.0/24',
    #     '--inter-ports', '192.168.10.10', '192.168.10.20',
    #     '--sites', 'test_A', 'test_B',
    #     '--site-networks', '192.168.0.0/24', '192.168.1.0/24'
    # ]
    # main(c)

    # b = ['init-master',
    #      '--on-site', 'test_A',
    #      '--public-key-file', '/opt/project/src/cli/recap_virtualenv/keys/cloud_key.public',
    #      '--private-key-file', '/opt/project/src/cli/recap_virtualenv/keys/cloud_key.pem'
    #      ]
    # main(b)

    # c = [
    #     'add-host',
    #     '--type', 'r_infra',
    #     '--on-site', 'test_A',
    #     '--instance', 0,
    #     '--public-key-file', '/opt/project/src/cli/recap_virtualenv/keys/cloud_key.public',
    #     '--private-key-file', '/opt/project/src/cli/recap_virtualenv/keys/cloud_key.pem'
    # ]
    # main(c)

    # d = [
    #     'add-host',
    #     '--type', 'r_infra',
    #     '--on-site', 'test_B',
    #     '--instance', 0,
    #     '--public-key-file', '/opt/project/src/cli/recap_virtualenv/keys/cloud_key.public',
    #     '--private-key-file', '/opt/project/src/cli/recap_virtualenv/keys/cloud_key.pem',
    #     '--extra-labels', 'label1=test1,label2=test2'
    # ]
    # main(d)

    # b = [
    #     'add-site',
    #     '--name', 'test_C',
    #     '--network', '192.168.2.0/24',
    #     '--router-ip', '192.168.2.1'
    # ]

    # main(b)
    # c = [
    #     'connect-sites',
    #     '--inter-network', '192.168.20.0/24',
    #     '--inter-ports', '192.168.20.10', '192.168.20.20',
    #     '--sites', 'test_A', 'test_C',
    #     '--site-networks', '192.168.0.0/24', '192.168.2.0/24'
    # ]
    # main(c)

    # d = [
    #     'add-host',
    #     '--type', 'r_user',
    #     '--on-site', 'test_C',
    #     '--instance', 0,
    #     '--public-key-file', '/opt/project/src/cli/recap_virtualenv/keys/cloud_key.public',
    #     '--private-key-file', '/opt/project/src/cli/recap_virtualenv/keys/cloud_key.pem',
    # ]
    # main(d)
