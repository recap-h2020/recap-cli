from pathlib import Path
from typing import Callable, List, Dict
import sys

import jsonpickle


class VenvJsonLoader(object):
    def __init__(self, json_file: str, venv: Callable[[List[str]], bool]):
        f = Path(json_file)
        assert f.is_file()
        self.env = jsonpickle.decode(f.read_text())
        self.venv = venv

    def setup(self) -> bool:
        result = True

        sites = self.env['sites']
        for s in sites:
            result = self._setup_site(s) and result

        master_site = [s for s in sites if s['master'] is True]
        assert len(master_site) == 1
        master_site = master_site[0]
        result = self._setup_master(master_site) and result

        for s in [s for s in sites if s['parent'] is not None]:
            result = self._setup_connection(s) and result

        for s in sites:
            result = self._setup_hosts(s) and result

        return result

    def _setup_site(self, site: Dict[str, any]) -> bool:
        return self.venv([
            'add-site',
            '--name', site['name'],
            '--network', site['network'],
            '--router-ip', site['router-ip']
        ])

    def _setup_connection(self, site: Dict[str, any]) -> bool:
        parent_site = [s for s in self.env['sites']
                       if s['name'] == site['parent']['name']]
        assert len(parent_site) == 1
        parent_site = parent_site[0]

        return self.venv([
            'connect-sites',
            '--inter-network', site['parent']['inter-network'],
            '--inter-ports', site['parent']['inter-ports'][0], site['parent']['inter-ports'][1],
            '--sites', parent_site['name'], site['name'],
            '--site-networks', parent_site['network'], site['network'],
            '--router-ip', site['router-ip']
        ])

    def _setup_master(self, site: Dict[str, any]) -> bool:
        site_names = []
        for site_name in self.env['sites']:
            site_names.append(site_name['name'])
        return self.venv([
            'init-master',
            '--on-site', site['name'],
            '--public-key-file', self.env['keys']['public'],
            '--private-key-file', self.env['keys']['private'],
            '--rancher-sites', *site_names
        ])

    def _setup_hosts(self, site: Dict[str, any]) -> bool:
        result = True
        is_master_site = site.get('master') or False

        host_type_az = {
            "r_infra": None,
            "r_user": None,
            "admin": None,
            "global": None,
        }

        if site.get('availability_zone'):
            site_az = site.get('availability_zone')
        else:
            site_az = 'blade'

        host_type_az['r_infra'] = site_az
        host_type_az['r_user'] = site_az
        host_type_az['admin'] = site_az
        host_type_az['global'] = site_az

        if site.get('availability_zones'):
            if site.get('availability_zones').get('r_infra'):
                host_type_az['r_infra'] = site.get(
                    'availability_zones').get('r_infra')
            if site.get('availability_zones').get('r_user'):
                host_type_az['r_user'] = site.get(
                    'availability_zones').get('r_user')
            if site.get('availability_zones').get('admin'):
                host_type_az['admin'] = site.get(
                    'availability_zones').get('admin')
            if site.get('availability_zones').get('global'):
                host_type_az['global'] = site.get(
                    'availability_zones').get('global')

        host_type_flavour = {
            "r_infra": None,
            "r_user": None,
            "admin": None,
            "global": None,
        }

        if site.get('flavour'):
            site_flavour = site.get('flavour')
        else:
            site_flavour = 'medium'

        host_type_flavour['r_infra'] = site_flavour
        host_type_flavour['r_user'] = site_flavour
        host_type_flavour['admin'] = site_flavour
        host_type_flavour['global'] = site_flavour

        if site.get('flavours'):
            if site.get('flavours').get('r_infra'):
                host_type_flavour['r_infra'] = site.get(
                    'flavours').get('r_infra')
            if site.get('flavours').get('r_user'):
                host_type_flavour['r_user'] = site.get(
                    'flavours').get('r_user')
            if site.get('flavours').get('admin'):
                host_type_flavour['admin'] = site.get('flavours').get('admin')
            if site.get('flavours').get('global'):
                host_type_flavour['global'] = site.get(
                    'flavours').get('global')

        for host_type, count in site['hosts'].items():
            if host_type_az.get(host_type):
                host_az = host_type_az.get(host_type)
            else:
                host_az = site_az

            if host_type_flavour.get(host_type):
                host_flavour = host_type_flavour.get(host_type)
            else:
                host_flavour = site_flavour

            for instance in range(count):
                args = [
                    'add-host',
                    '--on-site', site['name'],
                    '--type', host_type,
                    '--instance', str(instance),
                    '--public-key-file', self.env['keys']['public'],
                    '--private-key-file', self.env['keys']['private'],
                    '--vm-flavour', host_flavour,
                    '--vm-availability-zone', host_az
                ]
                if is_master_site:
                    args.append('--is-master')

                result = self.venv(args) and result
        return result
