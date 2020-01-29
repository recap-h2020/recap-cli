from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path
from typing import List, Dict, Optional
import os

from ansible_runner import AnsibleRunner, Host
from logger import get_logger
from rancher_api import RancherClient
from recap_stack import main as stack_cmd

recap_module_name = 'host'

log = get_logger(recap_module_name)

_file_path = Path(__file__).resolve().parent
_playbook_path = f'{_file_path}/playbooks'


def labels_type(s: str) -> Optional[Dict[str, str]]:
    if s is None:
        return None

    result = {}
    pairs = s.split(',')
    for pair in pairs:
        label = pair.split('=')
        result[label[0]] = label[1]
    return result


def get_labels_string(labels: Dict[str, str]) -> str:
    result = ''
    for k, v in labels.items():
        result += f'&{k}={v}'
    return result


def main(argv: List[str]) -> bool:
    arg_parser = ArgumentParser(
        prog=recap_module_name,
        description='Add or Remove Hosts from RECAP Environment',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    arg_parser.add_argument('action', choices=['add', 'remove'])
    arg_parser.add_argument('host')
    arg_parser.add_argument(
        '--infrastructure', choices=['r_user', 'r_infra', 'admin', 'global'], required=False)
    arg_parser.add_argument('--site', required=False)
    arg_parser.add_argument('--username', required=True)
    arg_parser.add_argument('--private-key-file', required=True)
    arg_parser.add_argument('--start-stack', action='store_true')
    arg_parser.add_argument('--python-interpreter', default='/usr/bin/python')
    arg_parser.add_argument('--pip-executable', default='pip')
    arg_parser.add_argument('--pip-as-non-root', action='store_true')
    arg_parser.add_argument('--proxy-host', required=False)
    arg_parser.add_argument('--extra-labels', required=False, type=labels_type)

    args = arg_parser.parse_args(argv)

    if args.action == 'add' and (args.infrastructure is None or args.site is None):
        arg_parser.error('add requires --infrastructure and --site')

    extra_labels = ''
    if args.extra_labels is not None:
        extra_labels = get_labels_string(args.extra_labels)

    if args.proxy_host is None:
        ssh_args = '-o StrictHostKeyChecking=no'
    else:
        ssh_args = f'-o StrictHostKeyChecking=no -o ProxyCommand="ssh -W %h:%p -q {args.username}@{args.proxy_host} -i {args.private_key_file} -o ControlMaster=auto -o ControlPersist=30m -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"'

    runner = AnsibleRunner()
    rancher_access_key_site = os.getenv('RANCHER_ACCESS_KEY_'+args.site)
    rancher_secret_key_site = os.getenv('RANCHER_SECRET_KEY_'+args.site)
    rancher_env_site = os.getenv('RANCHER_ENV_ID_'+args.site)
    rancher = RancherClient(
        rancher_env_site, rancher_access_key_site, rancher_secret_key_site)

    host = Host(address=args.host,
                username=args.username,
                private_key_file=args.private_key_file,
                variables={
                    'ansible_ssh_common_args': ssh_args,
                    'ansible_python_interpreter': args.python_interpreter,
                    'type': args.infrastructure,
                    'site': args.site,
                    'extra_labels': extra_labels
                })

    if args.action == 'add':
        success = add(host=host,
                      ansible_runner=runner,
                      rancher=rancher,
                      pip_executable=args.pip_executable,
                      pip_as_root=not args.pip_as_non_root)

        if success and args.start_stack:
            success = stack_cmd([
                'up', args.site, '--infrastructures', args.infrastructure
            ])

    else:
        success = remove(host=host,
                         ansible_runner=runner,
                         rancher_client=rancher)

    return success


def add(host: Host,
        ansible_runner: AnsibleRunner,
        rancher: RancherClient,
        pip_executable: str = 'pip',
        pip_as_root: bool = True) -> bool:
    ansible_runner.add_host(host)

    log.info(f'Adding {host} to environment')

    return ansible_runner.play(
        f'{_playbook_path}/add_host.yml',
        targets=[host.address],
        extra_vars={
            'RANCHER_SERVER_URL': rancher.url,
            'RANCHER_ENV_ID': rancher.env_id,
            'RANCHER_REG_TOKEN': rancher.get_registration_token(),
            'HOST_ID': host.address,
            'HOST_TYPE': host.variables['type'],
            'HOST_SITE': host.variables['site'],
            'PIP_EXECUTABLE': pip_executable,
            'PIP_AS_ROOT': 'yes' if pip_as_root else 'no',
            'EXTRA_LABELS': host.variables['extra_labels']
        }
    )


def remove(host: Host,
           ansible_runner: AnsibleRunner,
           rancher_client: RancherClient) -> bool:
    ansible_runner.add_host(host)

    log.info(f'Removing {host} from environment')

    rancher_host = rancher_client.get_host(host.address)

    if rancher_host is None:
        log.warning(f'Host {host.address} was not found in rancher, skipping')
        return False

    deleted_from_rancher = rancher_client.delete_host(rancher_host)
    if not deleted_from_rancher:
        log.warning(
            f'Host {host} was not deleted from Rancher master, skipping')
        return False

    return ansible_runner.play(
        f'{_playbook_path}/remove_host.yml',
        targets=[host.address]
    )

