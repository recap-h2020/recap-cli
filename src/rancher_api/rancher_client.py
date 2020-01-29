import os
from typing import Union

from rancher import Client, RestObject

from logger import get_logger


class RancherClient:

    def __init__(self, rancher_env_site, rancher_access_key_site, rancher_secret_key_site):
        self.log = get_logger(self.__class__.__name__)

        self.url = os.getenv('RANCHER_URL')
        self.access_key = rancher_access_key_site
        self.secret_key = rancher_secret_key_site
        self.env_id = rancher_env_site

        self.log.info(
            f'Playing against Rancher at {self.url} in {self.env_id}')
        print(self)
        self.rancher_client = Client(url=self.url,
                                     access_key=self.access_key,
                                     secret_key=self.secret_key)

    def get_registration_token(self) -> str:
        t = self.rancher_client.list_registration_token()
        assert t is not None
        return t.data[0].token

    def get_host(self, ip_address: str) -> Union[RestObject, None]:
        hosts = self.rancher_client.list_host().data
        for host in hosts:
            for endpoint in host.publicEndpoints:
                if endpoint.ipAddress == ip_address:
                    return host

            if hasattr(host.labels, 'host') and host.labels.host == ip_address:
                return host

        return None

    def delete_host(self, host: RestObject) -> bool:
        self.deactivate_host(host)
        self.rancher_client.delete(host)
        return True

    def deactivate_host(self, host: RestObject) -> bool:
        self.rancher_client.action(host, 'deactivate')
        return True


