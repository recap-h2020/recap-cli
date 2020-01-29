#!/bin/sh

VERSION=3.6.0.3600
PACKAGE=ActivePython-${VERSION}-linux-x86_64-glibc-2.3.6-401834

mkdir -p /opt/python
mkdir -p /opt/bin

cd /tmp
wget http://downloads.activestate.com/ActivePython/releases/${VERSION}/${PACKAGE}.tar.gz
tar -xzvf ${PACKAGE}.tar.gz
cd ${PACKAGE}
./install.sh -I /opt/python/

ln -sf /opt/python/bin/easy_install /opt/bin/easy_install
ln -sf /opt/python/bin/pip3 /opt/bin/pip
ln -sf /opt/python/bin/pip3 /opt/bin/pip3
ln -sf /opt/python/bin/python3 /opt/bin/python
ln -sf /opt/python/bin/python3 /opt/bin/python3
ln -sf /opt/python/bin/virtualenv /opt/bin/virtualenv

cd /tmp
rm -rf /tmp/${PACKAGE}
rm /tmp/${PACKAGE}.tar.gz
