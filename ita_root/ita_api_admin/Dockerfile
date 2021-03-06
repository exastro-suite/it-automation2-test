#   Copyright 2022 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
FROM    registry.access.redhat.com/ubi8/ubi-init as common_build

ARG USERNAME=app_user
ARG GROUPNAME=app_user

ARG APP_PATH=/exastro

RUN dnf install -y \
    gcc \
    httpd \
    httpd-devel \
    python39 \
    python39-devel \
    python39-mod_wsgi \
    langpacks-en \
    wget \
    unzip \
&&  pip3.9 install --upgrade pip setuptools \
&&  pip3.9 install \
    Flask \
    connexion \
    six \
    requests \
    pyyaml \
    pytz \
    markdown \
    pymysql \
    python-dotenv \
&&  pip3.9 install \
    connexion[swagger-ui] \
&&  groupadd $GROUPNAME \
&&  useradd -m -s /bin/bash -g $GROUPNAME $USERNAME

#
# Build for development
#   Specify options when creating this image: --target develop_build
#
FROM    common_build as develop_build

RUN dnf install -y \
    sudo \
    git \
    vim \
    diffutils \
    bind-utils \
    iputils \
&&  pip3.9 install \
    debugpy \
    flake8 \
    autopep8 \
&&  usermod -G wheel $USERNAME \
&&  echo '%wheel ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

USER $USERNAME

RUN mkdir ~/.config

WORKDIR $APP_PATH

COPY ./ita_root/ita_api_admin/config/httpd.conf/httpd.conf /etc/httpd/conf/httpd.conf
COPY ./ita_root/ita_api_admin/config/httpd.conf/wsgi.conf /etc/httpd/conf.d/wsgi.conf

COPY ./ita_root/ita_api_admin/ $APP_PATH/
COPY ./ita_root/common_libs/ $APP_PATH/common_libs/
COPY ./ita_root/messages/ $APP_PATH/messages/

CMD ["sudo","-E","httpd","-D","FOREGROUND"]

#
# Build for production
#
FROM    common_build

USER $USERNAME
WORKDIR $APP_PATH

COPY ./ita_root/ita_api_admin/httpd.conf/httpd.conf /etc/httpd/conf/httpd.conf
COPY ./ita_root/ita_api_admin/httpd.conf/wsgi.conf /etc/httpd/conf.d/wsgi.conf

COPY ./ita_root/ita_api_admin/ $APP_PATH/
COPY ./ita_root/common_libs/ $APP_PATH/common_libs/
COPY ./ita_root/messages/ $APP_PATH/messages/

CMD ["httpd","-D","FOREGROUND"]

RUN mkdir /storage
