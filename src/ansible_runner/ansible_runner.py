from typing import List, Dict, Optional

from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager

from ansible_runner.host import Host
from ansible_runner.options import Options


class AnsibleRunner:

    def __init__(self,
                 inventory: List[str] = None):
        self.options = Options()
        self.data_loader = DataLoader()
        self.inventory_manager = InventoryManager(
            loader=self.data_loader,
            sources=inventory
        )
        self.variable_manager = VariableManager(
            loader=self.data_loader,
            inventory=self.inventory_manager
        )

    def add_host(self, host: Host) -> None:
        self.inventory_manager.add_host(
            host.address,
            group=host.group
        )
        h = self.inventory_manager.get_host(
            host.address
        )
        h.set_variable(
            'ansible_ssh_user',
            host.username
        )
        h.set_variable(
            'ansible_ssh_private_key_file',
            host.private_key_file
        )
        for (key, val) in host.variables.items():
            h.set_variable(key, val)

    def get_host_vars(self, host: Host) -> Optional[Dict[str, any]]:
        h = self.inventory_manager.get_host(
            host.address
        )
        return h.get_vars() if h is not None else None

    def get_local_facts(self, host: Host) -> Optional[Dict[str, any]]:
        h = self.inventory_manager.get_host(
            host.address
        )
        if h is None:
            return None
        v = self.variable_manager.get_vars(host=h)
        return v.get('ansible_facts', {}).get('ansible_local', {})

    def play(self,
             playbook: str,
             targets: List[str] = None,
             extra_vars: Dict[str, str] = None) -> bool:
        if extra_vars is None:
            extra_vars = {}

        if targets is not None:
            extra_vars['targets'] = ','.join(targets)

        self.variable_manager.extra_vars = extra_vars

        pbex = PlaybookExecutor(
            playbooks=[playbook],
            inventory=self.inventory_manager,
            variable_manager=self.variable_manager,
            loader=self.data_loader,
            options=self.options,
            passwords=None
        )

        return pbex.run() == 0
