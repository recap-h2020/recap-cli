class Options(object):
    """
    Options class to replace Ansible OptParser

    stolen from 
    https://serversforhackers.com/c/running-ansible-2-programmatically
    """

    def __init__(self,
                 ask_become_pass=False,
                 become=False,
                 become_ask_pass=None,
                 become_method='sudo',
                 become_user='root',
                 check=None,
                 connection='smart',
                 diff=None,
                 extra_vars=None,
                 flush_cache=None,
                 force_handlers=None,
                 forks=5,
                 inventory=None,
                 listhosts=None,
                 listtags=None,
                 listtasks=None,
                 module_path=None,
                 module_paths=None,
                 new_vault_password_file=None,
                 one_line=None,
                 output_file=None,
                 poll_interval=None,
                 private_key_file=None,
                 remote_user=None,
                 scp_extra_args=None,
                 seconds=None,
                 sftp_extra_args=None,
                 skip_tags=[],
                 ssh_common_args=None,
                 ssh_extra_args=None,
                 subset=None,
                 syntax=None,
                 tags=[],
                 timeout=10,
                 tree=None,
                 vault_password_files=None,
                 verbosity=None):
        self.become = become
        self.become_ask_pass = become_ask_pass
        self.become_method = become_method
        self.become_user = become_user
        self.check = check
        self.connection = connection
        self.diff = diff
        self.extra_vars = extra_vars
        self.flush_cache = flush_cache
        self.force_handlers = force_handlers
        self.forks = forks
        self.inventory = inventory
        self.listhosts = listhosts
        self.listtags = listtags
        self.listtasks = listtasks
        self.module_path = module_path
        self.module_paths = module_paths
        self.new_vault_password_file = new_vault_password_file
        self.one_line = one_line
        self.output_file = output_file
        self.poll_interval = poll_interval
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.scp_extra_args = scp_extra_args
        self.seconds = seconds
        self.sftp_extra_args = sftp_extra_args
        self.skip_tags = skip_tags
        self.ssh_common_args = ssh_common_args
        self.ssh_extra_args = ssh_extra_args
        self.subset = subset
        self.syntax = syntax
        self.tags = tags
        self.timeout = timeout
        self.tree = tree
        self.vault_password_files = vault_password_files
        self.verbosity = verbosity
