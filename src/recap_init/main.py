from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path
from typing import List, Dict

from ansible_runner import AnsibleRunner, Host
from logger import get_logger
from recap_env import main as env

recap_module_name = 'init'

log = get_logger(recap_module_name)

_file_path = Path(__file__).resolve().parent
_playbook_path = f'{_file_path}/playbooks'


def main(argv: List[str]) -> bool:
    arg_parser = ArgumentParser(
        prog=recap_module_name,
        description='Initialize a new RECAP Environment',
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    arg_parser.add_argument('--host', required=True)
    arg_parser.add_argument('--username', required=True)
    arg_parser.add_argument('--private-key-file', required=True)
    arg_parser.add_argument('--python-interpreter', default='/usr/bin/python')
    arg_parser.add_argument('--update-config', action='store_true')
    arg_parser.add_argument('--rancher-username', required=True)
    arg_parser.add_argument('--rancher-password', required=True)
    arg_parser.add_argument('--rancher-env-name', default='recap')
    arg_parser.add_argument('--rancher-registry-url', required=True)
    arg_parser.add_argument('--rancher-registry-username', required=True)
    arg_parser.add_argument('--rancher-registry-password', required=True)
    arg_parser.add_argument('--pip-executable', default='pip')
    arg_parser.add_argument('--pip-as-non-root', action='store_true')
    arg_parser.add_argument('--rancher-sites', nargs='*')

    args = arg_parser.parse_args(argv)

    print(args)

    runner = AnsibleRunner()

    host = Host(address=args.host,
                username=args.username,
                private_key_file=args.private_key_file,
                variables={
                    'ansible_ssh_common_args': '-o StrictHostKeyChecking=no',
                    'ansible_python_interpreter': args.python_interpreter
                })

    return init(host=host,
                ansible_runner=runner,
                update_config=args.update_config,
                rancher_username=args.rancher_username,
                rancher_password=args.rancher_password,
                rancher_environment_name=args.rancher_env_name,
                rancher_registry_url=args.rancher_registry_url,
                rancher_registry_username=args.rancher_registry_username,
                rancher_registry_password=args.rancher_registry_password,
                rancher_sites=args.rancher_sites,
                pip_executable=args.pip_executable,
                pip_as_root=not args.pip_as_non_root)


def init(host: Host,
         ansible_runner: AnsibleRunner,
         update_config: bool,
         rancher_username: str,
         rancher_password: str,
         rancher_environment_name: str,
         rancher_registry_url: str,
         rancher_registry_username: str,
         rancher_registry_password: str,
         rancher_sites: List[str],
         pip_executable: str = 'pip',
         pip_as_root: bool = True) -> bool:
    ansible_runner.add_host(host)

    log.info(f'Initializing RECAP environment at {host}')
    success = ansible_runner.play(
        f'{_playbook_path}/init_server.yml',
        targets=[host.address],
        extra_vars={
            'RANCHER_USERNAME': rancher_username,
            'RANCHER_PASSWORD': rancher_password,
            'RANCHER_ENVIRONMENT_NAME': rancher_environment_name,
            'RANCHER_REGISTRY_URL': rancher_registry_url,
            'RANCHER_REGISTRY_USERNAME': rancher_registry_username,
            'RANCHER_REGISTRY_PASSWORD': rancher_registry_password,
            'RANCHER_SITES': rancher_sites,
            'PIP_EXECUTABLE': pip_executable,
            'PIP_AS_ROOT': 'yes' if pip_as_root else 'no'
        }
    )

    facts = ansible_runner.get_local_facts(host)
    try:
        settings = _get_settings(facts, host, rancher_sites)
    except KeyError as err:
        log.error(f'Unable to get RECAP settings: {err}')
        exit(1)
        return False
    except Exception:
        log.error('Unable to retrieve RECAP settings')
        exit(1)
        return False

    _print_settings(settings)
    if update_config:
        _update_config(settings)
        # exit(1)
    return success


def _get_settings(facts: Dict[str, any], host: Host, rancher_sites: List[str]) -> Dict[str, str]:
    r = {
        # 'RANCHER_URL': facts['rancher_registration_url']['value'],
        'RANCHER_URL': f'http://{host.address}:8080'
        # 'RANCHER_ACCESS_KEY': facts['rancher_recap_api']['publicValue'],
        # 'RANCHER_SECRET_KEY': facts['rancher_recap_api']['secretValue']
    }

    for site in rancher_sites:
        r.update(
            {'RANCHER_ENV_ID_' +
             site: facts['rancher_recap_api_'+site]['accountId'],
             'RANCHER_SECRET_KEY_' +
             site: facts['rancher_recap_api_'+site]['secretValue'],
             'RANCHER_ACCESS_KEY_' +
             site: facts['rancher_recap_api_'+site]['publicValue']
             }
        )

    return r


def _print_settings(settings: Dict[str, str]) -> None:
    for k, v in settings.items():
        print(f'{k}={v}')


def _update_config(settings: Dict[str, str]) -> None:
    for k, v in settings.items():
        env(['set', k, v])


