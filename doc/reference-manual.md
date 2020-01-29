---
title: |
  RECAP Command Line Interface: \
  Reference Manual
author: |
  Benjamin Schanzel (benjamin.schanzel@uni-ulm.de) \
  Institute of Information Resource Management, Ulm University
date: \today
toc: true
---

Introduction
============

The RECAP Command Line Interface (CLI) module provides commands to setup and interact with RECAP components and services. It orchestrates several other tools to provide a convenient interface to RECAP infrastructure and services. This reference manual instructs how to set up the RECAP CLI tool and provides a comprehensive list of the available commands.

Setup
=====

The preferred way of running the tool is within a Docker container.
You can obtain a copy of the RECAP CLI code at

`https://omi-gitlab.e-technik.uni-ulm.de/students/hiwi/recap-cli`.

After downloading the repository sources, the following steps are needed to setup an initial environment configuration.

``` {.bash}
cd recap-cli/src
cp .env.example .env
```

Assuming you have Docker installed and running on your local machine, no additional steps are needed to install any dependencies.
The following command should succeed and display available commands.

``` {.bash}
./recap help
```

To have the CLI tool use the latest upsteam Docker image version run the `recap` command with the `--pull` flag.

``` {.bash}
./recap --pull [args]
```

To build the Docker image locally, e.g. when developing and modifying sources of the CLI project, include the `--build` flag.

``` {.bash}
./recap --build [args]
```

Please also note that the `recap` wrapper executable file is implemented as a Unix shell script. If you are running Windows, please use the [Windows Subsystem for Linux], [Cygwin], or execute the Python script directly as listed below.

If you prefer to run RECAP CLI on your host system directly, without Docker, the following steps are needed.

