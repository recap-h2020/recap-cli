FROM python:3.6-alpine3.8

# add build-time dependencies
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    linux-headers \
    openssl-dev \
    python3-dev \
    libffi-dev \
    git

# install python packages
WORKDIR /tmp
COPY requirements.txt /tmp/
RUN pip install -r requirements.txt && rm requirements.txt

# add run-time dependencies
RUN apk add --no-cache \
    openssh-client

RUN ansible-galaxy install \
    defunctzombie.coreos-bootstrap \
    hp41.coreos-docker-compose

ENV RANCHER_CLI_VERSION v0.6.13
ENV RANCHER_COMPOSE_VERSION v0.12.5

# install rancher-cli
WORKDIR /tmp
RUN wget https://github.com/rancher/cli/releases/download/${RANCHER_CLI_VERSION}/rancher-linux-amd64-${RANCHER_CLI_VERSION}.tar.gz \
    && tar xzf rancher-linux-amd64-${RANCHER_CLI_VERSION}.tar.gz \
    && mv rancher-${RANCHER_CLI_VERSION}/* /usr/bin/ \
    && rm rancher-linux-amd64-${RANCHER_CLI_VERSION}.tar.gz \
    && rm -rf rancher-${RANCHER_CLI_VERSION}

# install rancher-compose
RUN wget https://github.com/rancher/rancher-compose/releases/download/${RANCHER_COMPOSE_VERSION}/rancher-compose-linux-amd64-${RANCHER_COMPOSE_VERSION}.tar.gz \
    && tar xzf rancher-compose-linux-amd64-${RANCHER_COMPOSE_VERSION}.tar.gz \
    && mv rancher-compose-${RANCHER_COMPOSE_VERSION}/* /usr/bin/ \
    && rm rancher-compose-linux-amd64-${RANCHER_COMPOSE_VERSION}.tar.gz \ 
    && rm -rf rancher-compose-${RANCHER_COMPOSE_VERSION}

# cleanup build-time dependencies
RUN apk del .build-deps

# copy project files
COPY . /opt/app/

# fix file permissions on key files
RUN chmod 600 /opt/app/recap_virtualenv/keys/cloud_key.pem \
  && chmod 600 /opt/app/recap_virtualenv/keys/cloud_key.public

WORKDIR /opt/app
ENTRYPOINT ["sh", "entrypoint.sh"]
CMD ["--help"]
