import os
from shutil import which
from typing import List

from logger import get_logger
from process import invoke


class RancherCompose(object):

    def __init__(self,
                 rancher_url: str,
                 rancher_access_key: str,
                 rancher_secret_key: str,
                 site: str,
                 infrastructure: str):
        self.log = get_logger(self.__class__.__name__)

        if which('rancher-compose') is None:
            self.log.error('rancher-compose binary not found')
            raise EnvironmentError()

        os.environ['RANCHER_URL'] = rancher_url
        os.environ['RANCHER_ACCESS_KEY'] = rancher_access_key
        os.environ['RANCHER_SECRET_KEY'] = rancher_secret_key
        os.environ['GLOBAL_SITE_NAME'] = site
        os.environ['RECAP_INFRASTRUCTURE_LABEL'] = infrastructure

        self.log.info('Playing against Rancher at %s for site %s' %
                      (os.environ['RANCHER_URL'], site))

    def up(self,
           stack: str,
           services: List[str],
           docker_compose_file: str,
           rancher_compose_file: str) -> bool:
        return self.exec(docker_compose_file,
                         rancher_compose_file,
                         stack,
                         'up -c -u -p -d',
                         services)

    def down(self,
             stack: str,
             services: List[str],
             docker_compose_file: str,
             rancher_compose_file: str) -> bool:
        return self.exec(docker_compose_file,
                         rancher_compose_file,
                         stack,
                         'down',
                         services)

    def restart(self,
                stack: str,
                services: List[str],
                docker_compose_file: str,
                rancher_compose_file: str) -> bool:
        return self.exec(docker_compose_file,
                         rancher_compose_file,
                         stack,
                         'restart',
                         services)

    def delete(self,
               stack: str,
               services: List[str],
               docker_compose_file: str,
               rancher_compose_file: str) -> bool:
        return self.exec(docker_compose_file,
                         rancher_compose_file,
                         stack,
                         'rm -f',
                         services)

    def exec(self,
             docker_compose_file: str,
             rancher_compose_file: str,
             stack: str,
             action: str,
             services: List[str]) -> bool:
        cmd = ['rancher-compose',
               '-f', docker_compose_file,
               '-r', rancher_compose_file,
               '-p', stack]
        cmd += action.split(' ')
        cmd += services

        self.log.debug('Running ' + ' '.join(cmd))
        returncode, stdout, stderr = invoke(cmd)
        self.log.info(stdout)

        if stderr:
            self.log.error(stderr)
        return returncode == 0