1.  have Git installed on your host system
2.  have Python 3.6 installed (it would propably work with Python 3 versions below 3.6 but will not work with Python 3.7 and above)
3.  install the Python dependencies via `pip3 install -r requirements.txt` (this will, among other tools, install Ansible on your host system)
4.  Install the `defunctzombie.coreos-bootstrap` Ansible role via `ansible-galaxy`
5.  Have a rancher-compose v0.12.5 binary somewhere in your PATH (can be obtained from [Ranchers' GitHub repository])

Verify everything works by typing `python3 cli/recap.py help` in your terminal. You should see the available commands in the output.

Available Commands
==================

To get a list of available commands, run `./recap help`. For each of the commands, the respective help text and argument list can be obtained via

``` {.bash}
./recap help [command]
```

env
---

``` {.bash}
./recap env [action] [key] [value]
```

`List and Persistently Modify Environment Variables`

The `env` command lists and persistently modifies configuration parameters found in the `.env` file.

-   `env list`

    prints all of the currently set configuration parameters to `STDOUT`

-   `env get [key]`

    prints a single configuration parameter identified by `[key]` to `STDOUT`

-   `env set [key] [value]`

    sets the configuration parameter identified by `[key]` to the given `[value]` by writing it to the `.env` file, either appending or replacing if the parameter with the given `[key]` was present before

### Example

``` {.bash}
./recap env get LOG_LEVEL
```

``` {.bash}
./recap env set LOG_LEVEL INFO
```

init
----

``` {.bash}
./recap init [arguments]
```

`Initilize a new RECAP Environment`

`init` installs a fresh RECAP environment on the given host, i.e. it starts a Rancher server and configures it according to the given parameters. The then created parameters for the `.env` file are printed to `STDOUT` and, if desired, directly updated in the `.env` configuration file for the CLI tool to subsequently perform any actions against the new RECAP installation.

Mandatory parameters are

-   `--host`

    the host on which the rancher server will be deployed (Python and Docker must be installed on this host in advance)

-   `--username`

    the username to authenticate at the given `--host`

-   `--private-key-file`

    the SSH private key file for authentication at the given `--host`

-   `--rancher-username`

    the username for Rancher local authentication (cf. [Access Control in Rancher])

-   `--rancher-password`

    the password for Rancher local authentication (cf. [Access Control in Rancher])

-   `--rancher-registry-url`

    the URL to a private image registry (cf. [Registries in Rancher])

-   `--rancher-registry-username`

    the username to authenticate at the given private image registry

-   `--rancher-registry-password`

    the password or access token to authenticate at the given private image registry

Optional parameters are

-   `--python-interpreter`

    path to the Python interpreter binary at the given `--host`, default `/usr/bin/python`

-   `--rancher-env-name`

    the name of the Rancher environment to create during installation, default `recap`

-   `--update-config`

    when passed, updates the `.env` config file with the newly created `RANCHER_URL`, `RANCHER_ACCESS_KEY`, `RANCHER_SECRET_KEY`, and `RANCHER_ENV_ID`

### Example

``` {.bash .numberLines}
  ./recap init \
    --host 134.60.64.123 \
    --username core \
    --private-key-file id_rsa \
    --python-interpreter /opt/bin/python \
    --rancher-username admin \
    --rancher-password secret123 \
    --rancher-env-name recap \
    --rancher-registry-url omi-registry.e-technik.uni-ulm.de \
    --rancher-registry-username recap \
    --rancher-registry-password 123456789ABCDEF \
    --update-config
```

host
----

``` {.bash}
./recap host [action] [host] [arguments]
```

`Add or Remove Hosts from RECAP Environment`

The `host` command takes an IP address or host name as an argument and adds or removes this host from the environment (i.e. as a Rancher agent).

Available actions are

-   `add`

    adds the given `host` to the environment, requires the arguments `--infrastructure` and `--site` to be set

-   `remove`

    removes the given `host` from the environment

Mandatory arguments are

-   `--username`

    the username to authenticate at the given `host`

-   `--private-key-file`

    the SSH private key file for authentication at the given `host`

Optional arguments are

-   `--infrastructure`

    the infrastructure label to apply for the `host`, must be either `r_user`, `r_infra`, `admin`, or `global`

-   `--site`

    the site label to apply for the `host`, takes an arbitrary value

-   `--start-stack`

    if set, immediately starts the stacks defined for the applied site and infrastructure labels on the given `host`

-   `--python-interpreter`

    path to the Python interpreter binary at the given `host`, default `/usr/bin/python`

### Example

``` {.bash .numberLines}
./recap host add 134.60.64.234 \
    --username core \
    --private-key-file id_rsa \
    --python-interpreter /opt/bin/python \
    --infrastructure r_user \
    --site datacenter_1 \
    --start-stack
```

``` {.bash .numberLines}
./recap host remove 134.60.64.234 \
    --username core \
    --private-key-file id_rsa \
    --python-interpreter /opt/bin/python
```

stack
-----

``` {.bash}
./recap stack [action] [site] [arguments]
```

`Manage Complete RECAP Stacks on Running Sites`

This command starts or stops the RECAP stacks on the given `site`. You can optionally specify which `--infrastructures` stacks should be started or stopped. The services to start for each infrastructure is specified in the `.env` file. Also you can optionally specify which configuration sidekick container should be used for the logstash and dashboard services. These arguments override the corresponding value given in the `.env` file.

Available actions are

-   `up`

    starts stacks on the given `site`

-   `down`

    stops stacks on the given `site`

-   `delete`

    deletes stacks on the given `site`

-   `restart`

    restats stacks on the given `site`

Optional arguments are

-   `--infrastructures`

    specifies which infrastructure stacks to start or stop, must be any subset of `r_infra`, `r_user`, `global`, and `admin`, defaults to all of these values.

-   `--services`

    restrict actions to specific services

-   `--logstash-config-image`

    specifies which configuration sidekick container to use for the logstash service, overrides the `LOGSTASH_CONFIG_IMAGE` configuration parameter

-   `--dashboard-config-image`

    specifies which configuration sidekick container to use for the dashboard service, overrides the `LOGSTASH_CONFIG_IMAGE` configuration parameter

### Example

``` {.bash .numberLines}
./recap stack up datacenter_1 \
    --infrastructures r_user r_infra global admin \
    --logstash-config-image \
        omi-registry.e-technik.uni-ulm.de/recap-demo/my-custom-logstash-config:latest
```

``` {.bash .numberLines}
./recap stack down datacenter_1 \
    --infrastructures r_user
```

component
---------

``` {.bash}
./recap component [action] [arguments]
```

`Atomically Manage RECAP Components via Rancher`

This command allows to manage single RECAP components/services in Rancher. You can bring specified components `up`, `down`, or `delete` them.

Mandatory arguments are

-   `--site`

    on which `site` to perform the specified `action` on

-   `--infrastructure`

    components of which `infrastructure` to perform the specified `action` on

-   `--stack`

    the name of the `stack` the components are running on

-   `--docker-compose-file`

    the `docker-compose.yml` file the services are defined in

-   `--rancher-compose-file`

    the `rancher-compose.yml` file defining Rancher related parameters for the services

-   `--services`

    a list of `services` on which the specified `action` shall be performed on, must be any subset of the services defined in the `docker-compose.yml` file

### Example

``` {.bash .numberLines}
./recap component up \
    --site datacenter_1 \
    --infrastructure r_infra \
    --stack state-local \
    --docker-compose-file infra/docker-compose.yml \
    --rancher-compose-file infra/rancher-compose.yml \
    --services logstash
```

venv
----

``` {.bash}
./recap venv -h
```

`Manage Virtual RECAP Infrastructure on OpenStack`

This command brings up or down a virtual RECAP infrastructure on an OpenStack installation. It creates a configurable number of hierarchical sites with a virtual network for each site. A VM for the Rancher master is provided at the main site. The names of sites and the number of VMs in them is parametrized. Each VM will serve as a Rancher agent. Which OpenStack installation to use is specified and configurable in the `.env` file.

Available actions are

-   `add-site`

    Add a new site. This requires the arguments `--name`, `--network`, and `--router-ip`.

-   `init-master`

    Initialize a new Rancher master on a site. This is usually issued once on the master site. This requires the arguments `--on-site`, `--public-key-file`, and `--private-key-file`.

-   `add-host`

    Add a new host VM as a Rancher agent to an existing site. This requires the arguments `--type`, `--on-site`, `--instance`, `--public-key-file`, and `--private-key-file`.

-   `connect-sites`

    Connects the networks of two sites allowing communication between them. This requires the arguments `--sites`, `--inter-network`, `--inter-ports`, `--site-networks`

-   `from-json`

    Automates the process of creating a virtual environment as described in a `JSON` file. This requires the argument `--file`.

Mandatory arguments are (depending on the chosen action)

-   `--name`

    The name of site to be created.

-   `--network`

    The IPv4 CIDR network address to use in the site to be created (e.g. 192.168.0.0/24).

-   `--router-ip`

    The IPv4 address to assign to the sites router.

-   `--on-site`

    The name of the site to perform an action on.

-   `--type`

    The type of the host to add (e.g. `r_user`, `r_infra`, ...).

-   `--instance`

    An integer value, usually consecutive, to uniquely identify a host within a site.

-   `--public-key-file`

    An SSH public key file to use for authentication.

-   `--private-key-file`

    An SSH private key file to store on created VMs, must be the correct counterpart to the given `--public-key-file`.

-   `--sites`

    The names of the sites to connect.

-   `--site-networks`

    The IPv4 CIDR network addresses of the sites to connect.

-   `--inter-network`

    An IPv4 CIDR network address to use for the interconnecting network.

-   `--inter-ports`

    IPv4 addresses from the `--inter-network` to assign on the interconnecting router.

-   `--file`

    The `JSON` file to load for automating the process of virtual environment creation.

### Example

``` {.bash}
./recap venv from-json --file example.json
```

with `example.json` having the following contents

``` {.json .numberLines}
{
	"keys": {
		"public": "/opt/app/recap_virtualenv/keys/cloud_key.public",
		"private": "/opt/app/recap_virtualenv/keys/cloud_key.pem"
	},
	"sites": [
		{
			"name": "A",
			"network": "192.168.0.0/24",
			"router-ip": "192.168.0.1",
			"master": true,
			"hosts": {
				"r_infra": 1,
				"r_user": 2,
				"admin": 1,
				"global": 1
			},
			"parent": null
		},
		{
			"name": "B",
			"network": "192.168.1.0/24",
			"router-ip": "192.168.1.1",
			"master": false,
			"hosts": {
				"r_infra": 1,
				"r_user": 2
			},
			"parent": {
				"name": "A",
				"inter-network": "192.168.10.0/24",
				"inter-ports": [
					"192.168.10.10",
					"192.168.10.20"
				]
			}
		}
	]
}
```

Configuration
=============

The RECAP CLI tool is configured using a `.env` file. It follows a simple `key=value` structure, with keys and values separated by a equality sign (`=`) and entries separated by a line break. Comment lines are denoted by a hash sign (`#`). Generally speaking, the format is a simplified version of the [.properties file format]. A short example of a `.env` file and its' format is depicted below.

``` {.ini .numberLines}
# set the application wide log level
LOG_LEVEL=DEBUG

# set the Rancher master connection parameters
RANCHER_URL=http://134.60.152.184:8080
RANCHER_ACCESS_KEY=72A30F123D3FE0D88577
RANCHER_SECRET_KEY=1cGRr2u3MdJWCZszS4eJFdT941sJahjHKc4aoDZj
RANCHER_ENV_ID=1a7
```

A comprehensive example of a RECAP CLI `.env` file can be found in the repository as [`.env.example`].

This section lists and explains the semantics of the available configuration parameters to the RECAP CLI tool. The parameters listed here are all mandatory, sane default values can be taken from the provided `.env.example` file.

Available Configuration Parameters
----------------------------------

-   `LOG_LEVEL`

    the level of details the log output contains, value must be either of `DEBUG`, `INFO`, `WARN`, or `ERROR`, where `DEBUG` is the most verbose level and `ERROR` only prints error messages

-   `RANCHER_URL`

    the URL under which the Rancher master API is creachable, usually an HTTP URL to port 8080

-   `RANCHER_ACCESS_KEY`

    the Rancher master public access key

-   `RANCHER_SECRET_KEY`

    the secret part of the Rancher access key

-   `RANCHER_ENV_ID`

    the Rancher master environment ID, usually a 3-char hexadecimal string

-   `SERVICES_ADMIN`

    a list of services to start within the `ADMIN` stack, services must be defined in the corresponding `docker-compose.yml` file

-   `SERVICES_GLOBAL`

    a list of services to start within the `GLOBAL` stack, services must be defined in the corresponding `docker-compose.yml` file

-   `SERVICES_INFRA`

    a list of services to start within the `R_INFRA` stack, services must be defined in the corresponding `docker-compose.yml` file

-   `SERVICES_USER`

    a list of services to start within the `R_USER` stack, services must be defined in the corresponding `docker-compose.yml` file

-   `STACK_NAME_ADMIN`

    the internal name Rancher shall give to the `ADMIN` stack, usually `admin`

-   `STACK_NAME_GLOBAL`

    the internal name Rancher shall give to the `GLOBAL` stack, usually `state-global`

-   `STACK_NAME_INFRA`

    the internal name Rancher shall give to the `R_INFRA` stack, usually `state-local-%site%` where `%site%` is automatically substituted to the name of the `site` the stack runs on

-   `STACK_NAME_USER`

    the internal name Rancher shall give to the `R_USER` stack, usually `state-local-%site%` where `%site%` is automatically substituted to the name of the `site` the stack runs on

-   `LOGSTASH_CONFIG_IMAGE`

    the configuration sidekick image to use for the Logstash service

-   `DASHBOARD_CONFIG_IMAGE`

    the configuration sidekick image to use for the Dashboard service

-   `DOCKER_COMPOSE_FILE_ADMIN`

    path to the `docker-compose.yml` file defining the services for the `ADMIN` stack

-   `DOCKER_COMPOSE_FILE_GLOBAL`

    path to the `docker-compose.yml` file defining the services for the `GLOBAL` stack

-   `DOCKER_COMPOSE_FILE_INFRA`

    path to the `docker-compose.yml` file defining the services for the `R_INFRA` stack

-   `DOCKER_COMPOSE_FILE_USER`

    path to the `docker-compose.yml` file defining the services for the `R_USER` stack

-   `RANCHER_COMPOSE_FILE_ADMIN`

    path to the `rancher-compose.yml` file defining Rancher specifica for the `ADMIN` stack

-   `RANCHER_COMPOSE_FILE_GLOBAL`

    path to the `rancher-compose.yml` file defining Rancher specifica for the `GLOBAL` stack

-   `RANCHER_COMPOSE_FILE_INFRA`

    path to the `rancher-compose.yml` file defining Rancher specifica for the `R_INFRA` stack

-   `RANCHER_COMPOSE_FILE_ADMIN`

    path to the `rancher-compose.yml` file defining Rancher specifica for the `R_USER` stack

-   `OS_AUTH_URL`

    the URL to the OpenStack authentication service, usually an HTTP URL to port 5000

-   `OS_PROJECT_ID`

    the internal OpenStack project ID under which VMs are managed, usually a 32-char hexadecimal string

-   `OS_PROJECT_NAME`

    the OpenStack project name under which VMs are managed

-   `OS_USER_DOMAIN`

    the OpenStack users' domain which logically groups projects and other resources, usually `Default`

-   `OS_USERNAME`

    the OpenStack username to use for authentication

-   `OS_PASSWORD`

    the OpenStack password to use for authentication

-   `OS_REGION_NAME`

    the OpenStack region name to manage VMs within

-   `OS_IDENTITY_API_VERSION`

    the version of the OpenStack identity API to use, usually `3`

  [Ranchers' GitHub repository]: https://github.com/rancher/rancher-compose/releases
  [Windows Subsystem for Linux]: https://docs.microsoft.com/en-us/windows/wsl/install-win10
  [Cygwin]: http://www.cygwin.com
  [Access Control in Rancher]: https://rancher.com/docs/rancher/v1.6/en/configuration/access-control/#local-authentication
  [Registries in Rancher]: https://rancher.com/docs/rancher/v1.6/en/environments/registries/
  [.properties file format]: https://en.wikipedia.org/wiki/.properties
  [`.env.example`]: https://omi-gitlab.e-technik.uni-ulm.de/students/hiwi/recap-cli/blob/master/src/.env.example
