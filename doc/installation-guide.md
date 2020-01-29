---
title: |
  RECAP Installation Guide
author: |
  Benjamin Schanzel (benjamin.schanzel@uni-ulm.de) \
  Institute of Information Resource Management, Ulm University
---

Introduction and Prerequisites
==============================

This guide guides you through a guided installation of a RECAP environment. **Guide!**

Following the steps outlined here, you will make use of the RECAP CLI module for a streamlined installation of the [Rancher Container Orchestration Platform] on a number of hosts and the deployment of RECAP services therein.

It is assumed you have at least 7 hosts available with each having *Python* and *Docker* installed on them and SSH access with public-key authentication (make sure you have the SSH private key for authentication at hand).

In this guide we will install a RECAP environment on 2 sites (i.e. 2 data centers). One of these sites will contain 4 hosts with infrastructure labels `r_infra`, `r_user`, `admin`, and `global` and be considered the master site. The other site, hierarchically located below, will contain 2 hosts with infrastructure labels `r_infra` and `r_user`, as depicted below. Together with a host running the Rancher Server, this totals to a number of 7 hosts (VMs or physical hosts) you must have at hand to complete this guide.

    SITE   HOST     ROLE

    Site 0
     |_host 0.0     (rancher-server)
     |_host 0.1     (admin)
     |_host 0.2     (global)
     |_host 0.3     (r_infra)
     |_host 0.4     (r_user)
     |
     |_ Site 1
         |_host 1.0 (r_infra)
         |_host 1.1 (r_user)

The following sections provide a step-by-step guide of how to [setup] your local RECAP CLI, [initialize a new RECAP environment], [add the hosts] to your environment, and finally [review] your new RECAP environment and the services running in it.

Setup Your Local CLI Module {#setup}
===========================

The RECAP CLI module is available as a Docker Container image and can be obtained from the image registry at `omi-registry.e-technik.uni-ulm.de`.

``` {.bash .numberLines}
docker pull \
  omi-registry.e-technik.uni-ulm.de/students/hiwi/recap-cli:latest
```

A `.env` configuration file is required for the CLI tool to run. As a starting point with sane default values, please obtain the exemplary configuration via

``` {.bash}
wget -O .env \
  https://omi-gitlab.e-technik.uni-ulm.de/students/hiwi/recap-cli/raw/master/src/cli/.env.example
```

and verify your installation of the CLI tool works by invoking the `help` command as shown below. It should present you the available commands without any error messages.

``` {.bash .numberLines}
docker run \
  -v $(realpath .env):/opt/app/cli/.env \
  omi-registry.e-technik.uni-ulm.de/students/hiwi/recap-cli:latest \
  help
```

A short description to each of the available commands and their arguments is available by running `help [command]`. Extensive documentation to the CLI tool can obtained online.

> TODO: add a link to the PDF

Initialize a New Environment {#install-master}
============================

Adding Hosts to the Environment {#install-agents}
===============================

Review the Installation {#review}
=======================

  [Rancher Container Orchestration Platform]: https://rancher.com/products/rancher/
  [setup]: #setup
  [initialize a new RECAP environment]: #install-master
  [add the hosts]: #install-agents
  [review]: #review
