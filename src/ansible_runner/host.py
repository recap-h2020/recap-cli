from typing import Dict


class Host:

    def __init__(self,
                 address: str,
                 username: str,
                 private_key_file: str,
                 group: str = 'all',
                 variables: Dict[str, str] = {}):
        self.address = address
        self.username = username
        self.private_key_file = private_key_file
        self.group = group
        self.variables = variables

    def __str__(self):
        return self.address
