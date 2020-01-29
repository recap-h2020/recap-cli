from pathlib import Path
from typing import List, Optional

from ansible.inventory.host import Host

from ansible_runner import AnsibleRunner
from logger import get_logger
from recap_stack import main as recap_stack
from settings.env import load_env

p = Path(__file__).parent.resolve().parent
playbook_path = f'{p}/playbooks'

log = get_logger(__name__)


def get_host_info(host: Host) -> dict:
    return {
        "ip": host.vars['ansible_ssh_host'],
        "hostname": host.vars['openstack']['name']
    }


def get_host_groups(host: Host) -> List[str]:
    return [g.get_name().lower() for g in host.get_groups()]


def is_user_host(host: Host, site: str) -> bool:
    groups = get_host_groups(host)
    return 'r_user' in groups and site.lower() in groups


def is_infra_host(host: Host, site: str) -> bool:
    groups = get_host_groups(host)
    return 'r_infra' in groups and site.lower() in groups


def is_rancher_host(host: Host) -> bool:
    groups = get_host_groups(host)
    return 'rancher-server' in groups


def get_infra_host(hosts: List[Host], site: str) -> Optional[Host]:
    infra_hosts = [h for h in hosts if is_infra_host(h, site)]
    return infra_hosts[0] if infra_hosts else None


def get_rancher_host(hosts: List[Host]) -> Optional[Host]:
    rancher_hosts = [h for h in hosts if is_rancher_host(h)]
    return rancher_hosts[0] if rancher_hosts else None


def update(site: str,
           restart_service: bool,
           ssh_user: str,
           private_key: str,
           python_interpreter: str,
           ssh_common_args: str
           ) -> bool:
    ar = AnsibleRunner(
        inventory=[f'{playbook_path}/inventory.d/90_os_inventory.sh']
    )
    hosts = ar.inventory_manager.get_hosts()
    user_hosts = [get_host_info(h) for h in hosts if is_user_host(h, site)]
    infra_host = get_infra_host(hosts, site)

    if not infra_host:
        log.error(f'No r_infra host found for site {site}')
        return False

    rancher_host = get_rancher_host(hosts)
    rancher_host.vars['ansible_ssh_user'] = ssh_user
    rancher_host.vars['ansible_ssh_private_key_file'] = private_key
    rancher_host.vars['ansible_python_interpreter'] = python_interpreter
    rancher_host.vars['ansible_ssh_common_args'] = ssh_common_args

    success = ar.play(
        f'{playbook_path}/update_landscaper.yml',
        extra_vars={
            'INFRA_HOST': infra_host.vars['ansible_ssh_host'],
            'USER_HOSTS': user_hosts
        }
    )

    if success and restart_service:
        recap_stack([
            'restart', site,
            '--infrastructures', 'r_infra',
            '--services', 'landscaper'
        ])

    return success


if __name__ == '__main__':
    load_env()
    update(site='A',
           restart_service=True,
           ssh_user='core',
           private_key='/opt/app/recap_virtualenv/keys/cloud_key.pem',
           python_interpreter='/home/core/bin/python',
           ssh_common_args='-o StrictHostKeyChecking=no')
